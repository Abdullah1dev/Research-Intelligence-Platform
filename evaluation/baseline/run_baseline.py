import json
import time
from pathlib import Path

# Register SQLAlchemy models
from app.features.users.models import User
from app.features.papers.models import (
    Paper,
    PaperDocument,
    DocumentChunk,
)
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.rag.dependencies import rag_service
from sqlalchemy import text


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "research_questions.json"
)

RESULTS_DIR = BASE_DIR / "results"

RESULTS_PATH = (
    RESULTS_DIR
    / "retrieval_baseline.json"
)


# --------------------------------------------------
# Load evaluation dataset
# --------------------------------------------------

with open(
    DATASET_PATH,
    "r",
    encoding="utf-8",
) as file:

    questions = json.load(file)


# --------------------------------------------------
# Create results directory
# --------------------------------------------------

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# --------------------------------------------------
# Run baseline retrieval
# --------------------------------------------------

db = SessionLocal()

from sqlalchemy import text

print(
    "Connected database:",
    db.execute(
        text("SELECT current_database()")
    ).scalar(),
)

print(
    "Document 1 chunks:",
    db.execute(
        text("""
            SELECT COUNT(*)
            FROM document_chunks
            WHERE document_id = 1
        """)
    ).scalar(),
)

rows = db.execute(
    text("""
        SELECT id, document_id, chunk_index
        FROM document_chunks
        WHERE document_id = 1
        ORDER BY chunk_index
    """)
).fetchall()

print("Chunk rows:")
for row in rows:
    print(row)

results = []

try:

    for item in questions:

        question_id = item["id"]
        question = item["question"]
        document_id = item["document_id"]

        expected_chunk_ids = item[
            "relevant_chunk_ids"
        ]

        print("\n====================================")
        print("Question:", question_id)
        print("Text:", question)
        print("====================================")

        # ------------------------------------------
        # Measure retrieval latency
        # ------------------------------------------

        start_time = time.perf_counter()

        retrieval = rag_service.retrieve(
            db=db,
            document_id=document_id,
            question=question,
            top_k=4,
            similarity_threshold=0.5,
        )

        end_time = time.perf_counter()

        latency_ms = (
            end_time - start_time
        ) * 1000

        # ------------------------------------------
        # Extract retrieved sources
        # ------------------------------------------

        retrieved_sources = []

        for source in retrieval.sources:

            retrieved_sources.append(
                {
                    "chunk_id": source.chunk_id,
                    "chunk_index": source.chunk_index,
                    "similarity_score": (
                        source.similarity_score
                    ),
                }
            )

        retrieved_chunk_ids = [
            source["chunk_id"]
            for source in retrieved_sources
        ]

        # ------------------------------------------
        # Store result
        # ------------------------------------------

        result = {
            "question_id": question_id,
            "question": question,
            "document_id": document_id,
            "expected_chunk_ids": (
                expected_chunk_ids
            ),
            "retrieved_chunk_ids": (
                retrieved_chunk_ids
            ),
            "retrieved_sources": (
                retrieved_sources
            ),
            "retrieval_latency_ms": round(
                latency_ms,
                2,
            ),
        }

        results.append(result)

        # ------------------------------------------
        # Console output
        # ------------------------------------------

        print(
            "Expected chunks:",
            expected_chunk_ids,
        )

        print(
            "Retrieved chunks:",
            retrieved_chunk_ids,
        )

        print(
            "Latency:",
            round(latency_ms, 2),
            "ms",
        )


finally:

    db.close()


# --------------------------------------------------
# Save baseline results
# --------------------------------------------------

with open(
    RESULTS_PATH,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        results,
        file,
        indent=2,
    )


print("\n====================================")
print("Baseline retrieval evaluation complete.")
print("Results saved to:")
print(RESULTS_PATH)
print("====================================")