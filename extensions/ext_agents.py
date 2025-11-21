import logging

from flask import Flask, current_app

from core.agents.doctor_agent.agent import DoctorAgent

logger = logging.getLogger(__name__)

def init_app(app: Flask):

    if "doctor_agent" in app.extensions:
        return

    try:
        doctor_agent_instance = DoctorAgent(
            # TODO
            connection_pool=connection_pool,
        )
        app.extensions["doctor_agent"] = doctor_agent_instance

    except Exception as e:
        logger.error("Failed to initialize DoctorAgent: %s", str(e))
        raise

def get_doctor_agent() -> DoctorAgent:
    return current_app.extensions["doctor_agent"]