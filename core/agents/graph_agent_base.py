import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, AsyncGenerator

from psycopg_pool import ConnectionPool

from langchain_openai import ChatOpenAI
from langgraph.graph.state import CompiledStateGraph

from configs import app_config

logger = logging.getLogger(__name__)

class GraphAgent(ABC):

    def __init__(
        self,
        connection_pool: Optional[ConnectionPool] = None    
    ):

        self.llm = ChatOpenAI(
            model=app_config.LLM_MODEL,
            temperature=app_config.LLM_TEMPERATURE,
            api_key=app_config.LLM_API_KEY,
            base_url=app_config.LLM_LOCAL_URL
        )
        self._graph: Optional[CompiledStateGraph] = None
        self._connection_pool: Optional[ConnectionPool] = connection_pool

    def _get_model_kwargs(self) -> Dict[str, Any]:
        return {}
    
    def _get_connection_pool(self) -> Optional[ConnectionPool]:

        if self._connection_pool is not None:
            return self._connection_pool
        
        try:
            max_size = app_config.DATABASE_POOL_SIZE
            self._connection_pool = ConnectionPool(
                conninfo=app_config.DATABASE_URL,
                max_size=max_size,
                kwargs={
                    "autocommit": True,
                    "connect_timeout": 60,
                    "prepare_threshold": None,
                },
            )
        except Exception as e:
            logger.exception("Init ConnectionPool failed.", exc_info=e)

            raise e

    @abstractmethod
    async def create_graph(self) -> Any:
        """Construct and compile the workflow graph."""

        raise NotImplementedError("Subclasses must implement create_graph method")
    
    @abstractmethod
    async def get_response(self, messages, chat_session_id):
        pass

    @abstractmethod
    async def get_stream_response(self, messages, chat_session_id) -> AsyncGenerator[Any, None]:
        raise NotImplementedError("Subclasses must implement get_stream_response method")
    
