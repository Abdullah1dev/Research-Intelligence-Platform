import json
from pathlib import Path


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RESULTS_PATH = (
    BASE_DIR
    / "results"
    / "retrieval_baseline.json"
)


# --------------------------------------------------
# Load baseline results
# --------------------------------------------------

with open(
    RESULTS_PATH,
    "r",
    encoding="utf-8",
) as file:

    results = json.load(file)


# --------------------------------------------------
# Metric functions
# --------------------------------------------------

def recall_at_k(
    retrieved,
    relevant,
    k,
):
    """
    Recall@K

    Measures how many of the relevant chunks
    were retrieved in the top K results.
    """

    retrieved_at_k = retrieved[:k]

    relevant_retrieved = len(
        set(retrieved_at_k)
        & set(relevant)
    )

    if len(relevant) == 0:
        return 0.0

    return (
        relevant_retrieved
        / len(relevant)
    )


def precision_at_k(
    retrieved,
    relevant,
    k,
):
    """
    Precision@K

    Measures how many of the top K retrieved
    chunks are actually relevant.
    """

    retrieved_at_k = retrieved[:k]

    relevant_retrieved = len(
        set(retrieved_at_k)
        & set(relevant)
    )

    if k == 0:
        return 0.0

    return (
        relevant_retrieved
        / k
    )


def reciprocal_rank(
    retrieved,
    relevant,
):
    """
    Reciprocal Rank

    Finds the rank of the first relevant
    retrieved chunk.

    RR = 1 / rank

    If no relevant chunk is retrieved,
    RR = 0.
    """

    relevant = set(relevant)

    for rank, chunk_index in enumerate(
        retrieved,
        start=1,
    ):

        if chunk_index in relevant:

            return 1 / rank

    return 0.0


# --------------------------------------------------
# Evaluation configuration
# --------------------------------------------------

K_VALUES = [1, 2, 4 , 10]


# --------------------------------------------------
# Store metric scores
# --------------------------------------------------

recall_scores = {
    k: []
    for k in K_VALUES
}

precision_scores = {
    k: []
    for k in K_VALUES
}

reciprocal_rank_scores = []


# --------------------------------------------------
# Evaluate each question
# --------------------------------------------------

print("\n========================================")
print("       BASELINE RETRIEVAL EVALUATION")
print("========================================")


for result in results:

    question_id = result["question_id"]

    question = result["question"]

    relevant = result[
        "expected_chunk_indexes"
    ]

    retrieved = result[
        "retrieved_chunk_indexes"
    ]


    # ----------------------------------------------
    # Display question information
    # ----------------------------------------------

    print("\n----------------------------------------")
    print("Question:", question_id)
    print("Text:", question)
    print("Expected:", relevant)
    print("Retrieved:", retrieved)


    # ----------------------------------------------
    # Calculate Recall@K and Precision@K
    # ----------------------------------------------

    for k in K_VALUES:

        recall = recall_at_k(
            retrieved,
            relevant,
            k,
        )

        precision = precision_at_k(
            retrieved,
            relevant,
            k,
        )

        recall_scores[k].append(
            recall
        )

        precision_scores[k].append(
            precision
        )


        print(
            f"Recall@{k}:",
            f"{recall:.4f}",
        )

        print(
            f"Precision@{k}:",
            f"{precision:.4f}",
        )


    # ----------------------------------------------
    # Calculate Reciprocal Rank
    # ----------------------------------------------

    rr = reciprocal_rank(
        retrieved,
        relevant,
    )

    reciprocal_rank_scores.append(
        rr
    )

    print(
        "Reciprocal Rank:",
        f"{rr:.4f}",
    )


# --------------------------------------------------
# Calculate average metrics
# --------------------------------------------------

print("\n\n========================================")
print("           FINAL BASELINE METRICS")
print("========================================\n")


for k in K_VALUES:

    mean_recall = (
        sum(recall_scores[k])
        / len(recall_scores[k])
    )

    mean_precision = (
        sum(precision_scores[k])
        / len(precision_scores[k])
    )


    print(
        f"Recall@{k}:",
        f"{mean_recall:.4f}",
    )

    print(
        f"Precision@{k}:",
        f"{mean_precision:.4f}",
    )

    print()


# --------------------------------------------------
# Mean Reciprocal Rank
# --------------------------------------------------

mrr = (
    sum(reciprocal_rank_scores)
    / len(reciprocal_rank_scores)
)


print(
    "MRR:",
    f"{mrr:.4f}",
)


print("\n========================================")
print("       EVALUATION COMPLETE")
print("========================================")

