from deepeval.models import OpenRouterModel
from app.config.settings import settings


def main():
    model = OpenRouterModel(
        model="openrouter/free",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    


if __name__ == "__main__":
    main()