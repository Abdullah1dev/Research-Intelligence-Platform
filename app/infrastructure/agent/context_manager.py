from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
)


MAX_RECENT_TURNS = 4


def build_model_context(
    messages: list[AnyMessage],
) -> list[AnyMessage]:

    if not messages:
        return []

    human_indexes = [
        index
        for index, message in enumerate(messages)
        if isinstance(message, HumanMessage)
    ]

    if len(human_indexes) <= MAX_RECENT_TURNS:
        return messages

    start_index = human_indexes[-MAX_RECENT_TURNS]

    return messages[start_index:]