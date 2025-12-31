

from enum import StrEnum

from core.graph_apps.pifuke_app_generator import PifukeAppGenerator

class AppType(StrEnum):
    
    PIFUKE = "pifuke"


class AppGenerateService:
    
    @staticmethod
    def generate(
        app_type: str, conversation_id: str, message: str, streaming: bool = False
    ):
        try:
            if app_type == AppType.PIFUKE:
                return PifukeAppGenerator.convert_to_event_stream(
                    PifukeAppGenerator().generate(message, conversation_id, streaming)
                )
            else:
                raise ValueError(f"Unsupported app_type: {app_type}")
        except Exception as e:
            raise 
        finally:
            pass