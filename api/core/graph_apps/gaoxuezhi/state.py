
from typing import Annotated, Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field

from langgraph.graph.message import add_messages

# 问诊阶段顺序
STAGES = ["condition", "history", "personal"]

REVISIT_STAGES = ["revisit"]

FIELD_SPECS: Dict[str, Dict[str, Any]] = {
    # 症状相关
    "condition": {
        "cn": "基本症状",
        "type": "text",
        "required": True,
        "desc": "用简短语句描述主要不适/主诉，如“腹痛”“咳嗽咳痰”等。"
    },
    "condition_duration": {
        "cn": "症状持续时间",
        "type": "duration",
        "required": True,
        "desc": "持续时间，建议规范化为 {value: 数字, unit: 分钟/小时/天/周/月/年}。"
    },
    "condition_location": {
        "cn": "症状部位",
        "type": "text",
        "required": False,
        "desc": "出现不适的部位，如“上腹部”“左下腹”等。"
    },
    "condition_severity": {
        "cn": "症状严重程度",
        "type": "enum|scale",
        "enums": ["轻度", "中度", "重度"],
        "scale": {"min": 1, "max": 10},
        "required": False,
        "desc": "可以是枚举（轻/中/重）或 1-10 分疼痛/严重程度。"
    },
    "associated_symptoms": {
        "cn": "伴随症状",
        "type": "list_text",
        "required": False,
        "desc": "用列表表示多个伴随症状，如['发热','恶心','呕吐']。"
    },
    "treatment_visited": {
        "cn": "有无就诊治疗过",
        "type": "bool",
        "required": False,
        "desc": "是/否 或 True/False。"
    },
    "treatment_diagnosis": {
        "cn": "就诊诊断",
        "type": "text",
        "required": False,
        "desc": "若就诊过，医生明确给出的诊断。"
    },
    "treatment_self_medication": {
        "cn": "有无自行使用过药物",
        "type": "bool",
        "required": False,
        "desc": "是/否 或 True/False。"
    },
    "medication_name": {
        "cn": "药物名称",
        "type": "list_text_or_text",
        "required": False,
        "desc": "可为单个药名字符串或药名列表。"
    },

    # 既往/过敏史
    "allergy_present": {
        "cn": "有无过敏食物或药物",
        "type": "bool",
        "required": False,
    },
    "allergy_foodordrug_name": {
        "cn": "过敏食物或药物名称",
        "type": "list_text_or_text",
        "required": False,
    },
    "long_term_medication_present": {
        "cn": "有无长期用药史",
        "type": "bool",
        "required": False,
    },
    "long_term_medication_name": {
        "cn": "长期用药名称",
        "type": "list_text_or_text",
        "required": False,
    },

    # 个人/生活方式与生理
    "personal_bad_habits": {"cn": "是否有不良生活习惯", "type": "text_or_bool", "required": False},
    "personal_smoking_frequency": {
        "cn": "抽烟频率",
        "type": "enum",
        "enums": ["从不", "偶尔", "有时", "经常", "每天"],
        "required": False
    },
    "personal_drinking_frequency": {
        "cn": "喝酒频率",
        "type": "enum",
        "enums": ["从不", "偶尔", "有时", "经常", "每天"],
        "required": False
    },
    "dietary_status": {"cn": "饮食与口味状况", "type": "text", "required": False},
    "sleep_status": {"cn": "睡眠状况", "type": "text", "required": False},
    "bowel_and_urine_condition": {"cn": "大小便状况", "type": "text", "required": True},

    # 月经/生育
    "menstrual_cycle": {
        "cn": "月经周期",
        "type": "duration_days_or_range",
        "required": True,
        "desc": "通常为天数或范围，如28天、25-35天。"
    },
    "menstrual_duration": {
        "cn": "经期天数",
        "type": "int_days",
        "required": True,
    },
    "last_menstrual_period": {
        "cn": "末次月经时间",
        "type": "date",
        "required": True,
        "desc": "建议标准化为 YYYY-MM-DD。"
    },
    # "menstrual_flow": {"cn": "经量", "type": "enum", "enums": ["少", "中", "多"], "required": False},
    "menstrual_flow": {"cn": "经量", "type": "text", "required": False},
    "menstrual_color": {"cn": "经色", "type": "text", "required": False},
    "menstrual_quality": {"cn": "经质", "type": "text", "required": False},
    "marital_reproductive_history": {"cn": "婚育史（18周岁以上）", "type": "text", "required": False},
    "full_term_birth_count": {"cn": "足月生产个数", "type": "int_ge0", "required": False},
    "preterm_birth_count": {"cn": "早产个数", "type": "int_ge0", "required": False},
    "miscarriage_count": {"cn": "流产个数", "type": "int_ge0", "required": False},
    "living_children_count": {"cn": "现存子女数量", "type": "int_ge0", "required": False},
    "children_count": {"cn": "已育子女数量", "type": "int_ge0", "required": False},

    # —— 复诊流程（随访） —— 
    "revisit_main_symptom": {
        "cn": "主要症状",
        "type": "text",
        "required": True
    },
    "revisit_associated_symptoms": {
        "cn": "伴随症状",
        "type": "list_text",
        "required": False
    },
    "revisit_diet": {
        "cn": "饮食习惯",
        "type": "text",
        "required": False
    },
    "revisit_sleep": {
        "cn": "睡眠状态",
        "type": "text",
        "required": False
    },
    "revisit_bowel_and_urine": {
        "cn": "大小便情况",
        "type": "text",
        "required": True
    },
    "revisit_other_hpi": {
        "cn": "其他现病史状况",
        "type": "text",
        "required": False
    },
    # 疗效评价-皮损严重程度：使用枚举或 0-4 量表
    "revisit_eval_erythema": {
        "cn": "疗效评价-皮损严重程度-红斑",
        "type": "enum|scale",
        "enums": ["无", "轻度", "中度", "重度"],
        "scale": {"min": 0, "max": 4},
        "required": False
    },
    "revisit_eval_edema_papules": {
        "cn": "疗效评价-皮损严重程度-水肿浸润丘疹",
        "type": "enum|scale",
        "enums": ["无", "轻度", "中度", "重度"],
        "scale": {"min": 0, "max": 4},
        "required": False
    },
    "revisit_eval_scale": {
        "cn": "疗效评价-皮损严重程度-鳞屑",
        "type": "enum|scale",
        "enums": ["无", "轻度", "中度", "重度"],
        "scale": {"min": 0, "max": 4},
        "required": False
    },
    "revisit_eval_lichenification": {
        "cn": "疗效评价-皮损严重程度-苔藓样改变",
        "type": "enum|scale",
        "enums": ["无", "轻度", "中度", "重度"],
        "scale": {"min": 0, "max": 4},
        "required": False
    },
    "revisit_other_discomfort": {
        "cn": "其他不适",
        "type": "text",
        "required": False
    },
}

# 阶段中文名
STAGE_CN = {
    "condition": "症状采集",
    "history":   "既往/过敏史采集",
    "personal":  "个人生活与生理采集",
    "revisit": "复诊"
}

CONDITION_FIELDS_TEMPLATE = [
    {"field_content": None, "field_name_cn": "基本症状", "field_name_eg": "condition"},
    {"field_content": None, "field_name_cn": "症状持续时间", "field_name_eg": "condition_duration"},
    {"field_content": None, "field_name_cn": "症状部位", "field_name_eg": "condition_location"},
    {"field_content": None, "field_name_cn": "症状严重程度", "field_name_eg": "condition_severity"},
    {"field_content": None, "field_name_cn": "伴随症状", "field_name_eg": "associated_symptoms"},
    {"field_content": None, "field_name_cn": "有无就诊治疗过", "field_name_eg": "treatment_visited"},
    {"field_content": None, "field_name_cn": "就诊诊断", "field_name_eg": "treatment_diagnosis"},
    {"field_content": None, "field_name_cn": "有无自行使用过药物", "field_name_eg": "treatment_self_medication"},
    {"field_content": None, "field_name_cn": "药物名称", "field_name_eg": "medication_name"},
]

HISTORY_FIELDS_TEMPLATE = [
    {"field_content": None, "field_name_cn": "过敏食物或药物名称", "field_name_eg": "allergy_foodordrug_name"},
    {"field_content": None, "field_name_cn": "长期用药名称", "field_name_eg": "long_term_medication_name"},
    {"field_content": None, "field_name_cn": "家族史", "field_name_eg": "family_history"},
]

PERSONAL_FIELDS_TEMPLATE = [
    {"field_content": None, "field_name_cn": "是否有不良生活习惯", "field_name_eg": "personal_bad_habits"},
    {"field_content": None, "field_name_cn": "抽烟频率", "field_name_eg": "personal_smoking_frequency"},
    {"field_content": None, "field_name_cn": "喝酒频率", "field_name_eg": "personal_drinking_frequency"},
    {"field_content": None, "field_name_cn": "饮食与口味状况", "field_name_eg": "dietary_status"},
    {"field_content": None, "field_name_cn": "睡眠状况", "field_name_eg": "sleep_status"},
    {"field_content": None, "field_name_cn": "大小便状况", "field_name_eg": "bowel_and_urine_condition"},
    {"field_content": None, "field_name_cn": "月经周期", "field_name_eg": "menstrual_cycle"},
    {"field_content": None, "field_name_cn": "经期天数", "field_name_eg": "menstrual_duration"},
    # {"field_content": None, "field_name_cn": "末次月经时间", "field_name_eg": "last_menstrual_period"},
    {"field_content": None, "field_name_cn": "经量", "field_name_eg": "menstrual_flow"},
    {"field_content": None, "field_name_cn": "经色", "field_name_eg": "menstrual_color"},
    {"field_content": None, "field_name_cn": "经质", "field_name_eg": "menstrual_quality"},
    {"field_content": None, "field_name_cn": "婚育史（18周岁以上）", "field_name_eg": "marital_reproductive_history"},
    {"field_content": None, "field_name_cn": "足月生产个数", "field_name_eg": "full_term_birth_count"},
    {"field_content": None, "field_name_cn": "早产个数", "field_name_eg": "preterm_birth_count"},
    {"field_content": None, "field_name_cn": "流产个数", "field_name_eg": "miscarriage_count"},
    {"field_content": None, "field_name_cn": "现存子女数量", "field_name_eg": "living_children_count"},
    {"field_content": None, "field_name_cn": "已育子女数量", "field_name_eg": "children_count"},
]

REVISIT_FIELDS_TEMPLATE = [
    {"field_content": None, "field_name_cn": "主要症状", "field_name_eg": "revisit_main_symptom"},
    # {"field_content": None, "field_name_cn": "伴随症状", "field_name_eg": "revisit_associated_symptoms"},
    {"field_content": None, "field_name_cn": "饮食习惯", "field_name_eg": "revisit_diet"},
    {"field_content": None, "field_name_cn": "睡眠状态", "field_name_eg": "revisit_sleep"},
    {"field_content": None, "field_name_cn": "大小便情况", "field_name_eg": "revisit_bowel_and_urine"},
    # {"field_content": None, "field_name_cn": "其他现病史状况", "field_name_eg": "revisit_other_hpi"},
    {"field_content": None, "field_name_cn": "疗效评价-皮损严重程度-红斑", "field_name_eg": "revisit_eval_erythema"},
    {"field_content": None, "field_name_cn": "疗效评价-皮损严重程度-水肿浸润丘疹", "field_name_eg": "revisit_eval_edema_papules"},
    {"field_content": None, "field_name_cn": "疗效评价-皮损严重程度-鳞屑", "field_name_eg": "revisit_eval_scale"},
    {"field_content": None, "field_name_cn": "疗效评价-皮损严重程度-苔藓样改变", "field_name_eg": "revisit_eval_lichenification"},
    {"field_content": None, "field_name_cn": "其他不适", "field_name_eg": "revisit_other_discomfort"},
]

class State(BaseModel):
    messages: Annotated[List, add_messages] = Field(default_factory=list)
    session_id: str

    gender: Optional[str] = None

    is_revisit: bool = False

    # 首次病历 JSON
    initial_context: Optional[Dict[str, Any]] = None
    record_initialized: bool = False

    # 对话历史（AI/Human）
    chat_history: List = Field(default_factory=list)

    # 三张字段表
    condition_fields: List[Dict] = Field(default_factory=lambda: [f.copy() for f in CONDITION_FIELDS_TEMPLATE])
    history_fields:   List[Dict] = Field(default_factory=lambda: [f.copy() for f in HISTORY_FIELDS_TEMPLATE])
    personal_fields:  List[Dict] = Field(default_factory=lambda: [f.copy() for f in PERSONAL_FIELDS_TEMPLATE])
    
    revisit_fields: List[Dict] = Field(default_factory=lambda: [f.copy() for f in REVISIT_FIELDS_TEMPLATE])

    revisit_asked_fields: Set[str] = Field(default_factory=set)

    # 当前阶段 & 当前要问/要填的字段（由 process 决定）
    current_stage: Optional[str] = None
    current_missing_field: Optional[str] = None
    start_missing_total: int = 0  # 新增：记录一开始就缺失的字段数量

    # 阶段内缺失/已知（冗余缓存，便于日志/提示）
    missing_fields: List[str] = Field(default_factory=list)
    known_fields: List[str] = Field(default_factory=list)

    # 缓存最近一次 ask 的目标（用于标注消息）
    last_asked_stage: Optional[str] = None
    last_asked_field: Optional[str] = None

    # 本阶段对话轮数 & 全局轮数
    stage_rounds: int = 0
    dialogue_count: int = 0

    # 全量完成标志
    all_done: bool = False
