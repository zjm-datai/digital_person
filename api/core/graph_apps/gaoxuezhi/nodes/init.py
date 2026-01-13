import re
import json
import logging
from typing import Dict, Optional, List

from langchain_core.messages import HumanMessage

from services.llm_service import LLMService

from .utils import advance_until_stage_missing, get_known_list, get_missing
from ..prompt import REVISIT_PREFILL_PROMPT
from ..state import STAGES, State

logger = logging.getLogger(__name__)

class InitNode:
    
    @staticmethod
    def run(
        state: State
    ):
        if state.initial_context is None and state.messages:
            bingli = state.messages[-1]
            if isinstance(bingli, HumanMessage):
                try:
                    state.initial_context = json.loads(bingli.content)
                except json.JSONDecodeError:
                    raise
                
            is_revisit = False
            if state.initial_context and isinstance(state.initial_context, dict):
                revisit_info = state.initial_context.get("revisitInfo", {})
                is_revisit = bool(revisit_info.get("isRevisit", 0) == 1)
            state.is_revisit = is_revisit
            
            if state.initial_context is None:
                state.initial_context = {}
                
            if not state.record_initialized:
                if state.is_revisit:
                    _prefill_from_context(
                        initial_context=state.initial_context,
                        history_fields=state.history_fields,
                        personal_fields=state.personal_fields
                    )
                    _prefill_revisit_from_context(
                        initial_context=state.initial_context,
                        revisit_fields=state.revisit_fields
                    )
                    state.current_stage = "revisit"
                else:
                    _prefill_from_context(
                        initial_context=state.initial_context,
                        history_fields=state.history_fields,
                        personal_fields=state.personal_fields
                    )
                    state.current_stage = STAGES[0]

                state.record_initialized = True
            
            if state.dialogue_count == 0:
                advance_until_stage_missing(state)
            
            state.missing_fields = get_missing(state)
            state.known_fields = get_known_list(state)
            
            return state


def _prefill_from_context(
    initial_context: Dict, history_fields: List[Dict], personal_fields: List[Dict]
):
    # 定义女性专属字段集合 - 男性则填充【不适用】
    female_only_fields = {
        "menstrual_cycle", "menstrual_duration", "last_menstrual_period",
        "menstrual_flow", "menstrual_color", "menstrual_quality",
        "full_term_birth_count", "preterm_birth_count", "miscarriage_count"
    }

    if "patientIdentity" in initial_context:
        # 1. 解构病历上下文的核心数据节点
        basic_info = initial_context["latestMedicalRecord"]["basicInfo"]
        past_history = initial_context["latestMedicalRecord"]["pastHistory"]
        marriage_child_info = initial_context["latestMedicalRecord"]["marriageChildInfo"] or {}
        
        revisit = initial_context.get("revisitInfo", {})
        is_revisit = revisit.get("isRevisit", 0)
        
        last_record = revisit.get("lastRecord", {})
        present_illness = last_record.get("presentIllness", "") if is_revisit == 1 else ""

        # 2. 填充【既往史】字段 history_fields
        for field_item in history_fields:
            field_key = field_item.get("field_name_eg")
            if not field_key:
                continue
            
            if field_key == "allergy_present":
                # 过敏史：有内容则为True，无/空/无过敏则为False
                allergy_content = past_history.get("allergyHistory", "")
                field_item["field_content"] = allergy_content not in (None, "", "无")
            
            elif field_key == "allergy_foodordrug_name":
                # 过敏原名称：直接赋值过敏史原文
                field_item["field_content"] = past_history.get("allergyHistory")
            
            elif field_key == "long_term_medication_present":
                # 长期用药标识：暂未对接数据，赋值None
                field_item["field_content"] = None
            
            elif field_key == "long_term_medication_name":
                # 长期用药名称：暂未对接数据，赋值None
                field_item["field_content"] = None
            
            elif field_key == "family_history":
                # 家族史：含「否认」则为空，否则赋值原文
                fh_content = past_history.get("familyHistory", "")
                field_item["field_content"] = None if "否认" in fh_content else fh_content or None

        # 3. 性别判断 & 女性专属字段屏蔽逻辑
        patient_gender = basic_info.get("gender")
        if patient_gender == "男":
            for field_item in personal_fields:
                f_key = field_item.get("field_name_eg")
                if f_key in female_only_fields:
                    field_item["field_content"] = "不适用"

        # 4. 工具方法：从复诊现病史文本中正则抽取指定内容
        def extract_content(pattern: str):
            match = re.search(pattern, present_illness)
            return match.group(1).strip() if match else None

        # 5. 填充【个人史+婚育史+月经史】核心字段 personal_fields
        for field_item in personal_fields:
            field_key = field_item.get("field_name_eg")
            # 跳过已被赋值【不适用】的男性女性专属字段
            if field_item.get("field_content") == "不适用" or not field_key:
                continue

            if field_key == "personal_bad_habits":
                # 个人不良嗜好：直接赋值个人史原文
                field_item["field_content"] = past_history.get("personalHistory")

            elif field_key == "personal_smoking_frequency":
                # 吸烟频率：调用方法解析个人史文本
                ph_content = past_history.get("personalHistory", "") or ""
                smoke_freq = _infer_smoke_drink_frequency(ph_content)["smoke"]
                field_item["field_content"] = smoke_freq

            elif field_key == "personal_drinking_frequency":
                # 饮酒频率：调用方法解析个人史文本
                ph_content = past_history.get("personalHistory", "") or ""
                drink_freq = _infer_smoke_drink_frequency(ph_content)["drink"]
                field_item["field_content"] = drink_freq

            elif field_key == "dietary_status":
                # 饮食情况：正则抽取「偏好xxx食物」
                field_item["field_content"] = extract_content(r"偏好([^，,；;]+)食物")

            elif field_key == "sleep_status":
                # 睡眠情况：正则抽取「夜间睡眠xxx」
                field_item["field_content"] = extract_content(r"(夜间睡眠[^，,；;]+)")

            elif field_key == "bowel_movement":
                # 大便情况：正则抽取「大便xxx」
                field_item["field_content"] = extract_content(r"(大便[^，,；;]+)")

            elif field_key == "urine_status":
                # 小便情况：正则抽取「小便xxx」
                field_item["field_content"] = extract_content(r"(小便[^，,；;]+)")

            elif field_key == "marital_reproductive_history":
                # 婚育史：已婚/离异等赋值原文，未婚/空则为None
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                field_item["field_content"] = marriage_status if marriage_status and marriage_status != "未婚" else None

            # ===== 生育相关字段 =====
            elif field_key == "full_term_birth_count":
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                if marriage_status in ("", "未婚"):
                    field_item["field_content"] = None
                elif field_item.get("field_content") is None:
                    field_item["field_content"] = marriage_child_info.get("fullTermCount")

            elif field_key == "preterm_birth_count":
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                if marriage_status in ("", "未婚"):
                    field_item["field_content"] = None
                elif field_item.get("field_content") is None:
                    field_item["field_content"] = marriage_child_info.get("prematureCount")

            elif field_key == "miscarriage_count":
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                if marriage_status in ("", "未婚"):
                    field_item["field_content"] = None
                elif field_item.get("field_content") is None:
                    field_item["field_content"] = marriage_child_info.get("abortionCount")

            elif field_key == "living_children_count":
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                field_item["field_content"] = marriage_child_info.get("livingChildrenCount") if marriage_status not in ("", "未婚") else None

            elif field_key == "children_count":
                marriage_status = marriage_child_info.get("marriageStatus", "").strip()
                field_item["field_content"] = marriage_child_info.get("livingChildrenCount") if marriage_status not in ("", "未婚") else None

            # ===== 月经相关字段 =====
            elif field_key in {
                "menstrual_cycle", "menstrual_duration", "last_menstrual_period",
                "menstrual_flow", "menstrual_color", "menstrual_quality"
            }:
                pass


def _prefill_revisit_from_context(
    initial_context: Dict, 
    revisit_fields: List[Dict]
):
    revisit_info = initial_context.get("revisitInfo", {})
    last_record = revisit_info.get("lastRecord", {})
    
    # ========= 规则一：直接填充“主要症状” =========
    chief_complaint = (last_record.get("chiefComplaint") or "").strip()

    if chief_complaint:
        for r in revisit_fields:
            if (
                r.get("field_name_eg") == "revisit_main_symptom"
                and r.get("field_content") is None
            ):
                r["field_content"] = chief_complaint
                break
    
    # ========= 规则二：仅用 presentIllness 调 LLM 做结构化提取 =========
    present_illness = (last_record.get("presentIllness") or "").strip()
    if not present_illness:
        return

    try:
        # 注意：需确保 LLMService 和 REVISIT_PREFILL_PROMPT 已提前导入/定义
        data = LLMService.prefill_revisit_from_present_illness(
            revisit_prefill_prompt_template=REVISIT_PREFILL_PROMPT,
            present_illness=present_illness,
        )
        if not data:
            return

        logger.info(f"extract revisit data: {data}")

        allowed = {
            "revisit_diet",
            "revisit_sleep",
            "revisit_bowel_and_urine",
            "revisit_other_discomfort",
        }

        table = {row["field_name_eg"]: row for row in revisit_fields}

        for k, v in data.items():
            if (
                k in allowed
                and k in table
                and table[k].get("field_content") is None
                and v not in (None, "")
            ):
                table[k]["field_content"] = v

    except Exception as e:
        logger.warning(f"复诊预填充 LLM 解析失败：{e}")


def _infer_smoke_drink_frequency(text: str) -> Dict[str, Optional[str]]:
    """
    从个人史文本中抽取吸烟/饮酒频率枚举：
    返回 {"smoke": "从不|偶尔|有时|经常|每天"|None, "drink": 同上}
    """
    if not text:
        return {"smoke": None, "drink": None}

    t = str(text).replace(" ", "").lower()

    NEVER_PATTERNS_SMOKE = [
        r"不[吸抽]烟", r"无[吸抽]烟", r"无烟", r"从不[吸抽]烟",
        r"无烟酒史", r"无吸烟饮酒史", r"无烟酒"
    ]
    NEVER_PATTERNS_DRINK = [
        r"不(喝|饮)酒", r"无(饮|喝)酒", r"从不(喝|饮)酒",
        r"无酒精摄入", r"无酒史", r"无烟酒史", r"无吸烟饮酒史", r"无烟酒"
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