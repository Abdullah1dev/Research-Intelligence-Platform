from langchain_ollama import ChatOllama


def get_chat_model():

    return ChatOllama(
        model="qwen2.5:1.5b",
        base_url="http://localhost:11434",
        temperature=0.2,
    )