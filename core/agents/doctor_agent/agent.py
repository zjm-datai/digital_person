"""
core/agents/doctor_agent/agent.py
"""

import re
import logging
import json
from typing import Any, Dict, List, Optional

from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
# langgraph-checkpoint-postgres
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, AIMessageChunk
)

from psycopg_pool import ConnectionPool

from core.agents.graph_agent_base import GraphAgent

from .state import (
    FIELD_SPECS, 
    STAGES, 
    STAGE_CN, 
    REVISIT_STAGES, 
    DoctorAgentState
)

from .prompt import (
    QUESTION_SYSTEM_PROMPT, 
    SUMMARY_SYSTEM_PROMPT, 
    FILL_FIELDS_PROMPT, 
    REVISIT_PREFILL_PROMPT, 
    QUESTION_PROMPT, 
    REVISIT_SUMMARY_SYSTEM_PROMPT, 
    REVISIT_QUESTION_PROMPT, 
    REVISIT_QUESTION_SYSTEM_PROMPT,
    SUMMARY_SYSTEM_PROMPT_MAN,
    REVISIT_SUMMARY_SYSTEM_PROMPT_MAN
)

logger = logging.getLogger(__name__)


class DoctorAgent(GraphAgent):

    def __init__(
        self,
        connection_pool: ConnectionPool | None = None
    ):
        super().__init__(connection_pool=connection_pool)

    def create_graph(self) -> CompiledStateGraph:
        if self._graph is not None:
            return self._graph
        
        graph = StateGraph(DoctorAgentState)

        graph.add_node("init", self._init)
        graph.add_node("process", self._process)
        graph.add_node("ask", self._ask)
        graph.add_node("summarize", self._summarize)

        graph.set_entry_point("init")
        graph.add_edge("init", "process")

        graph.add_conditional_edges(
            "process",
            lambda s: "summarize" if s.all_done else "ask",
            {
                "ask": "ask",
                "summarize": "summarize",
            },
        )

        graph.add_edge("ask", END)
        graph.add_edge("summarize", END)

        connection_pool = self._get_connection_pool()       

        if connection_pool:
            checkpointer = PostgresSaver(connection_pool)
            checkpointer.setup()
        else:
            checkpointer = None
            logger.info(f"checkpoint 初始化失败，将使用无状态模式运行")

        self._graph = graph.compile(
            checkpointer=checkpointer,
            name="DoctorAgent"
        )

        return self._graph
    
    def _init(
        self,
        state: DoctorAgentState,
    ) -> DoctorAgentState:
        
        if state.initial_context is None and state.messages:
            logger.info("开始初始化")
            bingli = state.messages[-1]

        if isinstance(bingli, HumanMessage):
            try:
                state.initial_context = json.loads(bingli.content)
            except json.JSONDecodeError:
                pass

        # 识别是否为复诊
        is_revisit = False

        if state.initial_context and isinstance(state.initial_context, dict):
            revisitInfo = state.initial_context.get("revisitInfo", {})
            is_revisit = bool(revisitInfo.get("isRevisit", 0) == 1)
        state.is_revisit = is_revisit

        if state.initial_context is None:
            state.initial_context = {}

        if not state.record_initialized:
            if state.is_revisit:
                self._prefill_revisit_from_context(state)
                state.current_stage = "revisit"
            else:
                self._prefill_from_context(
                    state.initial_context or [],
                    state.history_fileds,
                    state.personal_fileds
                )
                state.current_stage = STAGES[0]

        # 初始化：从当前阶段起，推进到第一个仍有缺失的阶段，并锁定该阶段第一个缺失字段
        self._advance_until_stage_with_missing(state)

        state.missing_fields = self._get_missing(state)
        state.known_fields = self._get_known_list(state)

        logger.info(
            "初始化后 all_done=%s, current_stage=%s, current_missing_field=%s",
            state.all_done, state.current_stage, state.current_missing_field
        )

        return state


    def _process(self, state: DoctorAgentState) -> DoctorAgentState:
        """主处理节点：根据上一轮对话抽取信息、推进阶段。"""

        logger.info(
            "Process node: dialogue_count=%s, stage=%s, is_revisit=%s",
            state.dialogue_count,
            state.current_stage,
            state.is_revisit,
        )

        # 必须已经有过至少一次问答才处理抽取逻辑
        if state.dialogue_count >= 1:
            # 复诊：固定顺序逐项问
            if state.is_revisit and state.current_stage == "revisit":
                if state.messages and isinstance(state.messages[-1], HumanMessage):
                    state.chat_history.append(state.messages[-1])

                # 最近一轮问答（AI + Human）用于抽取
                last_two = []
                if state.chat_history:
                    if isinstance(state.chat_history[-1], HumanMessage):
                        last_two.append(state.chat_history[-1])
                    if len(state.chat_history) >= 2 and isinstance(state.chat_history[-2], AIMessage):
                        last_two.insert(0, state.chat_history[-2])

                fills = self._extract_from_recent_chat(state, recent_msgs=last_two)
                if fills:
                    table = {row["field_name_eg"]: row for row in state.revisit_fields}
                    for k, v in fills.items():
                        if k in table and table[k].get("field_content") is None:
                            table[k]["field_content"] = v

                # 选择下一个复诊字段
                nxt = self._next_revisit_field(state)
                if nxt is None:
                    state.all_done = True
                    logger.info("Revisit: all fields asked, all_done=True")
                else:
                    state.current_missing_field = nxt

                state.dialogue_count += 1
                return state

            # 初诊：原有逻辑
            # 收集历史
            state.chat_history.append(state.messages[-1])
            state.stage_rounds += 1

            # 先刷新缺失/已知
            state.missing_fields = self._get_missing(state)
            state.known_fields = self._get_known_list(state)

            # 当前字段为空或已填，重新选择
            if not state.current_missing_field or state.current_missing_field not in state.missing_fields:
                state.current_missing_field = self._next_missing_field_in_stage(state)

            state.last_asked_stage = state.current_stage
            state.last_asked_field = state.current_missing_field

            # 最近一轮问答用于抽取
            last_two = []
            if state.chat_history:
                if isinstance(state.chat_history[-1], HumanMessage):
                    last_two.append(state.chat_history[-1])
                if len(state.chat_history) >= 2 and isinstance(state.chat_history[-2], AIMessage):
                    last_two.insert(0, state.chat_history[-2])

            fills = self._extract_from_recent_chat(state, recent_msgs=last_two)
            if fills:
                tbl = self._get_table(state)
                row_map = {row["field_name_eg"]: row for row in tbl}
                for k, v in fills.items():
                    if k in row_map and row_map[k].get("field_content") is None:
                        row_map[k]["field_content"] = v

            # 写回后刷新
            state.missing_fields = self._get_missing(state)
            state.known_fields = self._get_known_list(state)

            # 若当前阶段填满，推进到下一个仍有缺失的阶段
            if not state.missing_fields:
                stages = self._stage_order(state)
                current_idx = stages.index(state.current_stage) if state.current_stage in stages else -1
                if current_idx + 1 < len(stages):
                    state.current_stage = stages[current_idx + 1]
                    logger.info("Stage fully filled, move to next: %s", state.current_stage)

                self._advance_until_stage_with_missing(state)
                state.missing_fields = self._get_missing(state)
                state.known_fields = self._get_known_list(state)
            else:
                # 仍在本阶段：找下一个缺失字段
                state.current_missing_field = self._next_missing_field_in_stage(state)

            if self._is_all_filled(state):
                state.all_done = True
                logger.info("All fields filled, all_done=True")
                return state

        state.dialogue_count += 1
        return state

    def _ask(self, state: DoctorAgentState) -> DoctorAgentState:
        """问诊节点：生成下一句提问。"""

        # ---------- 复诊：固定顺序问 + 复诊提示词 ----------
        if state.is_revisit and state.current_stage == "revisit":
            if state.all_done or state.current_missing_field is None:
                return state

            tbl = state.revisit_fields
            name_map = {r["field_name_eg"]: r["field_name_cn"] for r in tbl}
            value_map = {r["field_name_eg"]: r.get("field_content") for r in tbl}

            target_field_eg = state.current_missing_field
            target_field_cn = name_map.get(target_field_eg, target_field_eg)
            prefilled_text = value_map.get(target_field_eg)
            prefilled_text = "（无）" if prefilled_text in (None, "", []) else str(prefilled_text)

            system_msg = SystemMessage(
                content=REVISIT_QUESTION_SYSTEM_PROMPT.format(
                    target_field_cn=target_field_cn,
                )
            )
            question_prompt = HumanMessage(
                content=REVISIT_QUESTION_PROMPT.format(
                    target_field_cn=target_field_cn,
                    prefilled_text=prefilled_text,
                )
            )

            msgs = (
                [system_msg] + state.chat_history + [question_prompt]
                if state.chat_history
                else [system_msg, question_prompt]
            )
            resp = self.llm.invoke(msgs)
            question = resp.content.strip()
            state.chat_history.append(AIMessage(content=question))

            # 标记该字段“已问过”
            state.revisit_asked_fields.add(target_field_eg)
            state.last_asked_stage = "revisit"
            state.last_asked_field = target_field_eg

            logger.info("Revisit ask: field=%s", target_field_eg)
            return state

        # ---------- 初诊 ----------
        if state.all_done or state.current_missing_field is None or state.current_stage not in self._stage_order(state):
            return state

        tbl = self._get_table(state)
        stage = state.current_stage
        stage_cn = STAGE_CN.get(stage, stage)

        name_map = {r["field_name_eg"]: r["field_name_cn"] for r in tbl}

        target_field_eg = state.current_missing_field
        target_field_cn = name_map.get(
            target_field_eg,
            FIELD_SPECS.get(target_field_eg, {}).get("cn", target_field_eg),
        )

        known_list_cn = [
            name_map[eg]
            for eg in (self._get_known_list(state) or [])
            if eg in name_map
        ]

        system_msg = SystemMessage(
            content=QUESTION_SYSTEM_PROMPT.format(
                known_list_cn=known_list_cn,
                stage_cn=stage_cn,
                target_field_cn=target_field_cn,
            )
        )
        question_prompt = HumanMessage(
            content=QUESTION_PROMPT.format(target_field_cn=target_field_cn)
        )

        msgs = (
            [system_msg] + state.chat_history + [question_prompt]
            if state.chat_history
            else [system_msg, question_prompt]
        )
        resp = self.llm.invoke(msgs)
        question = resp.content.strip()
        state.chat_history.append(AIMessage(content=question))

        logger.info("First-visit ask: stage=%s, field=%s", stage, target_field_eg)
        return state

    def _summarize(self, state: DoctorAgentState) -> DoctorAgentState:
        """总结节点：根据填好的字段生成总结。"""

        # ---------- 复诊 ----------
        if state.is_revisit:
            gender = None
            try:
                ctx = state.initial_context or {}
                gender = (
                    ctx.get("latestMedicalRecord", {})
                    .get("basicInfo", {})
                    .get("gender")
                )
            except Exception:
                pass

            if gender == "男":
                summary_tmpl = REVISIT_SUMMARY_SYSTEM_PROMPT_MAN
            else:
                summary_tmpl = REVISIT_SUMMARY_SYSTEM_PROMPT

            last_record = {}
            try:
                last_record = ((ctx.get("revisitInfo") or {}).get("lastRecord") or {})
            except Exception:
                last_record = {}

            payload = {
                "revisit_fields": state.revisit_fields,
                "previous_record": last_record,
                "_notes": {
                    "scene": "revisit",
                    "gender": gender or "未知",
                    "bowel_urine_field": "revisit_bowel_and_urine",
                    "missing_repr": "无记录",
                },
            }

            sys = SystemMessage(content=summary_tmpl)
            ctx_msg = SystemMessage(content=json.dumps(payload, ensure_ascii=False))
            msg = self.llm.invoke([sys, ctx_msg])
            state.chat_history.append(AIMessage(content=msg.content))

            logger.info("Revisit summary generated.")
            return state

        # ---------- 初诊 ----------
        sys = SystemMessage(content=summary_prompt)
        ctx_payload = {
            "condition_fields": state.condition_fields,
            "history_fields": state.history_fields,
            "personal_fields": state.personal_fields,
        }
        ctx = SystemMessage(content=json.dumps(ctx_payload, ensure_ascii=False))
        msg = self.llm.invoke([ctx, sys])
        state.chat_history.append(AIMessage(content=msg.content))

        logger.info("First-visit summary generated.")
        return state

    # ----------------- 预填充逻辑 -----------------

    def _prefill_from_context(
        self,
        ctx: Dict,
        history_fields: List[Dict],
        personal_fields: List[Dict],
    ):
        """初诊：从完整病历对象中预填既往史/个人史。"""
        if "patientIdentity" not in ctx:
            return

        rec = ctx
        basic = rec["latestMedicalRecord"]["basicInfo"]
        past = rec["latestMedicalRecord"]["pastHistory"]
        mci = rec["latestMedicalRecord"]["marriageChildInfo"] or {}
        revisit = rec.get("revisitInfo", {})
        is_rev = revisit.get("isRevisit", 0)
        last_rec = revisit.get("lastRecord", {})
        pi_text = last_rec.get("presentIllness", "") if is_rev == 1 else ""

        # ---------- 1. 既往史 ----------
        for f in history_fields:
            k = f["field_name_eg"]
            if k == "allergy_present":
                f["field_content"] = past.get("allergyHistory", "") not in (None, "", "无")
            elif k == "allergy_foodordrug_name":
                f["field_content"] = past.get("allergyHistory")
            elif k in ("long_term_medication_present", "long_term_medication_name"):
                f["field_content"] = None

        # ---------- 2. 性别相关 ----------
        female_only = {
            "menstrual_cycle",
            "menstrual_duration",
            "last_menstrual_period",
            "menstrual_flow",
            "menstrual_color",
            "menstrual_quality",
            "full_term_birth_count",
            "preterm_birth_count",
            "miscarriage_count",
        }

        global summary_prompt
        if basic.get("gender") == "男":
            summary_prompt = SUMMARY_SYSTEM_PROMPT_MAN
            for f in personal_fields:
                if f["field_name_eg"] in female_only:
                    f["field_content"] = "不适用"
        else:
            summary_prompt = SUMMARY_SYSTEM_PROMPT

        def ext(pat: str) -> Optional[str]:
            m = re.search(pat, pi_text)
            return m.group(1).strip() if m else None

        # 3. 个人史
        for f in personal_fields:
            k = f["field_name_eg"]

            if k == "personal_bad_habits":
                f["field_content"] = past.get("personalHistory")

            elif k == "personal_smoking_frequency":
                ph = past.get("personalHistory", "") or ""
                freq = self._infer_smoke_drink_frequency(ph)["smoke"]
                f["field_content"] = freq

            elif k == "personal_drinking_frequency":
                ph = past.get("personalHistory", "") or ""
                freq = self._infer_smoke_drink_frequency(ph)["drink"]
                f["field_content"] = freq

            elif k == "dietary_status":
                f["field_content"] = ext(r"偏好([^，,；;]+)食物")

            elif k == "sleep_status":
                f["field_content"] = ext(r"(夜间睡眠[^，,；;]+)")

            elif k == "bowel_movement":
                f["field_content"] = ext(r"(大便[^，,；;]+)")

            elif k == "urine_status":
                f["field_content"] = ext(r"(小便[^，,；;]+)")

            elif k == "marital_reproductive_history":
                marriage_status = mci.get("marriageStatus", "")
                f["field_content"] = marriage_status or None

            elif k == "full_term_birth_count":
                if f.get("field_content") is None:
                    f["field_content"] = mci.get("fullTermCount")

            elif k == "preterm_birth_count":
                if f.get("field_content") is None:
                    f["field_content"] = mci.get("prematureCount")

            elif k == "miscarriage_count":
                if f.get("field_content") is None:
                    f["field_content"] = mci.get("abortionCount")

            elif k in ("living_children_count", "children_count"):
                f["field_content"] = mci.get("livingChildrenCount")

            # 月经相关：初始化不预填，后续问诊再填
            elif k in {
                "menstrual_cycle",
                "menstrual_duration",
                "last_menstrual_period",
                "menstrual_flow",
                "menstrual_color",
                "menstrual_quality",
            }:
                pass  # 留给后续问诊

    def _prefill_revisit_from_context(self, state: DoctorAgentState) -> None:
        """复诊：从上次病历中预填主要症状、大小便等。"""
        ctx = state.initial_context or {}
        revisit = (ctx.get("revisitInfo") or {})
        last_rec = revisit.get("lastRecord") or {}

        # 主要症状
        main_symptom = None
        cc = (last_rec.get("chiefComplaint") or "").strip()
        if cc:
            m = re.search(r"([^\d\W]{1,8})", cc)
            if m:
                main_symptom = m.group(1)
        if not main_symptom:
            pi = (last_rec.get("presentIllness") or "").strip()
            m2 = re.search(r"(腹痛|瘙痒|红斑|丘疹|脱屑|水肿|疼痛|灼热|刺痛|渗出|结痂)", pi)
            if m2:
                main_symptom = m2.group(1)

        if main_symptom:
            for r in state.revisit_fields:
                if r["field_name_eg"] == "revisit_main_symptom" and r.get("field_content") is None:
                    r["field_content"] = main_symptom
                    break

        # presentIllness 中的大小便信息
        pi_text = (last_rec.get("presentIllness") or "") or ""

        def _grab_segment(text: str, head: str) -> Optional[str]:
            pat = rf"{head}[^。\.；;，,]*"
            m = re.search(pat, text)
            return m.group(0).strip() if m else None

        bowel_seg = _grab_segment(pi_text, "大便")
        urine_seg = _grab_segment(pi_text, "小便")
        if bowel_seg or urine_seg:
            combo = "；".join(
                s
                for s in [bowel_seg if bowel_seg else None, urine_seg if urine_seg else None]
                if s
            )
            table = {row["field_name_eg"]: row for row in state.revisit_fields}
            if "revisit_bowel_and_urine" in table and not table["revisit_bowel_and_urine"].get(
                "field_content"
            ):
                table["revisit_bowel_and_urine"]["field_content"] = combo

        # LLM 预填充
        source_text_parts = []
        for key in ("presentIllness", "tcmFourExams", "physicalExam", "auxiliaryExam", "treatmentAdvice"):
            val = last_rec.get(key)
            if isinstance(val, dict):
                source_text_parts.extend([str(v) for v in val.values() if v])
            elif val:
                source_text_parts.append(str(val))
        source_text = "\n".join([cc] + source_text_parts).strip()

        if not source_text:
            return

        prompt = REVISIT_PREFILL_PROMPT.format(source_text=source_text)
        try:
            resp = self.llm.invoke([SystemMessage(content=prompt)])
            m = re.search(r"\{.*\}", resp.content, re.DOTALL)
            if not m:
                return
            data = json.loads(m.group())

            allowed = {
                "revisit_associated_symptoms",
                "revisit_diet",
                "revisit_sleep",
                "revisit_bowel_and_urine",
                "revisit_bowel",
                "revisit_urine",
                "revisit_other_hpi",
            }
            table = {row["field_name_eg"]: row for row in state.revisit_fields}

            for k, v in data.items():
                if (
                    k in allowed
                    and k in table
                    and table[k].get("field_content") is None
                    and v is not None
                ):
                    table[k]["field_content"] = v

            # 如果 LLM 返回分离的大便/小便字段，合并到合并字段
            if "revisit_bowel_and_urine" in table and not table["revisit_bowel_and_urine"].get(
                "field_content"
            ):
                bowel = data.get("revisit_bowel")
                urine = data.get("revisit_urine")
                if bowel or urine:
                    combo = "；".join(
                        s for s in [bowel if bowel else None, urine if urine else None] if s
                    )
                    if combo:
                        table["revisit_bowel_and_urine"]["field_content"] = combo
        except Exception as e:
            logger.warning("复诊预填充 LLM 解析失败：%s", e)

    # ----------------- 阶段与表工具 -----------------

    def _stage_order(self, state: DoctorAgentState) -> List[str]:
        return REVISIT_STAGES if state.is_revisit else STAGES

    def _all_tables(self, state: DoctorAgentState):
        if state.is_revisit:
            return state.revisit_fields
        return state.condition_fields + state.history_fields + state.personal_fields

    def _count_all_missing(self, state: DoctorAgentState) -> int:
        return sum(1 for r in self._all_tables(state) if r.get("field_content") is None)

    def _progress_counts(self, state: DoctorAgentState) -> dict:
        if state.is_revisit:
            total = len(state.revisit_fields)
            completed = len(state.revisit_asked_fields)
            completed = min(max(0, completed), total)
            return {"completed": completed, "total": total}

        total = state.start_missing_total or 0
        remaining = self._count_all_missing(state)
        completed = max(0, total - remaining)
        return {"completed": completed, "total": total}

    def _get_table(self, state: DoctorAgentState) -> List[Dict]:
        if not state.current_stage:
            return []
        if state.current_stage == "revisit":
            return state.revisit_fields
        return {
            "condition": state.condition_fields,
            "history": state.history_fields,
            "personal": state.personal_fields,
        }[state.current_stage]

    def _get_missing(self, state: DoctorAgentState) -> List[str]:
        if not state.current_stage:
            return []
        tbl = self._get_table(state)
        return [r["field_name_eg"] for r in tbl if r.get("field_content") is None]

    def _get_known_list(self, state: DoctorAgentState) -> List[str]:
        if not state.current_stage:
            return []
        tbl = self._get_table(state)
        return [r["field_name_eg"] for r in tbl if r.get("field_content") is not None]

    def _next_missing_field_in_stage(self, state: DoctorAgentState) -> Optional[str]:
        table = self._get_table(state)
        for r in table:
            if r.get("field_content") is None:
                return r["field_name_eg"]
        return None

    def _next_revisit_field(self, state: DoctorAgentState) -> Optional[str]:
        for row in state.revisit_fields:
            eg = row["field_name_eg"]
            if eg not in state.revisit_asked_fields:
                return eg
        return None

    def _is_all_filled(self, state: DoctorAgentState) -> bool:
        if state.is_revisit:
            all_rows = state.revisit_fields
        else:
            all_rows = state.condition_fields + state.history_fields + state.personal_fields
        return all(r.get("field_content") is not None for r in all_rows)

    def _stage_has_missing(self, state: DoctorAgentState, stage_key: str) -> bool:
        if stage_key == "revisit":
            table = state.revisit_fields
        else:
            table = {
                "condition": state.condition_fields,
                "history": state.history_fields,
                "personal": state.personal_fields,
            }[stage_key]
        return any(r.get("field_content") is None for r in table)

    def _advance_until_stage_with_missing(self, state: DoctorAgentState) -> None:
        stages = self._stage_order(state)
        if not stages:
            state.current_missing_field = None
            state.all_done = True
            return

        # 复诊特化
        if state.is_revisit and "revisit" in stages:
            state.current_stage = "revisit"
            nxt = self._next_revisit_field(state)
            if nxt is None:
                state.current_missing_field = None
                state.all_done = True
            else:
                state.current_missing_field = nxt
                state.all_done = False
            return

        # 初诊
        if state.current_stage not in stages:
            state.current_stage = stages[0]

        start_idx = stages.index(state.current_stage)
        for idx in range(start_idx, len(stages)):
            stage_key = stages[idx]
            if self._stage_has_missing(state, stage_key):
                state.current_stage = stage_key
                state.current_missing_field = self._next_missing_field_in_stage(state)
                state.all_done = False
                return

        state.current_missing_field = None
        state.all_done = True

    # ----------------- 文本解析工具 -----------------

    def _infer_smoke_drink_frequency(self, text: str) -> Dict[str, Optional[str]]:
        if not text:
            return {"smoke": None, "drink": None}

        t = str(text).replace(" ", "").lower()

        NEVER_PATTERNS_SMOKE = [
            r"不[吸抽]烟",
            r"无[吸抽]烟",
            r"无烟",
            r"从不[吸抽]烟",
            r"无烟酒史",
            r"无吸烟饮酒史",
            r"无烟酒",
        ]
        NEVER_PATTERNS_DRINK = [
            r"不(喝|饮)酒",
            r"无(饮|喝)酒",
            r"从不(喝|饮)酒",
            r"无酒精摄入",
            r"无酒史",
            r"无烟酒史",
            r"无吸烟饮酒史",
            r"无烟酒",
        ]
        OCCASIONAL_PATTERNS = [r"偶尔", r"偶而"]
        SOMETIMES_PATTERNS = [r"有时", r"有时候", r"时有"]
        OFTEN_PATTERNS = [r"经常", r"常常", r"时常", r"较常"]
        DAILY_PATTERNS = [r"每天", r"日常.*(吸烟|抽烟|饮酒|喝酒)", r"日均.*(支|杯|瓶|两|盎司)"]

        def match_any(pats, s):
            return any(re.search(p, s) for p in pats)

        def level_from_text(s: str, is_smoke: bool) -> Optional[str]:
            if match_any(NEVER_PATTERNS_SMOKE if is_smoke else NEVER_PATTERNS_DRINK, s):
                return "从不"
            if match_any(DAILY_PATTERNS, s):
                return "每天"
            if match_any(OFTEN_PATTERNS, s):
                return "经常"
            if match_any(SOMETIMES_PATTERNS, s):
                return "有时"
            if match_any(OCCASIONAL_PATTERNS, s):
                return "偶尔"
            return None

        smoke = level_from_text(t, True)
        drink = level_from_text(t, False)

        if smoke is None and match_any(NEVER_PATTERNS_SMOKE, t):
            smoke = "从不"
        if drink is None and match_any(NEVER_PATTERNS_DRINK, t):
            drink = "从不"

        if ("无吸烟饮酒史" in t or "无烟酒史" in t or "无烟酒" in t) and (smoke is None or drink is None):
            smoke = smoke or "从不"
            drink = drink or "从不"

        return {"smoke": smoke, "drink": drink}

    def _extract_from_recent_chat(self, state: DoctorAgentState, recent_msgs: List) -> Dict[str, Any]:
        """从最近一轮对话中抽取字段值。"""

        # ---------- 复诊：直接使用用户回答 ----------
        if state.is_revisit and state.current_stage == "revisit":
            last_human = None
            for m in reversed(recent_msgs):
                if isinstance(m, HumanMessage):
                    last_human = m.content.strip()
                    break

            if not last_human:
                return {}

            target_field = state.current_missing_field
            if not target_field:
                return {}

            efficacy_fields = {
                "revisit_eval_erythema",
                "revisit_eval_edema_papules",
                "revisit_eval_scale",
                "revisit_eval_lichenification",
                "revisit_other_discomfort",
            }

            # 疗效字段 or 普通字段：一律直接填用户回答
            return {target_field: last_human}

        # ---------- 初诊：LLM 抽取 ----------
        if not state.current_stage:
            return {}

        tbl = self._get_table(state)
        tbl_missing_rows = [row for row in tbl if row.get("field_content") is None]
        if not tbl_missing_rows:
            return {}

        specs = []
        for row in tbl_missing_rows:
            eg = row["field_name_eg"]
            spec = FIELD_SPECS.get(eg, {})
            specs.append(
                {
                    "field_eg": eg,
                    "field_cn": row["field_name_cn"],
                    "type": spec.get("type"),
                    "required": spec.get("required", False),
                    **({"enums": spec.get("enums")} if "enums" in spec else {}),
                    **({"scale": spec.get("scale")} if "scale" in spec else {}),
                }
            )

        chat_log = "\n".join(
            f"[{'患者' if isinstance(m, HumanMessage) else '医生'}] {m.content}"
            for m in recent_msgs
        ) or "(无对话)"

        prompt = FILL_FIELDS_PROMPT.format(
            stage_cn=STAGE_CN[state.current_stage],
            field_cns="、".join(r["field_cn"] for r in specs),
            specs=json.dumps(specs, ensure_ascii=False, indent=2),
            chat_log=chat_log,
        )

        resp = self.llm.invoke([SystemMessage(content=prompt)])
        m = re.search(r"\{.*\}", resp.content, re.DOTALL)
        if not m:
            return {}
        try:
            result = json.loads(m.group())
            allowed = {row["field_name_eg"] for row in tbl_missing_rows}
            result = {k: v for k, v in result.items() if k in allowed and v is not None}
            return result
        except json.JSONDecodeError:
            return {}

    # 对外同步接口（适配 Flask）
    def get_response(
        self,
        messages: List[Message],
        session_id: str,
    ) -> List[Dict]:
        """
        同步版本：一次性返回问句或总结。
        Flask 中可以直接：
            agent = DigitalPerson()
            resp = agent.get_response(messages, session_id)
        """
        if self._graph is None:
            self.create_graph()

        cfg = {"configurable": {"thread_id": session_id}}
        try:
            result = self._graph.invoke(
                {"messages": _dump_messages(messages), "session_id": session_id},
                cfg,
            )
            return _get_openai_style(result["messages"])
        except Exception as e:
            logger.error("get_response error: %s", e)
            raise

    def get_stream_response(
        self,
        messages: List[Message],
        session_id: str,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        同步流式版本：生成器返回事件，可在 Flask 中 streaming 发送。
        """
        if self._graph is None:
            self.create_graph()

        cfg = {"configurable": {"thread_id": session_id}}

        last_end_output: Optional[DoctorAgentState] = None
        is_summary = False

        try:
            for event in self._graph.stream_events(
                {"messages": _dump_messages(messages), "session_id": session_id},
                cfg,
                stream_mode="messages",
            ):
                if isinstance(event, dict):
                    if event.get("event") == "on_chain_stream":
                        chunk = event.get("data", {}).get("chunk")
                        if isinstance(chunk, tuple) and isinstance(chunk[0], AIMessageChunk):
                            node = chunk[1].get("langgraph_node")
                            content = chunk[0].content
                            if not content or not content.strip():
                                continue

                            if node == "ask":
                                yield {"event": "stream_output", "content": content}
                            elif node == "summarize":
                                is_summary = True
                                yield {"event": "summarize", "content": content}

                    elif event.get("event") == "on_chain_end":
                        output = event.get("data", {}).get("output")
                        if isinstance(output, DoctorAgentState):
                            last_end_output = output

            if last_end_output:
                progress = self._progress_counts(last_end_output)

                yield {
                    "event": "message_context",
                    "content": {
                        "assistant": {
                            "message_kind": "summary" if is_summary else "question",
                            "target_stage": last_end_output.current_stage,
                            "target_field": last_end_output.current_missing_field,
                            "progress": progress,
                        },
                        "user": {
                            "message_kind": "answer",
                            "target_stage": last_end_output.last_asked_stage,
                            "target_field": last_end_output.last_asked_field,
                        },
                    },
                }
                yield {"event": "is_end", "content": last_end_output.all_done}

        except Exception as e:
            logger.error("get_stream_response error: %s", e)
            raise