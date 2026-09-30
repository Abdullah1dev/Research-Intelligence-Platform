from app.features.users.models import User
from app.features.papers.models import Paper, PaperDocument, DocumentChunk
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.rag.dependencies import get_rag_service


def main():
    db = SessionLocal()

    try:
        rag_service = get_rag_service()

        question = "What is supervised learning?"
        document_id = 30

        result = rag_service.ask(
            db=db,
            document_id=document_id,
            question=question,
            retrieval_top_k=10,
            rerank_top_k=4,
            similarity_threshold=0.5,
        )

        print("\n" + "=" * 70)
        print("QUESTION")
        print("=" * 70)
        print(question)

        print("\n" + "=" * 70)
        print("GENERATED ANSWER")
        print("=" * 70)
        print(result["answer"])

        print("\n" + "=" * 70)
        print("RETRIEVED CONTEXT")
        print("=" * 70)

        for source in result["sources"]:
            print(f"\n--- Chunk {source.chunk_id} ---")
            print(source.content)

    finally:
        db.close()


if __name__ == "__main__":
    main()