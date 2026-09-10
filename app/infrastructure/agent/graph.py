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

from app.infrastructure.agent.tools.rag_tool import search_paper
from app.infrastructure.agent.tools.search_papers import search_papers


llm = get_chat_model()

llm_with_tools = llm.bind_tools(
    [
    search_paper,
    search_papers
    
    ]
    
)


SYSTEM_PROMPT = """
You are a research assistant.

You help the user work with their research paper library
and understand the research paper associated with the
current conversation.

You have access to two tools:

1. search_papers
Use this tool when the user wants to find, discover, or
locate papers in their research library.

Examples:
- Find my papers about artificial intelligence.
- Find papers by Andrew Ng.
- Do I have a paper about transformers?
- Find my paper called Attention Is All You Need.

2. search_paper
Use this tool when the user asks about the contents
of the current research paper.

Examples:
- What methodology does this paper use?
- What are the main findings?
- What dataset was used?
- What are the limitations?
- Summarize the paper.
- What experiments were performed?

Important rules:

- For paper-library searches, use search_papers.
- For questions about the contents of the current paper,
  use search_paper.
- Do not answer paper-specific questions from your own knowledge.
- For general conversation or unrelated questions, answer
  directly without using a tool.
- After receiving a tool result, use that information to
  provide a clear and accurate answer.
"""



def research_assistant_node(
    state: ResearchAgentState,
):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)
    print("MODEL RESPONSE:")
    print(response)

    print("TOOL CALLS:")
    print(response.tool_calls)
    
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
            [
            search_paper,
            search_papers
        ]
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