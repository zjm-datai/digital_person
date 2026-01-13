
from typing import Generator, Mapping, Union, Any

from core.graph_apps.gaoxuezhi.app import App
from libs.orjson import orjson_dumps
from models.conversation import MessageRole
from models.model import AppType
from services.message_service import MessageService


class GaoxuezhiAppGenerator:
    
    def __init__(
        self,
    ):
        self.app: App = App()
        
    def generate(
        self, message: str, conversation_id: str, streaming: bool
    ) -> Union[Mapping, Generator[Mapping | str, None, None]]:
        
        return self.app.get_response(
            message=message,
            conversation_id=conversation_id,
            streaming=streaming,
        )
    
    @classmethod
    def convert_to_event_stream(
        cls, generator: Union[Mapping, Generator[Mapping | str, None, None]]
    ) -> Union[Mapping, Generator[Mapping | str, None, None]]:

        if isinstance(generator, dict):
            return generator

        def gen() -> Generator[str, None, None]:
            conversation_id: str = ""
            final_message: str = ""
            current_stage: str = ""
            current_field: str = ""
            message_kind: str = "question"  # summary/question

            try:
                for item in generator:

                    # TODO: to many fucking if else maybe fix it in the future
                    if isinstance(item, Mapping | dict):
                        payload = dict(item)
                        evt = payload.get("event")
                        content = payload.get("content")

                        if isinstance(evt, str):
                            if evt == "ask_end" and isinstance(content, str):
                                final_message = content
                                yield f"data: {orjson_dumps(item)}\n\n"
                            elif evt == "summarize_end" and isinstance(content, str):
                                final_message = content
                                yield f"data: {orjson_dumps(item)}\n\n"
                            elif evt == "message_context":
                                try:
                                    assistant_ctx = (content or {}).get("assistant", {})
                                    if isinstance(assistant_ctx, dict):
                                        conversation_id = assistant_ctx.get("conversation_id", conversation_id) or conversation_id
                                        current_stage = assistant_ctx.get("current_stage", current_stage) or current_stage
                                        current_field = assistant_ctx.get("current_field", current_field) or current_field
                                        message_kind = assistant_ctx.get("message_kind", message_kind) or message_kind
                                except Exception:
                                    raise
                                yield f"data: {orjson_dumps(item)}\n\n"

                            elif evt == "ask_stream" or evt == "summarize_stream":
                                yield f"data: {orjson_dumps(item)}\n\n"

                            else:
                                yield f"data: {orjson_dumps(item)}\n\n"

                            continue
                    else:

                        yield f"event: {item}\n\n"

            finally:
                final_message = (final_message or "").strip()
                if final_message:
                    message_id = MessageService.create_message(
                        conversation_id=conversation_id,
                        app_type=AppType.GAOXUEZHI,
                        message=final_message,
                        role=MessageRole.ASSISTANT,
                        current_stage=current_stage,
                        current_field=current_field,
                        message_kind=message_kind,
                    )
                    message_context = {
                        "event": "message_context",
                        "content": {
                            "message_id": message_id,
                        }
                    }

                yield f"data: {orjson_dumps(message_context)}\n\n"

        return gen()

