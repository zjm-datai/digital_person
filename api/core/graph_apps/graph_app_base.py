


from typing import Any

from abc import ABC, abstractmethod


class GraphApp(ABC):
    
    @abstractmethod
    def get_response(
        self, message: str, conversation_id: str, streaming: bool
    ) -> Any:
        raise NotImplementedError("Subclasses must implement get_response method")