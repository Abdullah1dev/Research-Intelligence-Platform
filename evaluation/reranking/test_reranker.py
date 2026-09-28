import json
from pathlib import Path

from sentence_transformers import CrossEncoder

from app.features.users.models import User
from app.features.papers.models import (
    Paper,
    PaperDocument,
    DocumentChunk,
)
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BASELINE_PATH = (
    BASE_DIR
    / "results"
    / "retrieval_baseline_top5.json"
)

RERANKED_RESULTS_PATH = (
    BASE_DIR
    / "results"
    / "retrieval_reranked_top5.json"
)


# ============================================================
# LOAD BASELINE RESULTS
# ============================================================

with open(
    BASELINE_PATH,
    "r",
    encoding="utf-8",
) as file:

    baseline_results = json.load(file)


# ============================================================
# LOAD RERANKER
# ============================================================

print("\n====================================")
print("Loading reranker...")
print("====================================")

reranker = CrossEncoder(
    "BAAI/bge-reranker-base"
)

print("Reranker loaded successfully.")


# ============================================================
# DATABASE
# ============================================================

db = SessionLocal()

reranked_results = []


try:

    # ========================================================
    # PROCESS EACH QUESTION
    # ========================================================

    for result in baseline_results:

        question_id = result["question_id"]
        question = result["question"]

        retrieved_sources = result[
            "retrieved_sources"
        ]


        print("\n====================================")
        print("Question:", question_id)
        print("Text:", question)
        print("====================================")


        # ----------------------------------------------------
        # Check whether vector search returned candidates
        # ----------------------------------------------------

        if not retrieved_sources:

            print("No candidates retrieved.")
            print("Skipping reranking.")

            reranked_results.append(
                {
                    "question_id": question_id,
                    "question": question,
                    "document_id": result[
                        "document_id"
                    ],
                    "expected_chunk_indexes": result[
                        "expected_chunk_indexes"
                    ],
                    "retrieved_chunk_indexes": [],
                    "retrieved_sources": [],
                    "retrieval_latency_ms": result[
                        "retrieval_latency_ms"
                    ],
                    "reranking_latency_ms": 0.0,
                }
            )

            continue


        # ----------------------------------------------------
        # Get chunk IDs from baseline results
        # ----------------------------------------------------

        chunk_ids = [
            source["chunk_id"]
            for source in retrieved_sources
        ]


        # ----------------------------------------------------
        # Fetch all chunks in ONE database query
        # ----------------------------------------------------

        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.id.in_(chunk_ids)
            )
            .all()
        )


        # ----------------------------------------------------
        # Create lookup dictionary
        # ----------------------------------------------------

        chunks_by_id = {
            chunk.id: chunk
            for chunk in chunks
        }


        # ----------------------------------------------------
        # Build query-document pairs
        # ----------------------------------------------------

        pairs = []
        valid_sources = []

        for source in retrieved_sources:

            chunk = chunks_by_id.get(
                source["chunk_id"]
            )

            if chunk is None:

                print(
                    "Warning: chunk not found:",
                    source["chunk_id"],
                )

                continue


            pairs.append(
                [
                    question,
                    chunk.content,
                ]
            )

            valid_sources.append(source)


        # ----------------------------------------------------
        # Check whether valid pairs exist
        # ----------------------------------------------------

        if not pairs:

            print(
                "No valid question-chunk pairs."
            )

            reranked_results.append(
                {
                    "question_id": question_id,
                    "question": question,
                    "document_id": result[
                        "document_id"
                    ],
                    "expected_chunk_indexes": result[
                        "expected_chunk_indexes"
                    ],
                    "retrieved_chunk_indexes": [],
                    "retrieved_sources": [],
                    "retrieval_latency_ms": result[
                        "retrieval_latency_ms"
                    ],
                    "reranking_latency_ms": 0.0,
                }
            )

            continue


        # ====================================================
        # ORIGINAL VECTOR RANKING
        # ====================================================

        print("\nOriginal vector ranking:")

        for rank, source in enumerate(
            valid_sources,
            start=1,
        ):

            print(
                f"{rank}. "
                f"Chunk {source['chunk_index']} "
                f"| Vector similarity: "
                f"{source['similarity_score']:.4f}"
            )


        # ====================================================
        # RERANK
        # ====================================================

        import time

        rerank_start = time.perf_counter()

        scores = reranker.predict(
            pairs
        )

        rerank_end = time.perf_counter()

        reranking_latency_ms = (
            rerank_end - rerank_start
        ) * 1000


        # ====================================================
        # BUILD RERANKED RESULTS
        # ====================================================

        reranked = []

        for source, score in zip(
            valid_sources,
            scores,
        ):

            reranked.append(
                {
                    "chunk_index": source[
                        "chunk_index"
                    ],
                    "chunk_id": source[
                        "chunk_id"
                    ],
                    "similarity_score": source[
                        "similarity_score"
                    ],
                    "rerank_score": float(
                        score
                    ),
                }
            )


        # ----------------------------------------------------
        # Sort by reranker score
        # ----------------------------------------------------

        reranked.sort(
            key=lambda item: item[
                "rerank_score"
            ],
            reverse=True,
        )


        # ====================================================
        # STORE RERANKED RESULT
        # ====================================================

        reranked_results.append(
            {
                "question_id": question_id,
                "question": question,
                "document_id": result[
                    "document_id"
                ],
                "expected_chunk_indexes": result[
                    "expected_chunk_indexes"
                ],
                "retrieved_chunk_indexes": [
                    item["chunk_index"]
                    for item in reranked
                ],
                "retrieved_sources": reranked,
                "retrieval_latency_ms": result[
                    "retrieval_latency_ms"
                ],
                "reranking_latency_ms": round(
                    reranking_latency_ms,
                    2,
                ),
            }
        )


        # ====================================================
        # RERANKED RANKING
        # ====================================================

        print("\nReranked ranking:")

        for rank, item in enumerate(
            reranked,
            start=1,
        ):

            print(
                f"{rank}. "
                f"Chunk {item['chunk_index']} "
                f"| Vector similarity: "
                f"{item['similarity_score']:.4f} "
                f"| Rerank score: "
                f"{item['rerank_score']:.4f}"
            )


        print(
            "Reranking latency:",
            round(
                reranking_latency_ms,
                2,
            ),
            "ms",
        )


finally:

    db.close()


# ============================================================
# SAVE RERANKED RESULTS
# ============================================================

with open(
    RERANKED_RESULTS_PATH,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        reranked_results,
        file,
        indent=2,
    )


print("\n====================================")
print("Reranked results saved to:")
print(RERANKED_RESULTS_PATH)
print("====================================")