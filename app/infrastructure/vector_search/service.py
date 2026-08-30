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
        similarity_threshold: float = 0.5,
    ) -> list[tuple[DocumentChunk, float]]:

        if not query or not query.strip():
            return []

        # 1. Generate embedding for the query
        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        # 2. Calculate cosine distance
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # 3. Search chunks and retrieve distance
        results = (
            db.query(
                DocumentChunk,
                distance.label("distance"),
            )
            .filter(
                DocumentChunk.document_id == document_id
            )
            .order_by(distance)
            .limit(top_k)
            .all()
        )

        relevant_results = []

        # 4. Convert distance to similarity
        for chunk, distance_value in results:

            similarity_score = 1 - distance_value

            # 5. Apply relevance threshold
            if similarity_score >= similarity_threshold:
                relevant_results.append(
                    (chunk, similarity_score)
                )

        return relevant_results