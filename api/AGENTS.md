(llm_eng_system) 
28361@WorkerZjm MINGW64 /c/Desktop/project/pro_backend/clip_vector_system (main)
$ ll extensions/
total 40
-rw-r--r-- 1 28361 197609    0 Dec 25 17:01 __init__.py
drwxr-xr-x 1 28361 197609    0 Dec 29 14:22 __pycache__/
-rw-r--r-- 1 28361 197609 2170 Dec 29 09:12 ext_app_metrics.py
-rw-r--r-- 1 28361 197609  938 Dec 29 09:12 ext_blueprints.py
-rw-r--r-- 1 28361 197609 1361 Dec 29 09:12 ext_celery.py
-rw-r--r-- 1 28361 197609  184 Dec 29 09:12 ext_commands.py
-rw-r--r-- 1 28361 197609  170 Dec 26 17:39 ext_database.py
-rw-r--r-- 1 28361 197609   62 Dec 29 09:12 ext_import_modules.py
-rw-r--r-- 1 28361 197609 2908 Dec 29 09:12 ext_logging.py
-rw-r--r-- 1 28361 197609  676 Dec 29 09:12 ext_login.py
-rw-r--r-- 1 28361 197609  178 Dec 29 14:13 ext_migrate.py
-rw-r--r-- 1 28361 197609  137 Dec 29 09:12 ext_orjson.py
-rw-r--r-- 1 28361 197609   66 Dec 29 09:12 ext_request_logging.py
-rw-r--r-- 1 28361 197609 2272 Dec 26 18:10 ext_storage.py
-rw-r--r-- 1 28361 197609  164 Dec 26 11:26 ext_timezone.py
-rw-r--r-- 1 28361 197609  131 Dec 29 09:12 ext_warnings.py
drwxr-xr-x 1 28361 197609    0 Dec 26 14:12 storage/


import time
import logging
from flask import Flask

from configs import app_config
from contexts.wrapper import RecyclableContextVar

logger = logging.getLogger(__name__)

def create_flask_app_with_configs() -> Flask:
    """ 
    create a raw flask app
    with configs loaded from .env file
    """
    
    app = Flask(__name__)
    app.config.from_mapping(app_config.model_dump())
    
    # add before request hook
    @app.before_request
    def before_request():
        # add an unique identifier to each request
        RecyclableContextVar.increment_thread_recycles()
        
    _ = before_request
    
    return app
    
def create_app() -> Flask:
    
    start_time = time.perf_counter()
    app = create_flask_app_with_configs()
    initialize_extensions(app)
    end_time = time.perf_counter()
    if app_config.DEBUG:
        logger.info("Finished create_app (%s ms)", round((end_time - start_time) * 1000, 2))
    
    return app

def initialize_extensions(app: Flask) -> None:
    from extensions import (
        ext_timezone,
        ext_logging,
        ext_warnings,
        ext_import_modules,
        ext_migrate,
        ext_orjson,
        ext_database,
        ext_app_metrics,
        ext_celery,
        ext_login,
        ext_blueprints,
        ext_commands,
        ext_request_logging,
    )
    
    extensions = [
        ext_timezone,
        ext_logging,
        ext_warnings,
        ext_import_modules,
        ext_migrate,
        ext_orjson,
        ext_database,
        ext_app_metrics,
        ext_celery,
        # ext_login,
        ext_blueprints,
        ext_commands,
        ext_request_logging,  
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
            logger.info(
                "Loaded %s (%s ms)", 
                short_name, round((end_time - start_time) * 1000, 2)
            )


