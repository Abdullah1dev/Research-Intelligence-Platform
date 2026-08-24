from app.infrastructure.document_processing.chunker import DocumentChunker


def main():
    text = """
    Artificial intelligence has changed modern research.
    Researchers increasingly use machine learning to analyze
    large datasets and discover patterns.

    Transformer architectures have become important in natural
    language processing and multimodal learning.

    Retrieval augmented generation combines retrieval systems
    with large language models to improve factual responses.
    """

    chunker = DocumentChunker(
        chunk_size=200,
        chunk_overlap=50,
    )

    chunks = chunker.split_text(text)

    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks, start=1):
        print(f"\n--- Chunk {i} ---")
        print(chunk)


if __name__ == "__main__":
    main()