from langchain_openai import ChatOpenAI

from app.config.settings import settings


def get_chat_model():

    return ChatOpenAI(
        model="openai/gpt-oss-20b",
        api_key=settings.OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.2,
    )