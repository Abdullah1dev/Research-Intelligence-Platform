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

from app.infrastructure.agent.tools.search_papers import (
    search_papers,
)

from app.infrastructure.llm.chat_model import (
    get_chat_model,
)
from app.infrastructure.agent.context_manager import (
    build_model_context,
)

llm = get_chat_model()

llm_with_tools = llm.bind_tools(
    [
        search_paper,
        search_papers,
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
- When calling search_paper, pass the user's complete question
  as the question argument.
- Preserve the user's wording and intent.
- Do not reduce the question to a keyword or short phrase.
- Do not summarize or rewrite the question before passing it
  to search_paper.
- For paper-library searches, preserve the user's search terms.
- If the user provides an exact paper title or author name,
  pass the exact title or author name to search_papers.
- Do not answer paper-specific questions from your own knowledge.
- For general conversation or unrelated questions, answer
  directly without using a tool.
- After receiving a tool result, use that information to
  provide a clear and accurate answer.
"""


def research_assistant_node(
    state: ResearchAgentState,
):

    recent_messages = build_model_context(
        state["messages"]
    )

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        *recent_messages,
    ]

    print("AVAILABLE TOOLS:")
    print(llm_with_tools.kwargs.get("tools"))

    response = llm_with_tools.invoke(messages)
    
    
    

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
                search_papers,
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