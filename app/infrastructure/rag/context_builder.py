from app.features.papers.models import DocumentChunk


class RAGContextBuilder:

    def build_context(
        self,
        results: list[tuple[DocumentChunk, float]],
    ) -> str:

        if not results:
            return ""

        context_parts = []

        for chunk, similarity_score in results:

            context_parts.append(
                f"""
Source Chunk {chunk.chunk_index}

Content:
{chunk.content}
"""
            )

        return "\n\n".join(context_parts)