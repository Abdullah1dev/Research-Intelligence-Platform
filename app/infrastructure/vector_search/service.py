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
    ) -> list[dict]:

        # Validate query
        if not query or not query.strip():
            return []

        # Generate embedding for the user's query
        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        # Calculate cosine distance
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # Retrieve the top-k nearest chunks
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

        # Convert distance to similarity
        sources = []

        for chunk, cosine_distance in results:

            cosine_distance = float(
                cosine_distance
            )

            similarity_score = (
                1 - cosine_distance
            )

            # Apply similarity threshold
            if similarity_score >= similarity_threshold:

                sources.append(
                    {
                        "chunk": chunk,
                        "similarity_score": round(
                            similarity_score,
                            4,
                        ),
                    }
                )

        return sources