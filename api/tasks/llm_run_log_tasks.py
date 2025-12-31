
import logging
import uuid
from datetime import datetime
from typing import Mapping
from celery import shared_task

from extensions.ext_database import db
from models.log import LLMRunLog

logger = logging.getLogger(__name__)

def _parse_dt(v) -> None | datetime:
    if v is None:
        return None
    if isinstance(v, datetime):
        return v
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v)
        except Exception:
            return None
    return None


@shared_task(name="llm.save_run_log", ignore_result=True)
def save_llm_run_log(payload: Mapping):
    
    try:
        llm_run_log = LLMRunLog(
            id=payload.get("id") or str(uuid.uuid4()),
            conversation_id=payload.get("conversation_id", ""),
            message_id=payload.get("message_id", ""),
            type=payload.get("type", ""),
            inputs=payload.get("inputs", ""),
            outputs=payload.get("outputs", ""),
            start_time=_parse_dt(payload.get("start_time")) or datetime.utcnow(),
            end_time=_parse_dt(payload.get("end_time", "")),
            elapsed_time=payload.get("elapsed_time", ""),
            status=payload.get("status") or "success",
            error=payload.get("error", ""), 
            prompt_tokens=payload.get("prompt_tokens", ""),
            completion_tokens=payload.get("completion_tokens", ""),
            total_tokens=payload.get("total_tokens", ""),
            hospital_guid=payload.get("hospital_guid", ""),
            hospital_name=payload.get("hospital_name", ""),
            trace_id=payload.get("opc_id", ""),
        )
        
        db.session.add(llm_run_log)
        db.session.commit()
    except Exception as e:
        logger.info(f"LLM Run Log 保存失败: {e}")
    finally:
        db.session.close()