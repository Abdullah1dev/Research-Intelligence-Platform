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

        if not query or not query.strip():
            return []

        # 1. Generate embedding for the user's query
        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        # 2. Calculate cosine distance
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # 3. Search the most relevant chunks
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

        sources = []

        # 4. Convert distance to similarity
        for chunk, cosine_distance in results:

            similarity_score = (
                1 - float(cosine_distance)
            )

            # 5. Apply similarity threshold
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