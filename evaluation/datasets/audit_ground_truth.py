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

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "research_questions.json"
)


# ============================================================
# Load evaluation dataset
# ============================================================

with open(
    DATASET_PATH,
    "r",
    encoding="utf-8",
) as file:
    questions = json.load(file)


# ============================================================
# Database
# ============================================================

db = SessionLocal()


try:

    for item in questions:

        question_id = item["id"]
        question = item["question"]
        document_id = item["document_id"]

        expected_indexes = item.get(
            "relevant_chunk_ids",
            [],
        )

        answerable = item.get(
            "answerable",
            True,
        )

        print("\n\n")
        print("=" * 70)
        print(f"QUESTION: {question_id}")
        print("=" * 70)

        print("\nQuestion:")
        print(question)

        print("\nDocument ID:")
        print(document_id)

        print("\nAnswerable:")
        print(answerable)

        print("\nCurrent expected chunk indexes:")
        print(expected_indexes)

        # ----------------------------------------------------
        # Get all chunks for this document
        # ----------------------------------------------------

        chunks = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.document_id
                == document_id
            )
            .order_by(
                DocumentChunk.chunk_index
            )
            .all()
        )

        print(
            f"\nTotal chunks in document: "
            f"{len(chunks)}"
        )

        # ----------------------------------------------------
        # Print every chunk
        # ----------------------------------------------------

        for chunk in chunks:

            is_expected = (
                chunk.chunk_index
                in expected_indexes
            )

            print("\n")
            print("-" * 70)

            if is_expected:
                print(
                    f">>> CURRENTLY LABELED RELEVANT "
                    f"<<<"
                )

            print(
                f"Chunk index: "
                f"{chunk.chunk_index}"
            )

            print(
                f"Chunk ID: "
                f"{chunk.id}"
            )

            print("\nCONTENT:")
            print(chunk.content)

        print("\n")
        print("=" * 70)
        print(
            f"END OF {question_id}"
        )
        print("=" * 70)


finally:

    db.close()


print("\n")
print("=" * 70)
print("GROUND-TRUTH AUDIT COMPLETE")
print("=" * 70)