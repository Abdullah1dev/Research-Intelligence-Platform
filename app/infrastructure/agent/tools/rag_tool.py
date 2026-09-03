from langchain.tools import tool, ToolRuntime
from sqlalchemy.orm import Session

from app.features.papers.models import (
    Paper,
    PaperDocument,
)

from app.features.papers.enums import (
    DocumentProcessingStatus,
)

from app.infrastructure.rag.service import RAGService
from app.infrastructure.rag.dependencies import get_rag_service



@tool
def search_paper(
    question: str,
    runtime: ToolRuntime,
) -> str:
    """
    Search the current research paper and retrieve
    relevant information to answer the user's question.
    """

    db: Session = runtime.context.db

    paper_id = runtime.state["paper_id"]
    user_id = runtime.state["user_id"]

    # 1. Verify paper ownership
    paper = (
        db.query(Paper)
        .filter(
            Paper.id == paper_id,
            Paper.owner_id == user_id,
        )
        .first()
    )

    if not paper:
        return "Paper not found."

    # 2. Find paper document
    document = (
        db.query(PaperDocument)
        .filter(
            PaperDocument.paper_id == paper.id,
        )
        .first()
    )

    if not document:
        return "No document is available for this paper."

    # 3. Make sure processing is complete
    if (
        document.processing_status
        != DocumentProcessingStatus.COMPLETED
    ):
        return (
            "The paper document is not ready yet. "
            f"Current status: {document.processing_status}"
        )

    # 4. Get existing RAG service
    rag_service = get_rag_service()

    # 5. Run existing RAG pipeline
    result = rag_service.ask(
        db=db,
        document_id=document.id,
        question=question,
    )

    # 6. Return information to the agent
    if not result["sources"]:
        return (
            "No relevant information was found "
            "in the paper."
        )

    return (
        f"Answer from the paper:\n"
        f"{result['answer']}\n\n"
        f"Sources:\n"
        + "\n\n".join(
            [
                (
                    f"Chunk {source['chunk_index']} "
                    f"(similarity: "
                    f"{source['similarity_score']}):\n"
                    f"{source['content']}"
                )
                for source in result["sources"]
            ]
        )
    )