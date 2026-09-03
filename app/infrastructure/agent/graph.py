from langgraph.graph import (
    StateGraph,
    START,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from app.infrastructure.agent.state import (
    ResearchAgentState,
)

from app.infrastructure.agent.context import (
    ResearchAgentContext,
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

    print("========== AVAILABLE TOOLS ==========")
    print(
        llm_with_tools.kwargs.get("tools")
    )
    print("======================================")

    response = llm_with_tools.invoke(
        state["messages"]
    )

    print("========== AGENT RESPONSE ==========")
    print("Content:", response.content)
    print("Tool calls:", response.tool_calls)
    print("====================================")

    return {
        "messages": [response]
    }


def build_research_agent(
    checkpointer,
):

    graph = StateGraph(
        ResearchAgentState,
        context_schema=ResearchAgentContext,
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