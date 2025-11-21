

from flask import Flask

from configs import app_config

def init_app(
    app: Flask
):
    # register blueprint routers

    from flask_cors import CORS

    from controllers.console import bp as console_app_bp

    CORS(
        console_app_bp,
        resources={
            r"/*": {
                "origins": app_config.CONSOLE_CORS_ALLOW_ORIGINS
            }
        },
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"],
        expose_headers=["X-Version", "X-Env"],
    )

    app.register_blueprint(console_app_bp)

