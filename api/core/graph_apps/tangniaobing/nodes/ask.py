

from langchain_core.messages.ai import AIMessage

from services.llm_service import LLMService

from .utils import get_table, get_known_list, stage_order
from ..prompt import REVISIT_QUESTION_SYSTEM_PROMPT, REVISIT_QUESTION_PROMPT, QUESTION_SYSTEM_PROMPT, QUESTION_PROMPT
from ..state import State, STAGE_CN, FIELD_SPECS


class AskNode:
    
    @staticmethod
    def run(
        state: State
    ):
        # 复诊：按顺序问、使用复诊专用提示词
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

            resp = LLMService.ask_question_in_revisit(
                system_prompt_template=REVISIT_QUESTION_SYSTEM_PROMPT,
                question_prompt_template=REVISIT_QUESTION_PROMPT,
                target_field_cn=target_field_cn,
                prefilled_text=prefilled_text,
                chat_history=state.chat_history,
            )

            question = resp.content.strip()
            state.chat_history.append(AIMessage(content=question))

            # 重要：标记该字段 “已问过”，以便下一步推进
            state.revisit_asked_fields.add(target_field_eg)
            state.last_asked_stage = "revisit"
            state.last_asked_field = target_field_eg
            return state

        # 初诊：沿用原逻辑
        if state.all_done or state.current_missing_field is None or state.current_stage not in stage_order(state):
            return state

        tbl = get_table(state)
        stage = state.current_stage
        stage_cn = STAGE_CN.get(stage, stage)

        name_map = {r["field_name_eg"]: r["field_name_cn"] for r in tbl}

        target_field_eg = state.current_missing_field
        target_field_cn = name_map.get(
            target_field_eg,
            FIELD_SPECS.get(target_field_eg, {}).get("cn", target_field_eg)
        )

        known_list_cn = [name_map[eg] for eg in (get_known_list(state) or []) if eg in name_map]

        resp = LLMService.ask_question_in_first_visit(
            system_prompt_template=QUESTION_SYSTEM_PROMPT,
            question_prompt_template=QUESTION_PROMPT,
            known_list_cn=known_list_cn,
            stage_cn=stage_cn,
            target_field_cn=target_field_cn,
            chat_history=state.chat_history,
        )

        question = resp.content.strip()
        state.chat_history.append(AIMessage(content=question))
        return state