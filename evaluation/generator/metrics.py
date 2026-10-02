from deepeval.metrics import FaithfulnessMetric
from deepeval.models import OpenRouterModel

from app.config.settings import settings


def get_faithfulness_metric():
    judge_model = OpenRouterModel(
        model="openrouter/free",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    return FaithfulnessMetric(
        model=judge_model,
        threshold=0.5,
        include_reason=True,
    )