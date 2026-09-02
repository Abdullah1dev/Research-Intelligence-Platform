from contextlib import contextmanager

from langgraph.checkpoint.postgres import PostgresSaver

from app.infrastructure.database.config import (
    LANGGRAPH_DATABASE_URL,
)


@contextmanager
def get_checkpointer():

    with PostgresSaver.from_conn_string(
        LANGGRAPH_DATABASE_URL
    ) as checkpointer:

        yield checkpointer