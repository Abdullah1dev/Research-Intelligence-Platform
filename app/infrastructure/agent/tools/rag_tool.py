from langchain.tools import tool, ToolRuntime
from sqlalchemy.orm import Session

from app.features.papers.models import (
    Paper,
    PaperDocument,
)

from app.features.papers.enums import (
    DocumentProcessingStatus,
)

from app.infrastructure.rag.dependencies import get_rag_service


@tool
def search_paper(
    question: str,
    runtime: ToolRuntime,
) -> str:

    """
    Search the current research paper using semantic RAG retrieval.

    Use this tool whenever the user asks a question about the
    current research paper, its PDF, its contents, methodology,
    findings, results, authors, datasets, experiments, limitations,
    contributions, or any other information that should be answered
    from the paper.

    Do not use this tool for general conversation or questions that
    are unrelated to the current research paper.
    - When answering paper-specific questions, use only facts
    explicitly supported by the retrieved evidence.
    - Do not infer, speculate, or add general domain knowledge.
    - If the evidence does not support a claim, say that the
    paper does not provide enough information.
    - Do not treat an implication as an explicit statement.
    
    """

    print("\n🔥 SEARCH_PAPER TOOL EXECUTED")
    print("QUESTION:", question)

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

    # 4. Get RAG service
    rag_service = get_rag_service()

    # 5. Retrieve relevant paper information
    result = rag_service.retrieve(
        db=db,
        document_id=document.id,
        question=question,
    )

    # 6. Stop if nothing relevant was found
    if not result["sources"]:
        return (
            "No relevant information was found "
            "in the paper."
        )

    # 7. Return retrieved evidence to the agent
    source_references = "\n".join(
    [
        (
            f"- Chunk {source['chunk_index']} "
            f"(similarity: {source['similarity_score']})"
        )
        for source in result["sources"]
    ]
)

    return (
    "Retrieved evidence from the current paper.\n\n"
    "Use only the information explicitly supported "
    "by this evidence.\n\n"
    f"{result['context']}\n\n"
    f"Source references:\n"
    f"{source_references}"
    
    )