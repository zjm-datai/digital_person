
from typing import Any, Dict, Generator, Mapping, Union, Optional

from langchain_core.messages import AIMessageChunk
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.checkpoint.postgres import PostgresSaver


from core.graph_apps.graph_app_base import GraphApp
from extensions.ext_apps_database import init_connection_pool
  

from .state import State
from .nodes.utils import progress_counts
from .nodes import InitNode, AskNode, SummaryNode, ProcessNode

class App(GraphApp):
    
    def __init__(
        self,
    ):
        self.graph: CompiledStateGraph = self._create_graph()
        self.checkpointer = None
    
    def _create_graph(self) -> CompiledStateGraph:
        graph = StateGraph(State)
        
        graph.add_node("init", self._init)
        graph.add_node("process", self._process)
        graph.add_node("ask", self._ask)
        graph.add_node("summarize", self._summarize)
        
        graph.set_entry_point("init")
        graph.add_edge("init", "process")
        
        graph.add_conditional_edges(
            "process",
            lambda s: "summarize" if s.all_done else "ask",
            {
                "ask": "ask",
                "summarize": "summarize"
            }
        )

        graph.add_edge("ask", END)
        graph.add_edge("summarize", END)
        
        db_pool = init_connection_pool()
        
        self.checkpointer = PostgresSaver(db_pool) # type: ignore
        self.checkpointer.setup()
        
        return graph.compile(checkpointer=self.checkpointer)
    
    def _init(self, state: State):
        return InitNode.run(state)
        
    def _process(self, state: State):
        return ProcessNode.run(state)
    
    def _ask(self, state: State):
        return AskNode.run(state)
    
    def _summarize(self, state: State):
        return SummaryNode.run(state)
        
        
    def get_response(
        self, message: str, conversation_id: str, streaming: bool
    ) -> Union[Mapping, Generator[Mapping | str, None, None]]:

        if self.graph is None:
            self.graph = self._create_graph()

        config: RunnableConfig = {
            "configurable": {"thread_id": conversation_id}
        }

        input = {
            "messages": message, "session_id": conversation_id,
        }

        if not streaming:
            # TODO: have problem
            result = self.graph.invoke(input=input, config=config)
            
            return result

        def stream_generator() -> Generator[Dict[str, Any], None, None]:
            last_end_state: Optional[Any] = None
            is_summary = False

            for mode, chunk in self.graph.stream(
                input, config, stream_mode=["messages", "values"]
            ):
                if mode == "messages":
                    if isinstance(chunk, tuple):
                        msg, meta = chunk
                        if hasattr(msg, "content"):
                            node = meta.get("langgraph_node", "")
                            content = msg.content
                            if not content:
                                continue
                            if node == "ask":
                                yield {"event": "stream_output", "content": content}
                            elif node == "summarize":
                                is_summary = True
                                yield {"event": "summarize", "content": content}
                    elif hasattr(chunk, "content"):
                        content = chunk.content
                        if content:
                            yield {"event": "stream_output", "content": content}
                elif mode == "values":
                    last_end_state = chunk

            if last_end_state:

                if isinstance(last_end_state, dict):
                    current_stage = last_end_state.get("current_stage")
                    current_missing_field = last_end_state.get("current_missing_field")
                    progress = last_end_state.get("progress", None)
                else:
                    current_stage = getattr(last_end_state, "current_stage", None)
                    current_missing_field = getattr(last_end_state, "current_missing_field", None)
                    progress = progress_counts(last_end_state)

                yield {
                    "event": "message_context",
                    "content": {
                        "assistant": {
                            "message_kind": "summary" if is_summary else "question",
                            "target_stage": current_stage,
                            "target_field": current_missing_field,
                            "progress": progress,
                        },
                        "user": {
                            "message_kind": "answer",
                            "target_stage": getattr(last_end_state, "last_asked_stage", None)
                                        if not isinstance(last_end_state, dict)
                                        else last_end_state.get("last_asked_stage"),
                            "target_field": getattr(last_end_state, "last_asked_field", None)
                                        if not isinstance(last_end_state, dict)
                                        else last_end_state.get("last_asked_field"),
                        },
                    },
                }

                yield {
                    "event": "is_end", 
                    "content": getattr(last_end_state, "all_done", None) 
                    if not isinstance(last_end_state, dict) 
                    else last_end_state.get("all_done")
                }
        
        return stream_generator()