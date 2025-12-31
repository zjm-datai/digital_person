import json
import time
import functools
import logging
from typing import Any, Callable, Optional
from datetime import datetime

from flask import has_request_context, g

from tasks.llm_run_log_tasks import save_llm_run_log

from configs import app_config

logger = logging.getLogger(__name__)

def get_llm_run_context():
    if has_request_context() and hasattr(g, "llm_run_context"):
        return g.llm_run_context

    logger.info("no llm_run_context")

    return None


def _to_jsonable(x: Any):
    if x is None or isinstance(x, (str, int, float, bool)):
        return x
    if isinstance(x, dict):
        return {str(k): _to_jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_to_jsonable(i) for i in x]
    if hasattr(x, "content"):
        return {"__type_": x.__class__.__name__, "content": getattr(x, "content", None)}
    return {"__type_": x.__class__.__name__, "__repr__": repr(x)}

def _dumps(x: Any, max_len: int = 50000) -> str:
    s = json.dumps(_to_jsonable(x), ensure_ascii=False, default=str)
    return s if len(s) <= max_len else s[:max_len] + "…(truncated)"

def _safe_delay(payload: dict) -> None:
    try:
        save_llm_run_log.delay(payload)  # type: ignore[attr-defined]
    except Exception:
        logger.exception("日志任务入队失败")

def _build_payload(
    *,
    context: Any,
    type: str,
    inputs_obj: Any,
    outputs_obj: Any,
    start_time: datetime,
    t0: float,
    status: str,
    error: Optional[str],
) -> dict:
    # 序列化失败也不应该影响主流程，所以这里单独 try
    try:
        inputs = _dumps(inputs_obj)
    except Exception:
        logger.exception("inputs 序列化失败")
        inputs = '"<serialize inputs failed>"'

    try:
        outputs = _dumps(outputs_obj)
    except Exception:
        logger.exception("outputs 序列化失败")
        outputs = '"serialize outputs failed"'

    now = datetime.utcnow()
    return {
        "conversation_id": context.get("conversation_id", ""),
        "message_id": context.get("message_id", ""),
        "type": type,
        "inputs": inputs,
        "outputs": outputs,
        "start_time": start_time.isoformat(),
        "end_time": now.isoformat(),
        "elapsed_time": time.perf_counter() - t0,
        "status": status,
        "error": error,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "hospital_guid": context.get("hospital_guid", ""),
        "hospital_name": context.get("hospital_name", ""),
        "opc_id": context.get("opc_id", ""),
    }

def llm_log(type: str):
    def deco(func: Callable):
        @functools.wraps(func)
        def wrapper(cls, *args, **kwargs):
            if not app_config.LLM_LOG_ENABLED:
                return func(cls, *args, **kwargs)

            context = get_llm_run_context()
            start_time = datetime.utcnow()
            t0 = time.perf_counter()
            inputs_obj = {"args": args, "kwargs": kwargs}

            resp: Any = None
            err: Optional[BaseException] = None

            try:
                resp = func(cls, *args, **kwargs)
                return resp
            except BaseException as e:
                err = e
                raise
            finally:
                status = "success" if err is None else "failed"
                payload = _build_payload(
                    context=context,
                    type=type,
                    inputs_obj=inputs_obj,
                    outputs_obj=resp,
                    start_time=start_time,
                    t0=t0,
                    status=status,
                    error=None if err is None else str(err),
                )
                print(payload)
                _safe_delay(payload)

        return wrapper
    return deco
