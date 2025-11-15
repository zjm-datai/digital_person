import time

import logging

from flask import Flask

from contexts.wrapper import RecyclableContextVar

from configs import app_config

logger = logging.getLogger(__name__)

def create_flask_app_with_configs() -> Flask:
    app = Flask(__name__)

    app.config.from_mapping(
        app_config.model_dump()
    )

    @app.before_request
    def before_request():
        # add an unique identifier to each request
        RecyclableContextVar.increment_thread_recycles()

    # Capture the decorator's return value to avoid pyright reportUnusedFunction
    _ = before_request

    return app

def initialize_app(app: Flask):

    from extensions import (
        ext_app_metrics,
        ext_blueprints,
        ext_database,
        ext_logging,
        ext_timezone
    )

    extensions = [
        ext_timezone,
        ext_logging,
        ext_database,
        ext_app_metrics,
        ext_blueprints,
    ]

    for ext in extensions:
        short_name = ext.__name__.split(".")[-1]
        is_enabled = ext.is_enabled() if hasattr(ext, "is_enabled") else True
        if not is_enabled:
            if app_config.DEBUG:
                logger.info("Skipped %s", short_name)
            continue

        start_time = time.perf_counter()
        ext.init_app(app)
        end_time = time.perf_counter()
        if app_config.DEBUG:
            logger.info("Loaded %s (%s ms)", short_name, round((end_time - start_time) * 1000, 2))

