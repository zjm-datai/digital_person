
import re
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage

from services.wraps.llm_run_log import llm_log

from configs import app_config

logger = logging.getLogger(__name__)

SUGGEST_QUESTION_PROMPT = """/no_think
## 你的角色
你是一个推荐回复生成器
## 你的任务
本次问诊是 {app_type}，当前医生的提问针对的是 {stage} 阶段的 {field} 进行的提问，你需要根据医生的提问和当前阶段和提问目的，给患者生成最多 {k} 条相关的简短候选回复
## 格式要求
- 每条不超过 15 个字
- 语言与原文一致
- 避免重复
- 不要加编号或解释
- 要生成对医生提问的回复，不要生成提问
仅输出一个 JSON 数组，不输出任何其他内容，包括解释、说明或链接。
严格遵守 JSON 格式，使用双引号，数组元素为字符串。
例如：["皮肤瘙痒","红斑起疹子了","皮肤发炎很疼"]
例如：["便血", "排便困难", "肛门肿胀"]
例如：["咳嗽", "咳痰", "呼吸不畅"]
医生提问：{question}
"""

class LLMService:

    llm: ChatOpenAI = ChatOpenAI(
        model=app_config.LLM_MODEL,
        temperature=app_config.DEFAULT_LLM_TEMPERATURE,
        api_key=app_config.LLM_API_KEY,
        base_url=app_config.LLM_BASE_URL,
    )

    @classmethod
    def ask_question_in_first_visit(
        cls,
        system_prompt_template: str,
        question_prompt_template: str,
        known_list_cn: List[str],
        stage_cn: str,
        target_field_cn: str,
        chat_history: List[BaseMessage],
    ):
        system_prompt = SystemMessage(
            content=system_prompt_template.format(
                known_list_cn=known_list_cn,
                stage_cn=stage_cn,
                target_field_cn=target_field_cn,
            )
        )
        question_prompt = HumanMessage(
            content=question_prompt_template.format(target_field_cn=target_field_cn)
        )
        msgs = [system_prompt] + chat_history + [question_prompt] if chat_history else [system_prompt, question_prompt]
        resp = cls.llm.invoke(msgs)
        
        return resp

    @classmethod
    def ask_question_in_revisit(
        cls, system_prompt_template, question_prompt_template, target_field_cn: str, prefilled_text: str, chat_history
    ):
        system_prompt = SystemMessage(
            content=system_prompt_template.format(
                target_field_cn=target_field_cn,
            )
        )
        question_prompt = HumanMessage(
            content=question_prompt_template.format(
                target_field_cn=target_field_cn,
                prefilled_text=prefilled_text
            )
        )
        
        msgs = [system_prompt] + chat_history + [question_prompt] if chat_history else [system_prompt, question_prompt]
        resp = cls.llm.invoke(msgs)
        
        return resp

    @classmethod
    @llm_log("extract_fields_from_recent_chat")
    def extract_fields_from_recent_chat(
        cls,
        fill_fields_prompt_template: str,
        stage_cn: str,
        specs: List[Dict[str, Any]],
        chat_log: str,
    ) -> Dict[str, Any]:

        prompt = fill_fields_prompt_template.format(
            stage_cn=stage_cn,
            field_cns="、".join(s["field_cn"] for s in specs),
            specs=json.dumps(specs, ensure_ascii=False, indent=2),
            chat_log=chat_log or "(无对话)",
        )

        resp = cls.llm.invoke([SystemMessage(content=prompt)])

        m = re.search(r"\{.*\}", resp.content, re.DOTALL) # type: ignore
        if not m:
            
            return {}

        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            logger.warning("extract_fields_from_recent_chat: JSON 解析失败")
            return {}
    
    @classmethod
    def prefill_revisit_from_present_illness(
        cls,
        revisit_prefill_prompt_template: str,
        present_illness: str,
    ) -> Dict[str, Any]:
        prompt = revisit_prefill_prompt_template.format(present_illness=present_illness)

        resp = cls.llm.invoke([SystemMessage(content=prompt)])
        m = re.search(r"\{.*\}", resp.content, re.DOTALL) # type: ignore
        if not m:
            return {}

        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            logger.warning("prefill_revisit_from_present_illness: JSON 解析失败")
            
            return {}

    @classmethod
    @llm_log("summarize_first_visit")
    def summarize_first_visit(
        cls,
        summary_system_prompt: str,
        ctx_payload: Dict[str, Any],
    ):
        sys = SystemMessage(content=summary_system_prompt)
        ctx = SystemMessage(content=json.dumps(ctx_payload, ensure_ascii=False))
        resp = cls.llm.invoke([ctx, sys])
        
        return resp

    @classmethod
    @llm_log("summarize_revisit")
    def summarize_revisit(
        cls,
        revisit_summary_system_prompt: str,
        payload: Dict[str, Any],
    ):
        sys = SystemMessage(content=revisit_summary_system_prompt)
        ctx_msg = SystemMessage(content=json.dumps(payload, ensure_ascii=False))
        resp = cls.llm.invoke([sys, ctx_msg])
        
        return resp

    @classmethod
    @llm_log("suggest_answers_after_question")
    def suggest_answers_after_question(
            cls,
            stage: str,
            field: str,
            question: str,
            prompt: str = SUGGEST_QUESTION_PROMPT,
            k: int = 5,
            app_type: str = ""
    ) -> Tuple[bool, List[str], str]:
        filled_prompt = prompt.format(
            app_type=app_type,
            stage=stage,
            field=field,
            question=question,
            k=k,
        )

        resp = cls.llm.invoke([SystemMessage(content=filled_prompt)])
        raw_output = resp.content if resp else ""
        success = False
        parsed_result: List[str] = []

        if raw_output:
            m = re.search(r"\[.*\]", raw_output, re.DOTALL)  # type: ignore
            if m:
                try:
                    data = json.loads(m.group())
                    if isinstance(data, list):
                        parsed_result = [str(x) for x in data if isinstance(x, str)]
                        success = True
                except json.JSONDecodeError:
                    logger.warning("suggest_answers_after_question: JSON 解析失败")
            else:
                logger.warning("suggest_answers_after_question: 未找到 JSON 数组")

        return success, parsed_result, raw_output
