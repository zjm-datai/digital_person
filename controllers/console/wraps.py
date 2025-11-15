
import os

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from configs import app_config

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