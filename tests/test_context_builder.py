from app.infrastructure.database.config import SessionLocal
from app.infrastructure.embeddings.service import EmbeddingService
from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder
from app.features.users.models import User


db = SessionLocal()

try:

    embedding_service = EmbeddingService()

    vector_search = VectorSearchService(
        embedding_service=embedding_service
    )

    chunks = vector_search.search(
        db=db,
        query="What is this PDF about?",
        top_k=2,
    )

    context_builder = RAGContextBuilder()

    context = context_builder.build_context(chunks)

    print("\n========== RAG CONTEXT ==========\n")
    print(context)
    print("\n=================================\n")

finally:
    db.close()