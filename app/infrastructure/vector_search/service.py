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

        print("\n========== VECTOR SEARCH ==========")
        print("Document ID:", document_id)
        print("Query:", query)
        print("Top K:", top_k)
        print("Similarity threshold:", similarity_threshold)

        # Generate embedding for the user's query
        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        print(
            "Query embedding dimensions:",
            len(query_embedding),
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

        print(
            "Retrieved candidate chunks:",
            len(results),
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

            print(
                f"Chunk {chunk.chunk_index} "
                f"| Distance: {cosine_distance:.4f} "
                f"| Similarity: {similarity_score:.4f}"
            )

            # Apply similarity threshold
            if similarity_score >= similarity_threshold:

                print(
                    f"  ✓ Accepted chunk "
                    f"{chunk.chunk_index}"
                )

                sources.append(
                    {
                        "chunk": chunk,
                        "similarity_score": round(
                            similarity_score,
                            4,
                        ),
                    }
                )

            else:

                print(
                    f"  ✗ Rejected chunk "
                    f"{chunk.chunk_index}"
                )

        print(
            "Accepted chunks:",
            len(sources),
        )

        print(
            "===================================\n"
        )

        return sources