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

    # Send conversation messages to the LLM
    response = llm.invoke(
        state["messages"]
    )

    # Return the new AI message
    return {
        "messages": [
            AIMessage(
                content=response.content
            )
        ]
    }


def build_research_agent():

    # Create graph
    graph = StateGraph(
        ResearchAgentState
    )

    # Add node
    graph.add_node(
        "research_assistant",
        research_assistant_node,
    )

    # Define graph flow
    graph.add_edge(
        START,
        "research_assistant",
    )

    graph.add_edge(
        "research_assistant",
        END,
    )

    return graph