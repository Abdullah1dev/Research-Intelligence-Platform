import json
from pathlib import Path


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BASELINE_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / "retrieval_baseline.json"
)

RERANKED_PATH = (
    BASE_DIR
    / "evaluation"
    / "results"
    / "retrieval_reranked.json"
)


# ============================================================
# Helpers
# ============================================================

def get_rank(chunk_index, ranking):
    """
    Return 1-based rank of a chunk.

    Example:
        ranking = [5, 2, 7]
        chunk_index = 2
        return 2

    Returns None if the chunk is not present.
    """
    try:
        return ranking.index(chunk_index) + 1
    except ValueError:
        return None


def get_relevant_ranks(expected_chunks, ranking):
    """
    Return the ranks of all expected/relevant chunks.
    """
    ranks = []

    for chunk_index in expected_chunks:
        rank = get_rank(chunk_index, ranking)

        if rank is not None:
            ranks.append((chunk_index, rank))

    return ranks


# ============================================================
# Load Results
# ============================================================

with open(BASELINE_PATH, "r", encoding="utf-8") as file:
    baseline_results = json.load(file)

with open(RERANKED_PATH, "r", encoding="utf-8") as file:
    reranked_results = json.load(file)


# ============================================================
# Create lookup for reranked results
# ============================================================

reranked_by_question = {
    result["question_id"]: result
    for result in reranked_results
}


# ============================================================
# Analysis
# ============================================================

print("=" * 70)
print("RERANKING ANALYSIS")
print("=" * 70)


for baseline in baseline_results:

    question_id = baseline["question_id"]
    question = baseline["question"]

    expected_chunks = baseline["expected_chunk_indexes"]

    reranked = reranked_by_question.get(question_id)

    if reranked is None:
        print(f"\n{question_id}")
        print("Reranked result not found.")
        continue

    baseline_ranking = baseline["retrieved_chunk_indexes"]
    reranked_ranking = reranked["retrieved_chunk_indexes"]

    # --------------------------------------------------------
    # Skip unanswerable questions
    # --------------------------------------------------------

    if not expected_chunks:
        print(f"\n{question_id}")
        print(f"Question: {question}")
        print("Unanswerable question - skipped")
        continue

    # --------------------------------------------------------
    # Get ranks
    # --------------------------------------------------------

    baseline_ranks = get_relevant_ranks(
        expected_chunks,
        baseline_ranking,
    )

    reranked_ranks = get_relevant_ranks(
        expected_chunks,
        reranked_ranking,
    )

    # First relevant rank
    baseline_first_rank = (
        min(rank for _, rank in baseline_ranks)
        if baseline_ranks
        else None
    )

    reranked_first_rank = (
        min(rank for _, rank in reranked_ranks)
        if reranked_ranks
        else None
    )

    # --------------------------------------------------------
    # Print
    # --------------------------------------------------------

    print("\n" + "-" * 70)

    print(f"{question_id}")
    print(f"Question: {question}")

    print(f"\nExpected relevant chunks:")
    print(f"  {expected_chunks}")

    print(f"\nBaseline ranking:")
    print(f"  {baseline_ranking}")

    print(f"\nReranked ranking:")
    print(f"  {reranked_ranking}")

    print(f"\nRelevant chunk ranks:")

    print("  Baseline:")
    if baseline_ranks:
        for chunk_index, rank in baseline_ranks:
            print(f"    Chunk {chunk_index} -> Rank {rank}")
    else:
        print("    No relevant chunk retrieved")

    print("  Reranked:")
    if reranked_ranks:
        for chunk_index, rank in reranked_ranks:
            print(f"    Chunk {chunk_index} -> Rank {rank}")
    else:
        print("    No relevant chunk retrieved")

    print("\nFirst relevant chunk:")

    print(f"  Baseline:  Rank {baseline_first_rank}")
    print(f"  Reranked:  Rank {reranked_first_rank}")

    # --------------------------------------------------------
    # Determine movement
    # --------------------------------------------------------

    if baseline_first_rank is None and reranked_first_rank is not None:
        print("  Result: IMPROVED - relevant chunk was retrieved")

    elif baseline_first_rank is not None and reranked_first_rank is None:
        print("  Result: WORSE - relevant chunk was lost")

    elif (
        baseline_first_rank is not None
        and reranked_first_rank is not None
    ):
        if reranked_first_rank < baseline_first_rank:
            print("  Result: IMPROVED - relevant chunk moved higher")

        elif reranked_first_rank > baseline_first_rank:
            print("  Result: WORSE - relevant chunk moved lower")

        else:
            print("  Result: UNCHANGED - same first relevant rank")


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

