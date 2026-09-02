from typing import Annotated

from langchain_core.messages import AnyMessage

from langgraph.graph.message import add_messages

from typing_extensions import TypedDict


class ResearchAgentState(TypedDict):

    messages: Annotated[
        list[AnyMessage],
        add_messages,
    ]

    conversation_id: int

    user_id: int

    paper_id: int