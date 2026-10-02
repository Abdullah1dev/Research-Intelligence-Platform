from deepeval.metrics import FaithfulnessMetric
from deepeval.models import GeminiModel

from app.config.settings import settings


def get_faithfulness_metric():
    judge_model = GeminiModel(
        model="gemini-3.5-flash-lite",
        api_key=settings.GOOGLE_API_KEY,
        temperature=0,
    )

    return FaithfulnessMetric(
        model=judge_model,
        threshold=0.5,
        include_reason=True,
    )