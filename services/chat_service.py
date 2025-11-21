from flask import current_app

from configs import app_config

from core.agents.doctor_agent.agent import DoctorAgent
from core.agents.features.rate_limiting import RateLimit


class DoctorAgentChatService:

    @classmethod
    def chat(
            cls,
            query: str,
            streaming: bool = False,
    ):
        doctor_agent: DoctorAgent = current_app.extensions["doctor_agent"]

        # agent level rate limiter
        max_active_request = app_config.AGENT_MAX_ACTIVE_REQUEST
        rate_limit = RateLimit(max_active_request)
        request_id = RateLimit.gen_request_key()

        try:
            request_id = rate_limit.enter(request_id)
            return rate_limit.generate(
                doctor_agent.get_response(conversation_id, query),
            )
        except Exception as e:
            rate_limit.exit(request_id)
            raise
        finally:
            if not streaming:
                rate_limit.exit(request_id)