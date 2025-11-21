
from flask_restx import Resource, reqparse

from controllers.console import console_ns
from controllers.console.wraps import setup_required
from extensions.ext_agents import get_doctor_agent


@console_ns("agent/doctor_agent/chat")
class DoctorAgentChatApi(Resource):
    @setup_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("query", type=str, required=True, location="json")
        parser.add_argument("response_mode", type=str, choices=["blocking", "streaming"], location="json")
        args = parser.parse_args()

        streaming = args["response_mode"] == "blocking"

        try:
            pass
        except Exception as e:
            pass


