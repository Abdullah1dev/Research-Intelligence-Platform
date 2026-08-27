from app.features.users.models import User
from app.features.papers.models import DocumentChunk

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.embeddings.service import EmbeddingService
from app.infrastructure.vector_search.service import VectorSearchService


db = SessionLocal()

try:

    embedding_service = EmbeddingService()

    vector_search = VectorSearchService(
        embedding_service=embedding_service
    )

    results = vector_search.search(
        db=db,
        query="What is this PDF about?",
        top_k=2,
    )

    print("\n========== SEARCH RESULTS ==========\n")

    for result in results:

        print(
            f"Chunk index: {result.chunk_index}"
        )

        print(
            f"Content:\n{result.content[:500]}"
        )

        print(
            "\n-----------------------------------\n"
        )

finally:
    db.close()