from langgraph.checkpoint.postgres import PostgresSaver

from app.infrastructure.database.config import (
    LANGGRAPH_DATABASE_URL,
)


with PostgresSaver.from_conn_string(
    LANGGRAPH_DATABASE_URL
) as checkpointer:

    checkpointer.setup()

    print(
        "LangGraph checkpoint tables created successfully."
    )