from langchain_core.messages import SystemMessage

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


SYSTEM_PROMPT = """
You are a research assistant.

You are helping the user understand the research paper
associated with the current conversation.

Whenever the user asks a question that requires information
from the research paper, its PDF, its contents, methodology,
findings, results, authors, datasets, experiments, limitations,
or contributions, you MUST use the search_paper tool.

Do not answer paper-specific questions from your own knowledge.

For general conversation or questions unrelated to the paper,
you may answer directly without using the tool.

After receiving the tool result, use that information to provide
a clear and accurate answer to the user.
"""


def research_assistant_node(
    state: ResearchAgentState,
):

    print("========== AVAILABLE TOOLS ==========")
    print(
        llm_with_tools.kwargs.get("tools")
    )
    print("======================================")

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(
        messages
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

    graph.add_node(
        "research_assistant",
        research_assistant_node,
    )

    graph.add_node(
        "tools",
        ToolNode(
            [search_paper]
        ),
    )

    graph.add_edge(
        START,
        "research_assistant",
    )

    graph.add_conditional_edges(
        "research_assistant",
        tools_condition,
    )

    graph.add_edge(
        "tools",
        "research_assistant",
    )

    return graph.compile(
        checkpointer=checkpointer,
    )