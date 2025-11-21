import os
import sys
import uuid
import flask 
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from configs import app_config


def init_app(app: Flask):

    log_handlers: list[logging.Handler] = []
    log_file = app_config.LOG_FILE
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=app_config.LOG_FILE_MAX_SIZE * 1024 * 1024,
                backupCount=app_config.LOG_FILE_BACKUP_COUNT,
            )
        )

    # Always add StreamHandler to log to console
    sh = logging.StreamHandler(sys.stdout)
    log_handlers.append(sh)

    # Apply RequestIdFilter to all handlers
    for handler in log_handlers:
        handler.addFilter(RequestIdFilter())

def get_request_id():
    if getattr(flask.g, "request_id", None):
        return flask.g.request_id

    new_uuid = uuid.uuid4().hex[:10]
    flask.g.request_id = new_uuid

    return new_uuid

class RequestIdFilter(logging.Filter):
    # This is a logging filter that makes the request ID available for use in
    # the logging format. Note that we're checking if we're in a request
    # context, as we may want to log things before Flask is fully loaded.

    def filter(self, record):
        record.req_id = get_request_id() if flask.has_request_context() else ""
        return True