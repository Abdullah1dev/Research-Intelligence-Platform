import json
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

RESULTS_FILE = (
    Path(__file__).resolve().parents[2]
    / "evaluation"
    / "results"
    / "retrieval_reranked.json"
)

K_VALUES = [1, 2, 4, 10]


# ============================================================
# Load evaluation results
# ============================================================

with open(
    RESULTS_FILE,
    "r",
    encoding="utf-8",
) as f:

    results = json.load(f)


# ============================================================
# Metric functions
# ============================================================

def recall_at_k(expected, retrieved, k):
    """
    Recall@K =
    number of relevant chunks retrieved in top K
    -----------------------------------------------
    total number of relevant chunks
    """

    expected_set = set(expected)
    retrieved_top_k = set(retrieved[:k])

    if not expected_set:
        return None

    return (
        len(expected_set & retrieved_top_k)
        / len(expected_set)
    )


def precision_at_k(expected, retrieved, k):
    """
    Precision@K =
    number of relevant chunks retrieved in top K
    -----------------------------------------------
    K
    """

    expected_set = set(expected)
    retrieved_top_k = retrieved[:k]

    if k == 0:
        return None

    relevant_retrieved = sum(
        1
        for chunk in retrieved_top_k
        if chunk in expected_set
    )

    return relevant_retrieved / k


def reciprocal_rank(expected, retrieved):
    """
    Reciprocal Rank =
    1 / rank of the first relevant chunk

    If no relevant chunk is retrieved:
    return 0
    """

    expected_set = set(expected)

    for rank, chunk in enumerate(
        retrieved,
        start=1,
    ):

        if chunk in expected_set:
            return 1.0 / rank

    return 0.0


# ============================================================
# Average helper
# ============================================================

def average(values):

    valid_values = [
        value
        for value in values
        if value is not None
    ]

    if not valid_values:
        return 0.0

    return sum(valid_values) / len(valid_values)


# ============================================================
# Calculate metrics
# ============================================================

recall_scores = {
    k: []
    for k in K_VALUES
}

precision_scores = {
    k: []
    for k in K_VALUES
}

reciprocal_ranks = []


evaluated_questions = []
excluded_questions = []


for item in results:

    expected = item[
        "expected_chunk_indexes"
    ]

    retrieved = item[
        "retrieved_chunk_indexes"
    ]


    # --------------------------------------------------------
    # Exclude unanswerable questions
    # --------------------------------------------------------

    if not expected:

        excluded_questions.append(
            item["question_id"]
        )

        continue


    evaluated_questions.append(
        item["question_id"]
    )


    # --------------------------------------------------------
    # Recall and Precision
    # --------------------------------------------------------

    for k in K_VALUES:

        recall_scores[k].append(
            recall_at_k(
                expected,
                retrieved,
                k,
            )
        )

        precision_scores[k].append(
            precision_at_k(
                expected,
                retrieved,
                k,
            )
        )


    # --------------------------------------------------------
    # MRR
    # --------------------------------------------------------

    reciprocal_ranks.append(
        reciprocal_rank(
            expected,
            retrieved,
        )
    )


# ============================================================
# Average metrics
# ============================================================

recall_results = {
    k: average(recall_scores[k])
    for k in K_VALUES
}

precision_results = {
    k: average(precision_scores[k])
    for k in K_VALUES
}

mrr = average(
    reciprocal_ranks
)


# ============================================================
# Print results
# ============================================================

print("\n" + "=" * 50)
print("RETRIEVAL EVALUATION - RERANKED")
print("=" * 50)


print("\nRecall:")

for k in K_VALUES:

    print(
        f"Recall@{k:<2}    = "
        f"{recall_results[k]:.4f}"
    )


print("\nPrecision:")

for k in K_VALUES:

    print(
        f"Precision@{k:<2} = "
        f"{precision_results[k]:.4f}"
    )


print("\nMRR:")

print(
    f"MRR           = "
    f"{mrr:.4f}"
)


# ============================================================
# Question information
# ============================================================

print("\n" + "=" * 50)

print(
    "Questions evaluated:",
    len(evaluated_questions),
)

print(
    "Excluded unanswerable:",
    len(excluded_questions),
)

if excluded_questions:

    print(
        "Excluded questions:",
        ", ".join(excluded_questions),
    )

print("=" * 50)