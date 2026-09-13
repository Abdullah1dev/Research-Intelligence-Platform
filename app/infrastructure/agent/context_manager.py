from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    ToolMessage,
)


MAX_CONTEXT_TOKENS = 4000


def build_model_context(
    messages: list[AnyMessage],
) -> list[AnyMessage]:

    if not messages:
        return []

    # Always keep the latest user message.
    latest_human_index = None

    for index in range(
        len(messages) - 1,
        -1,
        -1,
    ):
        if isinstance(messages[index], HumanMessage):
            latest_human_index = index
            break

    if latest_human_index is None:
        return messages[-1:]

    # Build complete conversation blocks.
    blocks = []

    current_block = []

    for message in messages:

        if (
            isinstance(message, HumanMessage)
            and current_block
        ):
            blocks.append(current_block)
            current_block = []

        current_block.append(message)

    if current_block:
        blocks.append(current_block)

    # Start from the newest complete blocks.
    selected_blocks = []
    estimated_tokens = 0

    for block in reversed(blocks):

        block_tokens = estimate_message_tokens(block)

        if (
            selected_blocks
            and estimated_tokens + block_tokens
            > MAX_CONTEXT_TOKENS
        ):
            break

        selected_blocks.insert(
            0,
            block,
        )

        estimated_tokens += block_tokens

    return [
        message
        for block in selected_blocks
        for message in block
    ]


def estimate_message_tokens(
    messages: list[AnyMessage],
) -> int:

    total_characters = 0

    for message in messages:

        content = message.content

        if isinstance(content, str):
            total_characters += len(content)

        # Tool calls can contain additional content
        if isinstance(message, AIMessage):

            for tool_call in message.tool_calls:
                total_characters += len(
                    str(tool_call)
                )

        # Tool messages can contain large RAG results
        if isinstance(message, ToolMessage):
            total_characters += len(
                str(message.content)
            )

    # Rough approximation:
    # ~4 characters ≈ 1 token
    return total_characters // 4