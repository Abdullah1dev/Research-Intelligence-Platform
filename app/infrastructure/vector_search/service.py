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

        print("\n========== VECTOR SEARCH START ==========")
        print(f"Document ID: {document_id}")
        print(f"Query: {query}")
        print(f"Top K: {top_k}")
        print(f"Similarity Threshold: {similarity_threshold}")
        print("=========================================")

        # 1. Validate query
        if not query or not query.strip():
            print("Empty query received.")
            return []

        # 2. Generate embedding for the user's query
        print("\nGenerating query embedding...")

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        print(
            f"Query embedding dimensions: "
            f"{len(query_embedding)}"
        )

        # 3. Calculate cosine distance
        distance = (
            DocumentChunk.embedding.cosine_distance(
                query_embedding
            )
        )

        # 4. Retrieve the top-k nearest chunks
        print("\nSearching PostgreSQL / pgvector...")

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
            f"Retrieved {len(results)} candidate chunks."
        )

        # 5. Convert distance to similarity
        sources = []

        print("\n========== SIMILARITY SCORES ==========")

        for chunk, cosine_distance in results:

            cosine_distance = float(
                cosine_distance
            )

            similarity_score = (
                1 - cosine_distance
            )

            print(
                f"Chunk {chunk.chunk_index} | "
                f"Distance: {cosine_distance:.4f} | "
                f"Similarity: {similarity_score:.4f} | "
                f"Accepted: "
                f"{similarity_score >= similarity_threshold}"
            )

            # 6. Apply similarity threshold
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

        print("=========================================")

        print(
            f"Accepted {len(sources)} "
            f"chunks after threshold filtering."
        )

        print("========== VECTOR SEARCH END ==========\n")

        return sources