from sqlalchemy.orm import Session

from app.features.papers.models import DocumentChunk
from app.infrastructure.embeddings.service import EmbeddingService


class VectorSearchService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
    ):
        self.embedding_service = embedding_service

    def search(
        self,
        db: Session,
        document_id: int,
        query: str,
        top_k: int = 4,
    ) -> list[DocumentChunk]:

        if not query or not query.strip():
            return []

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(
                DocumentChunk.embedding.cosine_distance(
                    query_embedding
                )
            )
            .limit(top_k)
            .all()
        )

        return chunks