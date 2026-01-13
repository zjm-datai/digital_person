
from typing import Dict, List

from ..state import State, STAGES, REVISIT_STAGES

def is_all_filled(state: State) -> bool:
    if state.is_revisit:
        all_rows = state.revisit_fields
    else:
        all_rows = state.condition_fields + state.history_fields + state.personal_fields
    return all(r.get("field_content") is not None for r in all_rows)


def stage_order(state: State) -> list:
    """获取当前问诊模式的阶段顺序：复诊返回 REVISIT_STAGES，初诊返回 STAGES"""

    return REVISIT_STAGES if state.is_revisit else STAGES


def next_revisit_field(state: State) -> str | None:
    """复诊专用：顺序取下一个「尚未问过」的字段标识，无则返回None"""
    
    for row in state.revisit_fields:
        eg = row["field_name_eg"]
        if eg not in state.revisit_asked_fields:
            return eg
    return None


def stage_has_missing(state: State, stage_key: str) -> bool:
    """判断指定阶段是否存在未填充的缺失字段，返回布尔值"""
    
    if stage_key == "revisit":
        table = state.revisit_fields
    else:
        table = {
            "condition": state.condition_fields,
            "history": state.history_fields,
            "personal": state.personal_fields
        }[stage_key]
    return any(r.get("field_content") is None for r in table)

def advance_until_stage_with_missing(state: State) -> None:
    """
    从当前阶段开始推进到“仍需提问”的阶段：
    - 复诊：按固定顺序逐项问，问过一次就进入下一项；全部问完即 all_done=True
    - 初诊：沿用原逻辑（寻找仍有缺失的阶段/字段）
    """
    stages = stage_order(state)
    if not stages:
        state.current_missing_field = None
        state.all_done = True
        return

    # 复诊特化
    if state.is_revisit and "revisit" in stages:
        state.current_stage = "revisit"
        nxt = next_revisit_field(state)
        if nxt is None:
            state.current_missing_field = None
            state.all_done = True
        else:
            state.current_missing_field = nxt
            state.all_done = False
        return

    # 初诊沿用旧逻辑
    if state.current_stage not in stages:
        state.current_stage = stages[0]

    start_idx = stages.index(state.current_stage)
    for idx in range(start_idx, len(stages)):
        stage_key = stages[idx]
        if stage_has_missing(state, stage_key):
            state.current_stage = stage_key
            state.current_missing_field = next_missing_field_in_stage(state)
            state.all_done = False
            return

    state.current_missing_field = None
    state.all_done = True


def next_missing_field_in_stage(state: State) -> str | None:
    """返回当前阶段下第一个缺失字段的英文标识，无缺失则返回None"""
    
    if not state.current_stage:
        return []
    if state.current_stage == "revisit":
        table = state.revisit_fields
    else:
        table = {
            "condition": state.condition_fields,
            "history": state.history_fields,
            "personal": state.personal_fields
        }[state.current_stage]
    for r in table:
        if r.get("field_content") is None:
            return r["field_name_eg"]
    return None


def advance_until_stage_missing(
    state: State
):
    stages = stage_order(state)
    if not stages:
        state.current_missing_field = None
        state.all_done = True
        return
    
    if state.is_revisit and "revisit" in stages:
        state.current_stage = "revisit"
        next_field = next_revisit_field(state)
        if next_field is None:
            state.current_missing_field = None
            state.all_done = True
        else:
            state.current_missing_field = next_field
            state.all_done = False
            
        return 
    
    if state.current_stage not in stages:
        state.current_stage = stages[0]
    
    start_index = stages.index(state.current_stage)
    for idx in range(start_index, len(stages)):
        stage_key = stages[idx]
        if stage_has_missing(state, stage_key):
            state.current_stage = stage_key
            state.current_missing_field = next_missing_field_in_stage(state)
            state.all_done = False
            
            return

    state.current_missing_field = None
    state.all_done = True
    
    return

def get_table(state: State) -> List[Dict]:
    if not state.current_stage:
        return []
    if state.current_stage == "revisit":
        return state.revisit_fields
    return {
        "condition": state.condition_fields,
        "history": state.history_fields,
        "personal": state.personal_fields
    }[state.current_stage]

def get_missing(state: State) -> List[str]:
    if not state.current_stage:
        return []
    tbl = get_table(state)
    return [r["field_name_eg"] for r in tbl if r.get("field_content") is None]

def get_known_list(state: State) -> List[str]:
    if not state.current_stage:
        return []
    tbl = get_table(state)
    return [r["field_name_eg"] for r in tbl if r.get("field_content") is not None]

def progress_counts(state: State) -> dict:
    """
    返回 {'completed': x, 'total': y}

    - 复诊：无论是否成功填充，按已问过的复诊字段个数统计进度；
    - 初诊：保持原逻辑，按缺失数量的填充进度统计。
    """
    if state.is_revisit:
        total = len(state.revisit_fields)
        completed = len(state.revisit_asked_fields)
        completed = min(max(0, completed), total)
        return {"completed": completed, "total": total}

    total = state.start_missing_total or 0
    remaining = self._count_all_missing(state)
    completed = max(0, total - remaining)
    
    return {"completed": completed, "total": total}