import time

import logging

from flask import Flask

# from contexts.wrapper import RecyclableContextVar

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
        # RecyclableContextVar.increment_thread_recycles()
        pass

    # Capture the decorator's return value to avoid pyright reportUnusedFunction
    _ = before_request

    return app

def initialize_extensions(app: Flask):

    from extensions import (
        ext_app_metrics,
        # ext_blueprints,
        ext_command,
        ext_database,
        ext_logging,
        ext_timezone,
        ext_migrate,
    )

    extensions = [
        ext_timezone,
        ext_logging,
        ext_database,
        ext_app_metrics,
        ext_migrate,
        # ext_blueprints,
        ext_command,
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

def create_app() -> Flask:
    start_time = time.perf_counter()
    app = create_flask_app_with_configs()
    initialize_extensions(app=app)
    end_time = time.perf_counter()
    if app_config.DEBUG:
        logger.info("Finished create_app (%s ms)", round((end_time - start_time) * 1000, 2))
    return app

def create_migrations_app():
    app = create_flask_app_with_configs()
    from extensions import ext_database, ext_migrate

    # Initialize only required extensions
    ext_database.init_app(app)
    ext_migrate.init_app(app)

    return app