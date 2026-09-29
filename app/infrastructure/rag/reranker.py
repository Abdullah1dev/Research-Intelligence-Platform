from sentence_transformers import CrossEncoder


class RerankerService:

    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        question: str,
        candidates: list[dict],
        top_k: int = 4,
    ) -> list[dict]:

        if not candidates:
            return []

        # Create question-chunk pairs
        pairs = [
            (
                question,
                candidate["chunk"].content,
            )
            for candidate in candidates
        ]

        # Score ALL candidates
        scores = self.model.predict(pairs)

        reranked = []

        for candidate, score in zip(
            candidates,
            scores,
        ):
            reranked.append(
                {
                    **candidate,
                    "rerank_score": float(score),
                }
            )

        # Highest score first
        reranked.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        # Final context candidates
        return reranked[:top_k]