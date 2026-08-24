from app.infrastructure.embeddings.service import EmbeddingService


def main():

    embedding_service = EmbeddingService()

    text = """
    Retrieval augmented generation combines information retrieval
    with large language models to produce grounded responses.
    """

    embedding = embedding_service.embed_text(text)

    print("Embedding type:", type(embedding))
    print("Embedding dimensions:", len(embedding))
    print("First 10 values:", embedding[:10])


if __name__ == "__main__":
    main()