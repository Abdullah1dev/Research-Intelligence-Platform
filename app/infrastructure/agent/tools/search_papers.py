from langchain.tools import tool, ToolRuntime
from sqlalchemy.orm import Session

from app.features.papers.service import search_papers as search_papers_service


@tool
def search_papers(
    query: str,
    runtime: ToolRuntime,
) -> str:
    """
    Search the user's research papers by title or author.

    Use this tool when the user wants to find or discover
    papers from their research library.

    Do not use this tool for questions about the contents
    of a specific paper.
    """

    db: Session = runtime.context.db
    user_id = runtime.state["user_id"]

    papers = search_papers_service(
        db=db,
        user_id=user_id,
        search=query,
        limit=5,
    )

    if not papers:
        return "No matching papers were found."

    results = []

    for paper in papers:
        results.append(
            (
                f"Paper ID: {paper.id}\n"
                f"Title: {paper.title}\n"
                f"Authors: {paper.authors}\n"
                f"Publication Year: {paper.publication_year}\n"
                f"Journal: {paper.journal}\n"
                f"Category: {paper.category}\n"
                f"DOI: {paper.doi}"
            )
        )

    return "\n\n".join(results)