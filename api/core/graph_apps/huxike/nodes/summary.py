
from langchain_core.messages.ai import AIMessage

from services.llm_service import LLMService

from ..prompt import REVISIT_SUMMARY_SYSTEM_PROMPT_MAN, REVISIT_SUMMARY_SYSTEM_PROMPT, SUMMARY_SYSTEM_PROMPT_MAN, SUMMARY_SYSTEM_PROMPT
from ..state import State

class SummaryNode:
    
    @staticmethod
    def run(
        state: State
    ):
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
                last_record = (ctx.get("latestMedicalRecord") or {})
            except Exception:
                last_record = {}

            family_history_item = next(
                (item for item in state.history_fields if item["field_name_eg"] == "family_history"),
                None
            )

            family_history = family_history_item["field_content"] if (family_history_item and family_history_item["field_content"]) else "无"

            payload = {
                "basic_fields": {
                    "family_history": family_history
                },
                "last_record": last_record,
                "revisit_fields": state.revisit_fields,
                "_notes": {
                    "scene": "revisit",
                    "gender": gender or "未知",
                    "bowel_urine_field": "revisit_bowel_and_urine",
                    "missing_repr": "无记录"
                }
            }

            resp = LLMService.summarize_revisit(
                revisit_summary_system_prompt=summary_tmpl,
                payload=payload,
            )

            state.chat_history.append(AIMessage(content=resp.content))
            return state

        if state.gender == "男":
            summary_prompt = SUMMARY_SYSTEM_PROMPT_MAN
        else:
            summary_prompt = SUMMARY_SYSTEM_PROMPT

        ctx_payload = {
            "condition_fields": state.condition_fields,
            "history_fields": state.history_fields,
            "personal_fields": state.personal_fields
        }

        resp = LLMService.summarize_first_visit(
            summary_system_prompt=summary_prompt,
            ctx_payload=ctx_payload,
        )

        state.chat_history.append(AIMessage(content=resp.content))
        return state