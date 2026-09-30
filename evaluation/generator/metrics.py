import os

from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
)
from deepeval.models import OpenRouterModel


def get_evaluation_metrics():
    api_key = os.getenv("OPEN_AI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPEN_AI_API_KEY is not set."
        )

    judge_model = OpenRouterModel(
        model="qwen/qwen3.8-27b:free",
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    faithfulness = FaithfulnessMetric(
        model=judge_model,
        threshold=0.5,
        include_reason=True,
    )

    answer_relevancy = AnswerRelevancyMetric(
        model=judge_model,
        threshold=0.5,
        include_reason=True,
    )

    return faithfulness, answer_relevancy