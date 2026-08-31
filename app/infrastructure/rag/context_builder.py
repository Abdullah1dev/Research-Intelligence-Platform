from app.features.papers.models import DocumentChunk


class RAGContextBuilder:

    def build_context(
        self,
        chunks,
    ) -> str:

        if not chunks:
            return ""

        context_parts = []

        for chunk in chunks:

            context_parts.append(
                f"[Chunk {chunk.chunk_index}]\n"
                f"{chunk.content}"
            )

        return "\n\n".join(context_parts)