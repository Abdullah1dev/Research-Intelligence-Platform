# app/infrastructure/rag/dependencies.py

from app.infrastructure.embeddings.service import EmbeddingService
from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder
from app.infrastructure.rag.service import RAGService
from app.infrastructure.llm.service import LLMService


embedding_service = EmbeddingService()

vector_search_service = VectorSearchService(
    embedding_service=embedding_service,
)

context_builder = RAGContextBuilder()

llm_service = LLMService()

rag_service = RAGService(
    vector_search_service=vector_search_service,
    context_builder=context_builder,
    llm_service=llm_service,
)


def get_rag_service() -> RAGService:
    return rag_service