from deepeval.metrics import AnswerRelevancyMetric
from deepeval.models import OpenRouterModel

from app.config.settings import settings


def get_answer_relevancy_metric():
    judge_model = OpenRouterModel(
        model="openrouter/free",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    return AnswerRelevancyMetric(
        model=judge_model,
        threshold=0.5,
        include_reason=True,
    )