
import logging

from werkzeug.exceptions import InternalServerError

from extensions.ext_database import db
from models.conversation import Message
from models.model import AppType
from services.errors.message import MessageNotExistsError
from services.llm_service import LLMService

logger = logging.getLogger(__name__)

HARD_CODE_SUGGESTIONS = {
    # revisit（复诊随访）
    "revisit_other_hpi": ["按时用药", "外用不规律", "停药后反复", "近期压力大"],
    "revisit_eval_erythema": ["无红斑", "红斑颜色很淡，比较轻微", "红斑很明显，颜色发红，程度中等", "红斑颜色鲜红或者深红，看着就很严重"],
    "revisit_eval_edema_papules": ["无", "有一些细小的疙瘩，情况比较轻", "疙瘩比较多，情况中等", "疙瘩非常多，而且还有出水的情况，比较严重"],
    "revisit_eval_scale": ["无脱屑",  "只有轻微脱屑，皮屑很少", "好多地方都在脱屑，鳞屑比较多", "脱屑特别明显，脱屑范围大，而且鳞屑特别多"],
    "revisit_eval_lichenification": ["无", "能感觉到皮肤纹理稍微增厚了一点", "肉眼就能看到皮肤纹理增厚了，程度中等", "皮肤纹理增厚，像牛皮纸一样，情况严重"],
    "revisit_other_discomfort": ["无其他不适", "偶头晕", "轻微乏力"],

    # personal（个人与月经/婚育）
    "menstrual_flow": ["量少", "中等", "量多", "有血块"],
    "menstrual_color": ["鲜红", "暗红", "褐色"],
    "menstrual_quality": ["稀薄", "黏稠", "伴血块"],
    "marital_reproductive_history": ["未婚未育", "已婚未育", "已婚已育", "离异"],
    "full_term_birth_count": ["0个", "1个", "2个"],
    "preterm_birth_count": ["0个", "1个"],
    "miscarriage_count": ["0次", "1次", "≥2次"],
    "living_children_count": ["0个", "1个", "2个", "3个以上"],
    "children_count": ["0个", "1个", "2个", "≥3个"],
    "personal_bad_habits": ["无明显", "熬夜较多", "爱抓挠", "不常保湿"],
    "personal_smoking_frequency": ["不吸烟", "偶尔", "每天半包", "已戒烟"],
    "personal_drinking_frequency": ["不喝酒", "偶尔小酌", "每周1次", "社交性饮酒"],
}

class MessageService:

    @classmethod
    def get_message(cls, app_type: AppType, message_id: str):
        message = (
            db.session.query(Message)
            .where(
                Message.id == message_id,
                Message.app_type == app_type
            )
            .first()
        )

        if not message:
            raise MessageNotExistsError()

        return message

    @staticmethod
    def create_message(
        conversation_id: str, message: str, **kwargs
    ) -> str:
        try:

            new_message = Message(
                conversation_id=conversation_id,
                content=message,
                **kwargs
            )
            db.session.add(new_message)
            db.session.commit()
            logger.info(f"Message created with ID: {new_message.id}")
            return new_message.id
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create message: {e}")
            raise

    @classmethod
    def get_suggested_answers_after_question(
        cls, app_type: str, message_id: str
    ):
        message = cls.get_message(app_type, message_id)

        stage = message.current_stage
        field = message.current_field
        question = message.content

        if field in HARD_CODE_SUGGESTIONS:
            suggestions = HARD_CODE_SUGGESTIONS[field][:6] or []
            return suggestions

        try:
            success, parsed_result, raw_output = LLMService.suggest_answers_after_question(
                stage=stage,
                field=field,
                question=question,
                app_type=app_type,
            )

            if success:
                return parsed_result
            else:
                logger.warning(f"LLM 生成候选答案失败，raw_output: {raw_output}")
                return []

        except Exception as e:
            logger.exception("调用 LLMService.suggest_answers_after_question 出错")
            raise InternalServerError() from e


