from deepeval.models import OpenRouterModel
from app.config.settings import settings


def main():
    model = OpenRouterModel(
        model="openrouter/free",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
    )

    response = model.generate(
        "Return a JSON object with exactly these fields: "
        "score (number) and reason (string). "
        "The score should be 1 and the reason should say 'test'."
    )

    print("\n========== JUDGE RESPONSE ==========")
    print(response)


if __name__ == "__main__":
    main()