from sqlalchemy.orm import Session

from app.infrastructure.embeddings.service import EmbeddingService
from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder


class RAGService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_search_service: VectorSearchService,
        context_builder: RAGContextBuilder,
    ):
        self.embedding_service = embedding_service
        self.vector_search_service = vector_search_service
        self.context_builder = context_builder

    def retrieve_context(
        self,
        db: Session,
        document_id: int,
        query: str,
        limit: int = 5,
    ) -> str:

        query_embedding = self.embedding_service.embed_text(
            query
        )

        chunks = self.vector_search_service.search(
            db=db,
            document_id=document_id,
            query_embedding=query_embedding,
            limit=limit,
        )

        context = self.context_builder.build_context(
            chunks
        )

        return context