import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from flask import request
from flask_restx import Resource, fields
from pydantic import BaseModel, Field
from werkzeug.exceptions import BadRequest

from libs.login import login_required
from controllers.console import console_ns
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

DEFAULT_REF_TEMPLATE_SWAGGER_2_0 = "#/definitions/{model}"

class AsrSuggestQuery(BaseModel):
    asr: str = Field(..., description="语音识别文本")
    ai: Optional[str] = Field(None, description="可选：最近一条 AI 提示/追问文本")
    k: int = Field(6, ge=1, le=10, description="候选条数上限")
    locale: str = Field("zh", description="语言：zh/en 等")

def reg(cls: type[BaseModel]):
    console_ns.schema_model(
        cls.__name__,
        cls.model_json_schema(ref_template=DEFAULT_REF_TEMPLATE_SWAGGER_2_0),
    )

reg(AsrSuggestQuery)

asr_option_fields = console_ns.model("AsrSuggestOption", {
    "label": fields.String(description="按钮展示短句"),
    "value": fields.String(description="完整纠正文本"),
})

asr_suggest_response_fields = console_ns.model("AsrSuggestResponse", {
    "options": fields.List(fields.Nested(asr_option_fields)),
})

def _parse_options_json(text: str) -> List[Dict[str, str]]:
    if not text:
        return []

    s = text.strip()

    try:
        obj = json.loads(s)
        return _extract_options(obj)
    except Exception:
        pass

    # 2) 尝试从文本里截取 {...}
    m = re.search(r"\{.*\}", s, re.DOTALL)
    if not m:
        return []

    try:
        obj = json.loads(m.group())
        return _extract_options(obj)
    except Exception:
        return []

def _extract_options(obj: Any) -> List[Dict[str, str]]:
    if not isinstance(obj, dict):
        return []
    arr = obj.get("options", [])
    if not isinstance(arr, list):
        return []
    out: List[Dict[str, str]] = []
    for x in arr:
        if not isinstance(x, dict):
            continue
        label = x.get("label")
        value = x.get("value")
        if isinstance(label, str) and isinstance(value, str):
            label = label.strip()
            value = value.strip()
            if label and value:
                out.append({"label": label, "value": value})
    return out

def _dedupe_options(options: List[Dict[str, str]], k: int) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []
    for x in options:
        key = f'{x.get("label","")}|||{x.get("value","")}'
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
        if len(out) >= k:
            break
    return out

ASR_SUGGEST_PROMPT = """/no_think
你是医疗问诊系统的“ASR 纠正器”。

输入：
- ASR：{asr}
- AI：{ai}

任务：
- 基于 ASR（以及可选的上一条医生/AI 追问）生成最多 {k} 条**纠正后的表达**候选，让用户一键选择。
- 语种使用 {lang}。
- 严格保持医学语义合理；保留数字与时间量纲（如 3 天、2 周、38.5℃ 等）。
- 不要编造未出现的关键信息。
- 每条包含：
  - label：按钮展示的短句（3~12字/words，摘要式）
  - value：可直接提交的**完整纠正文本**（通顺规范）

仅输出一个 JSON 对象，严格遵守 JSON 格式（双引号），不要包含任何解释或多余文本。
格式如下（示例）：
{{
  "options": [
    {{"label": "反复瘙痒3周", "value": "我反复瘙痒已有3周，夜间更重。"}},
    {{"label": "体温38.5℃", "value": "我今天体温 38.5℃，伴有寒战。"}}
  ]
}}
"""

@console_ns.route("/asr/suggest")
class AsrSuggestedApi(Resource):
    @console_ns.doc("asr_suggest")
    @console_ns.doc(description="根据 ASR（+可选AI提示）生成纠正候选")
    @console_ns.expect(console_ns.models[AsrSuggestQuery.__name__])
    @console_ns.marshal_with(asr_suggest_response_fields)
    @login_required
    def get(self):
        try:
            args = AsrSuggestQuery.model_validate(request.args.to_dict(flat=True))  # type: ignore
        except Exception as e:
            raise BadRequest(str(e))

        asr = (args.asr or "").strip()
        ai = (args.ai or "").strip() if args.ai else None
        k = args.k
        locale = (args.locale or "zh").strip().lower()
        lang = "中文" if locale.startswith("zh") else "English"

        try:
            raw_text = LLMService.asr_suggest(
                prompt_template=ASR_SUGGEST_PROMPT,
                asr=asr,
                ai=ai,
                k=k,
                lang=lang,
            )

            arr = _parse_options_json(raw_text)
            arr = _dedupe_options(arr, k)

            if not arr:
                brief = asr
                if brief:
                    label = brief if len(brief) <= 12 else brief[:12]
                    arr = [{"label": label, "value": brief}]
                else:
                    brief2 = "请重述" if lang == "中文" else "Please repeat"
                    arr = [{"label": brief2 if len(brief2) <= 12 else brief2[:12], "value": brief2}]

            return {"options": arr}, 200

        except Exception as e:
            logger.warning("audio_suggest_failed: %s", e)
            brief = asr or ("请重述" if lang == "中文" else "Please repeat")
            label = brief if len(brief) <= 12 else brief[:12]

            return {"options": [{"label": label, "value": brief}]}, 200
