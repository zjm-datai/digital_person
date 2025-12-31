

from flask import Flask

from celery import Task, Celery
import pytz

from configs import app_config

def init_app(app: Flask):
    
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)
            
    broker_transport_options = {}
    
    celery_app = Celery(
        app.name,
        task_cls=FlaskTask,
        broker=app_config.CELERY_BROKER_URL,
        backend=app_config.CELERY_BACKEND,
    )
    
    celery_app.conf.update(
        result_backend=app_config.CELERY_RESULT_BACKEND,
        broker_transport_options=broker_transport_options,
        broker_connection_retry_on_startup=True,
        worker_log_format=app_config.LOG_FORMAT,
        worker_task_log_format=app_config.LOG_FORMAT,
        worker_hijack_root_logger=False,
        timezone=pytz.timezone(app_config.LOG_TZ or "UTC"),
        task_ignore_result=True
    )
    
    if app_config.LOG_FILE:
        celery_app.conf.update(
            worker_log_file=app_config.LOG_FILE,
        )
    
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    
    imports = [
        "tasks.llm_run_log_tasks"
    ]
    
    celery_app.conf.update(imports=imports)
    
    return celery_app