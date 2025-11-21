
import os

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from flask import current_app

from configs import app_config
from core.agents.doctor_agent.agent import DoctorAgent

from extensions.ext_database import db

from .error import NotInitValidateError, NotSetupError

P = ParamSpec("P")
R = TypeVar("R")


def setup_required(view: Callable[P, R]):
    @wraps(view)
    def decorated(*args: P.args, **kwargs: P.kwargs):
        # check setup
        if (
            app_config.EDITION == "SELF_HOSTED"
            and os.environ.get("INIT_PASSWORD")
            and not db.session.query(AppSetup).first()
        ):
            raise NotInitValidateError()
        elif app_config.EDITION == "SELF_HOSTED" and not db.session.query(AppSetup).first():
            raise NotSetupError()

        return view(*args, **kwargs)

    return decorated

# 注释支持太差
# def get_doctor_agent(view: Callable[P, R]) -> Callable[P, R]:
#     @wraps(view)
#     def decorated(*args: P.args, **kwargs: P.kwargs) -> R:
#         doctor_agent: DoctorAgent = current_app.extensions["doctor_agent"]
#         kwargs['doctor_agent'] = doctor_agent
#         return view(*args, **kwargs)
#
#     return decorated