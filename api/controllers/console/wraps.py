from functools import wraps
from typing import ParamSpec, TypeVar, Callable

from controllers.console.error import NotInitValidateError
from extensions.ext_database import db
from models.model import AppSetup

P = ParamSpec("P")
R = TypeVar("R")

def setup_required(view: Callable[P, R]):
    @wraps(view)
    def decorated(*args: P.args, **kwargs: P.kwargs):
        if (not db.session.query(AppSetup).first()):
            raise NotInitValidateError()

        return view(*args, **kwargs)

    return decorated