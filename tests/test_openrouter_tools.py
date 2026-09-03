from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from app.config.settings import settings


@tool
def search_paper(question: str) -> str:
    """Search the current research paper for information."""
    return "This is a test result from the research paper."


llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2,
)

llm_with_tools = llm.bind_tools(
    [search_paper]
)

response = llm_with_tools.invoke(
    "According to the research paper, what is the main methodology?"
)

print("CONTENT:")
print(response.content)

print("\nTOOL CALLS:")
print(response.tool_calls)