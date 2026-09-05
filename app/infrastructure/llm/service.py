from langchain_openai import ChatOpenAI

from app.config.settings import settings


class LLMService:

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ):
        self.model = model

        self.llm = ChatOpenAI(
            model=self.model,
            api_key=settings.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.2,
        )

    def generate(
        self,
        prompt: str,
    ) -> str:

        response = self.llm.invoke(
            prompt
        )

        return response.content