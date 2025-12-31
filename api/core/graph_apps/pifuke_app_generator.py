
from typing import Generator, Mapping, Union

from core.graph_apps.pifuke.app import App
from libs.orjson import orjson_dumps


class PifukeAppGenerator:
    
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
    def convert_to_event_stream(cls, generator: Union[Mapping, Generator[Mapping | str, None, None]]) -> Union[Mapping, Generator[Mapping | str, None, None]]:
        
        if isinstance(generator, dict):
            return generator
        else:
            
            def gen() -> Generator[Mapping | str, None, None]:
                for message in generator:
                    if isinstance(message, Mapping | dict):
                        yield f"data: {orjson_dumps(message)}\n\n"
                    else:
                        yield f"event: {message}\n\n"

            return gen()
        
        