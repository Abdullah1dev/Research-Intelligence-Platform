from app.infrastructure.database.config import SessionLocal
from app.infrastructure.rag.dependencies import get_rag_service
from app.features.users.models import User


from app.features.papers.models import (
    Paper,
    PaperDocument,
    DocumentChunk,
)

from app.features.conversations.models import Conversation


def main():

    db = SessionLocal()

    try:

        rag_service = get_rag_service()

        document_id = 22

        result = rag_service.ask(
            db=db,
            document_id=document_id,
            question="What is the main methodology used in this paper?",
        )

        print("\n========== ANSWER ==========")
        print(result["answer"])

        print("\n========== SOURCES ==========")

        for source in result["sources"]:

            print(
                f"\nChunk ID: {source['chunk_id']}"
            )

            print(
                f"Chunk Index: {source['chunk_index']}"
            )

            print(
                f"Similarity: {source['similarity_score']}"
            )

            print(
                source["content"][:500]
            )

    finally:

        db.close()


if __name__ == "__main__":
    main()