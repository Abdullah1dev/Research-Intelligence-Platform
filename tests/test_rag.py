from app.infrastructure.database.config import SessionLocal
from app.infrastructure.rag.dependencies import get_rag_service


def main():

    db = SessionLocal()

    try:

        rag_service = get_rag_service()

        document_id = 12  # CHANGE THIS

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