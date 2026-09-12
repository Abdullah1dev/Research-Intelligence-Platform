from langchain_core.messages import AnyMessage


MAX_RECENT_MESSAGES = 8


def build_model_context(
    messages: list[AnyMessage],
) -> list[AnyMessage]:

    if not messages:
        return []

    return messages[-MAX_RECENT_MESSAGES:]