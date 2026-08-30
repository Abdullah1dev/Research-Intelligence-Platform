from app.infrastructure.database.config import SessionLocal

from app.features.papers.models import (
    PaperDocument,
)

from app.infrastructure.embeddings.service import (
    EmbeddingService,
)

from app.infrastructure.vector_search.service import (
    VectorSearchService,
)

from app.infrastructure.rag.context_builder import (
    RAGContextBuilder,
)

from app.infrastructure.llm.service import (
    LLMService,
)

from app.infrastructure.rag.service import (
    RAGService,
)
from app.features.papers.enums import (
    DocumentProcessingStatus,
)
from app.features.users.models import User


def test_rag():

    db = SessionLocal()

    try:

        # Get an existing document
        document = (
            db.query(PaperDocument)
            .filter(
                PaperDocument.processing_status
                == DocumentProcessingStatus.COMPLETED
            )
            .first()
        )

        if not document:
            print("No completed document found.")
            return

        print(
            f"\nUsing document: {document.file_name}"
        )

        print(
            f"Document ID: {document.id}"
        )

        # Initialize services
        embedding_service = EmbeddingService()

        vector_search_service = (
            VectorSearchService(
                embedding_service=embedding_service
            )
        )

        context_builder = RAGContextBuilder()

        llm_service = LLMService()

        rag_service = RAGService(
            vector_search_service=vector_search_service,
            context_builder=context_builder,
            llm_service=llm_service,
        )

        # Ask question
        question = (
            "What is this document about?"
        )

        print("\nQUESTION:")
        print(question)

        print("\nSearching document...\n")

        # Run complete RAG pipeline
        answer = rag_service.ask(
            db=db,
            document_id=document.id,
            question=question,
        )

        print("\nFINAL ANSWER:")
        print(answer)

    finally:

        db.close()


if __name__ == "__main__":
    test_rag()