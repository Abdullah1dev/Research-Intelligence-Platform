from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from app.infrastructure.agent.state import (
    ResearchAgentState,
)

from app.infrastructure.agent.tools.rag_tool import (
    search_paper,
)

from app.infrastructure.llm.chat_model import (
    get_chat_model,
)


llm = get_chat_model()

llm_with_tools = llm.bind_tools(
    [search_paper]
)


def research_assistant_node(
    state: ResearchAgentState,
):

    response = llm_with_tools.invoke(
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

    # Assistant
    graph.add_node(
        "research_assistant",
        research_assistant_node,
    )

    # Tools
    graph.add_node(
        "tools",
        ToolNode(
            [search_paper]
        ),
    )

    # Start
    graph.add_edge(
        START,
        "research_assistant",
    )

    # Decide whether tool is required
    graph.add_conditional_edges(
        "research_assistant",
        tools_condition,
    )

    # Tool result goes back to LLM
    graph.add_edge(
        "tools",
        "research_assistant",
    )

    return graph.compile(
        checkpointer=checkpointer,
    )