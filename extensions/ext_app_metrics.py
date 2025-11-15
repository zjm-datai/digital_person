
import json
import os
from flask import Flask, Response

from configs import app_config

def init_app(app: Flask):

    @app.after_request
    def after_request(response):
        """
        Add Version headers to the response.
        """

        response.headers.add("X-Version", app_config.project.version)
        response.headers.add("X-Env", app_config.DEPLOY_ENV)
        return response
    
    @app.route("/health")
    def health():
        return Response(
            json.dumps({
                "pid": os.getpid(),
                "status": "ok",
                "version": app_config.project.version,
            })
        )