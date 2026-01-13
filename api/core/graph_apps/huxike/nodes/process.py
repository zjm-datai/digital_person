
import logging

from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage

from core.graph_apps.pifuke.prompt import FILL_FIELDS_PROMPT
from services.llm_service import LLMService

from .utils import get_table, is_all_filled, next_revisit_field, get_missing, get_known_list, next_missing_field_in_stage, stage_order, advance_until_stage_with_missing
from ..state import FIELD_SPECS, STAGE_CN, State

logger = logging.getLogger(__name__)

class ProcessNode:
    
    @staticmethod
    def run(
        state: State
    ):
        # 必须在传入病历之后（第 1 次 process 只是建立上下文，不处理抽取）
        if state.dialogue_count >= 1:
            # —— 复诊：不以缺失为准，固定顺序问 ——
            if state.is_revisit and state.current_stage == "revisit":
                # 把本轮用户最新消息也纳入 chat_history
                if state.messages and isinstance(state.messages[-1], HumanMessage):
                    state.chat_history.append(state.messages[-1])

                # 依然尝试从最近一轮对话抽取并回填
                last_two = []
                if state.chat_history:
                    if isinstance(state.chat_history[-1], HumanMessage):
                        last_two.append(state.chat_history[-1])
                    if len(state.chat_history) >= 2 and isinstance(state.chat_history[-2], AIMessage):
                        last_two.insert(0, state.chat_history[-2])

                fills = extract_from_recent_chat(state, recent_msgs=last_two)
                if fills:
                    logger.info(f"fills: {fills}")
                    table = {row["field_name_eg"]: row for row in state.revisit_fields}
                    for k, v in fills.items():
                        if k in table and table[k].get("new_change") is None:
                            table[k]["new_change"] = v

                # 下一问：无论是否已填过，都取尚未“问过”的下一个
                nxt = next_revisit_field(state)
                if nxt is None:
                    state.all_done = True
                else:
                    state.current_missing_field = nxt

                state.dialogue_count += 1
                return state

            # 初诊：保留原逻辑（以下为你原来的分支）
            # 收集历史（把最新一条消息加入 chat_history）
            state.chat_history.append(state.messages[-1])
            state.stage_rounds += 1

            # 先刷新缺失/已知（以当前阶段为视角）
            state.missing_fields = get_missing(state)
            state.known_fields = get_known_list(state)

            # 若当前字段未定或已被填充，则在本阶段重新选择第一个缺失字段
            if (state.current_missing_field is None) or (state.current_missing_field not in state.missing_fields):
                state.current_missing_field = next_missing_field_in_stage(state)

            state.last_asked_stage = state.current_stage
            state.last_asked_field = state.current_missing_field

            # 仅用最近一轮问答进行判断是否可以填充“当前阶段的缺失字段们”
            last_two = []
            if state.chat_history:
                # 最新 human
                if isinstance(state.chat_history[-1], HumanMessage):
                    last_two.append(state.chat_history[-1])
                # 上一个 AI
                if len(state.chat_history) >= 2 and isinstance(state.chat_history[-2], AIMessage):
                    last_two.insert(0, state.chat_history[-2])

            fills = extract_from_recent_chat(
                state, recent_msgs=last_two
            )

            if fills:
                # 将能填的“本阶段缺失字段”全部写回
                tbl = get_table(state)
                row_map = {row["field_name_eg"]: row for row in tbl}
                for k, v in fills.items():
                    if k in row_map and row_map[k].get("field_content") is None:
                        row_map[k]["field_content"] = v

            # 写回后刷新“当前阶段”的已知/缺失
            state.missing_fields = get_missing(state)
            state.known_fields = get_known_list(state)

            # 若当前阶段无缺失了，按顺序推进到下一个仍有缺失的阶段
            if not state.missing_fields:
                logger.info("当前阶段已填满，尝试推进到下一个仍有缺失的阶段")
                stages = stage_order(state)
                current_idx = stages.index(state.current_stage) if state.current_stage in stages else -1
                if current_idx + 1 < len(stages):
                    state.current_stage = stages[current_idx + 1]
                advance_until_stage_with_missing(state)
                state.missing_fields = get_missing(state)
                state.known_fields = get_known_list(state)
            else:
                # 仍在本阶段：选择本阶段的下一个缺失字段（按顺序）
                state.current_missing_field = next_missing_field_in_stage(state)

            # 如果全量填充完毕，标记结束
            if is_all_filled(state):
                state.all_done = True
                return state

        state.dialogue_count += 1
        return state

def extract_from_recent_chat(state, recent_msgs):
    # 复诊：直接使用最新 human 回答
    if state.is_revisit and state.current_stage == "revisit":
        last_human = None
        for m in reversed(recent_msgs):
            if isinstance(m, HumanMessage):
                last_human = m.content.strip()
                break
        if not last_human or not state.current_missing_field:
            return {}
        return {state.current_missing_field: last_human}

    # 初诊：调用 LLM 提取（保留原逻辑）
    if not state.current_stage:
        return {}

    tbl = get_table(state)
    tbl_missing_rows = [row for row in tbl if row.get("field_content") is None]
    if not tbl_missing_rows:
        return {}

    specs = []
    for row in tbl_missing_rows:
        eg = row["field_name_eg"]
        spec = FIELD_SPECS.get(eg, {})
        specs.append({
            "field_eg": eg,
            "field_cn": row["field_name_cn"],
            "type": spec.get("type"),
            "required": spec.get("required", False),
            **({"enums": spec.get("enums")} if "enums" in spec else {}),
            **({"scale": spec.get("scale")} if "scale" in spec else {})
        })

    chat_log = "\n".join(
        f"[{'患者' if isinstance(m, HumanMessage) else '医生'}] {m.content}"
        for m in recent_msgs
    ) or "(无对话)"

    result = LLMService.extract_fields_from_recent_chat(
        fill_fields_prompt_template=FILL_FIELDS_PROMPT,
        stage_cn=STAGE_CN[state.current_stage],
        specs=specs,
        chat_log=chat_log,
    )

    if not result:
        return {}

    allowed = {row["field_name_eg"] for row in tbl_missing_rows}
    result = {k: v for k, v in result.items() if k in allowed and v is not None}
    return result
