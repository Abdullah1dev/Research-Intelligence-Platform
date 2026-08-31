from app.features.papers.models import DocumentChunk


class RAGContextBuilder:

    def __init__(
        self,
        max_context_characters: int = 6000,
    ):
        self.max_context_characters = (
            max_context_characters
        )

    def build_context(
        self,
        chunks: list[DocumentChunk],
    ) -> str:

        if not chunks:
            return ""

        context_parts = []
        current_length = 0

        for chunk in chunks:

            chunk_text = (
                f"[Chunk {chunk.chunk_index}]\n"
                f"{chunk.content}\n\n"
            )

            # Stop before exceeding the context limit
            if (
                current_length + len(chunk_text)
                > self.max_context_characters
            ):
                break

            context_parts.append(chunk_text)

            current_length += len(chunk_text)

        return "".join(context_parts)