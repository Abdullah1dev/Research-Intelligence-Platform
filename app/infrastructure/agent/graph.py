from langchain_core.messages import AIMessage

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.infrastructure.agent.state import (
    ResearchAgentState,
)

from app.infrastructure.llm.chat_model import (
    get_chat_model,
)


# Create the chat model
llm = get_chat_model()


def research_assistant_node(
    state: ResearchAgentState,
):

    response = llm.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


def build_research_agent(
    checkpointer,
):

    graph = StateGraph(
        ResearchAgentState
    )

    graph.add_node(
        "research_assistant",
        research_assistant_node,
    )

    graph.add_edge(
        START,
        "research_assistant",
    )

    graph.add_edge(
        "research_assistant",
        END,
    )

    return graph.compile(
        checkpointer=checkpointer,
    )