import json
from pathlib import Path

from app.features.users.models import User
from app.features.papers.models import (
    Paper,
    PaperDocument,
    DocumentChunk,
)
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "datasets" / "research_questions.json"
BASELINE_PATH = BASE_DIR / "results" / "retrieval_baseline.json"
RERANKED_PATH = BASE_DIR / "results" / "retrieval_reranked.json"


# ============================================================
# Load files
# ============================================================

with open(DATASET_PATH, "r", encoding="utf-8") as file:
    questions = json.load(file)

with open(BASELINE_PATH, "r", encoding="utf-8") as file:
    baseline_results = json.load(file)

with open(RERANKED_PATH, "r", encoding="utf-8") as file:
    reranked_results = json.load(file)


# ============================================================
# Show compact overview
# ============================================================

print("\n" + "=" * 70)
print("RETRIEVAL / RERANKING OVERVIEW")
print("=" * 70)

for question in questions:

    question_id = question["id"]

    if question_id not in {
        "Q1", "Q2", "Q3", "Q4",
        "Q5", "Q6", "Q7", "Q8"
    }:
        continue

    baseline = next(
        item for item in baseline_results
        if item["question_id"] == question_id
    )

    reranked = next(
        item for item in reranked_results
        if item["question_id"] == question_id
    )

    baseline_indexes = [
        item["chunk_index"]
        for item in baseline["retrieved_sources"]
    ]

    reranked_indexes = [
        item["chunk_index"]
        for item in reranked["retrieved_sources"]
    ]

    print(f"\n{question_id}: {question['question']}")
    print(f"GT:       {question.get('relevant_chunk_ids', [])}")
    print(f"Baseline: {baseline_indexes}")
    print(f"Reranked: {reranked_indexes}")


# ============================================================
# Select question
# ============================================================

question_id = input(
    "\n\nEnter question to inspect (Q1-Q8): "
).strip().upper()

selected_question = next(
    (
        question
        for question in questions
        if question["id"] == question_id
    ),
    None,
)

if selected_question is None:
    print("Invalid question.")
    raise SystemExit


# ============================================================
# Select chunks
# ============================================================

print("\nQuestion:")
print(selected_question["question"])

print("\nCurrent Ground Truth:")
print(selected_question.get("relevant_chunk_ids", []))

chunk_input = input(
    "\nEnter chunk indexes to inspect "
    "(example: 3,4): "
).strip()

try:
    chunk_indexes = [
        int(index.strip())
        for index in chunk_input.split(",")
    ]
except ValueError:
    print("Invalid chunk indexes.")
    raise SystemExit


# ============================================================
# Get document ID
# ============================================================

document_id = selected_question["document_id"]


# ============================================================
# Query chunks
# ============================================================

db = SessionLocal()

try:

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == document_id,
            DocumentChunk.chunk_index.in_(chunk_indexes),
        )
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    # ========================================================
    # Display chunks
    # ========================================================

    print("\n" + "=" * 70)
    print("CHUNK CONTENT")
    print("=" * 70)

    for chunk in chunks:

        print("\n" + "-" * 70)
        print(f"Chunk index: {chunk.chunk_index}")
        print(f"Chunk ID: {chunk.id}")
        print("-" * 70)

        print(chunk.content)

finally:
    db.close()