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

BASELINE_PATH = (
    BASE_DIR
    / "results"
    / "retrieval_baseline.json"
)

RERANKED_PATH = (
    BASE_DIR
    / "results"
    / "retrieval_reranked.json"
)


# ============================================================
# Load results
# ============================================================

with open(
    BASELINE_PATH,
    "r",
    encoding="utf-8",
) as file:
    baseline_results = json.load(file)


with open(
    RERANKED_PATH,
    "r",
    encoding="utf-8",
) as file:
    reranked_results = json.load(file)


# ============================================================
# Get Q4
# ============================================================

baseline_q4 = next(
    item
    for item in baseline_results
    if item["question_id"] == "Q4"
)

reranked_q4 = next(
    item
    for item in reranked_results
    if item["question_id"] == "Q4"
)


question = baseline_q4["question"]

expected_indexes = baseline_q4[
    "expected_chunk_indexes"
]


print("\n============================================")
print("RERANKING INSPECTION — Q4")
print("============================================")

print("\nQuestion:")
print(question)

print("\nExpected relevant chunk indexes:")
print(expected_indexes)


# ============================================================
# Reranked lookup
# ============================================================

reranked_by_id = {
    item["chunk_id"]: item
    for item in reranked_q4["retrieved_sources"]
}


# ============================================================
# Get top 5 from each ranking
# ============================================================

baseline_top_5 = (
    baseline_q4["retrieved_sources"][:5]
)

reranked_top_5 = (
    reranked_q4["retrieved_sources"][:5]
)


# ============================================================
# Collect chunk IDs
# ============================================================

chunk_ids = set()

for source in baseline_top_5:
    chunk_ids.add(source["chunk_id"])

for source in reranked_top_5:
    chunk_ids.add(source["chunk_id"])

# Also include the expected relevant chunk(s)
for source in baseline_q4["retrieved_sources"]:

    if source["chunk_index"] in expected_indexes:
        chunk_ids.add(source["chunk_id"])


# ============================================================
# Fetch chunks
# ============================================================

db = SessionLocal()

try:

    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.id.in_(chunk_ids)
        )
        .all()
    )

    chunks_by_id = {
        chunk.id: chunk
        for chunk in chunks
    }

finally:

    db.close()


# ============================================================
# Helper function
# ============================================================

def print_chunk(
    rank,
    source,
    show_rerank=False,
):

    chunk_id = source["chunk_id"]
    chunk_index = source["chunk_index"]

    chunk = chunks_by_id.get(chunk_id)

    print("\n--------------------------------------------")

    print(f"Rank: {rank}")
    print(f"Chunk index: {chunk_index}")
    print(f"Chunk ID: {chunk_id}")

    print(
        f"Vector similarity: "
        f"{source.get('similarity_score', 'N/A')}"
    )

    if show_rerank:

        print(
            f"Rerank score: "
            f"{source.get('rerank_score', 'N/A')}"
        )

    if chunk_index in expected_indexes:

        print(
            ">>> EXPECTED RELEVANT CHUNK <<<"
        )

    if chunk is None:

        print(
            "ERROR: Chunk not found in database."
        )

        return

    print("\nCONTENT:")
    print(chunk.content)


# ============================================================
# Vector search ranking
# ============================================================

print("\n\n============================================")
print("TOP 5 — VECTOR SEARCH")
print("============================================")

for rank, source in enumerate(
    baseline_top_5,
    start=1,
):

    print_chunk(
        rank,
        source,
        show_rerank=False,
    )


# ============================================================
# Reranker ranking
# ============================================================

print("\n\n============================================")
print("TOP 5 — RERANKER")
print("============================================")

for rank, source in enumerate(
    reranked_top_5,
    start=1,
):

    print_chunk(
        rank,
        source,
        show_rerank=True,
    )


# ============================================================
# Expected relevant chunk
# ============================================================

print("\n\n============================================")
print("EXPECTED RELEVANT CHUNK(S)")
print("============================================")

for source in baseline_q4["retrieved_sources"]:

    if source["chunk_index"] not in expected_indexes:
        continue

    chunk_index = source["chunk_index"]
    chunk_id = source["chunk_id"]

    print("\n--------------------------------------------")

    print(
        f"Chunk index: {chunk_index}"
    )

    print(
        f"Chunk ID: {chunk_id}"
    )

    # Vector rank
    vector_rank = (
        baseline_q4[
            "retrieved_chunk_indexes"
        ].index(chunk_index) + 1
    )

    print(
        f"Vector rank: {vector_rank}"
    )

    # Reranker rank
    if chunk_index in reranked_q4[
        "retrieved_chunk_indexes"
    ]:

        reranker_rank = (
            reranked_q4[
                "retrieved_chunk_indexes"
            ].index(chunk_index) + 1
        )

        print(
            f"Reranker rank: {reranker_rank}"
        )

    reranked_source = reranked_by_id.get(
        chunk_id
    )

    if reranked_source:

        print(
            f"Rerank score: "
            f"{reranked_source['rerank_score']}"
        )

    chunk = chunks_by_id.get(
        chunk_id
    )

    if chunk:

        print("\nCONTENT:")
        print(chunk.content)


print("\n\n============================================")
print("INSPECTION COMPLETE")
print("============================================")