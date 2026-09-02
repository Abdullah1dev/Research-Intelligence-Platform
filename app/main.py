from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.features.auth.router import router as auth_router

from app.features.papers.router import router as papers_router

from app.features.conversations.router import (
    router as conversations_router,
)

from app.config.settings import settings

from app.infrastructure.agent.memory import (
    get_checkpointer,
)

from app.infrastructure.agent.graph import (
    build_research_agent,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    with get_checkpointer() as checkpointer:

        # Create checkpoint tables if needed
        checkpointer.setup()

        # Build the LangGraph Research Agent
        research_agent = build_research_agent(
            checkpointer=checkpointer,
        )

        # Store the agent for reuse
        app.state.research_agent = research_agent

        print(
            "Research Agent initialized successfully."
        )

        yield

        print(
            "Shutting down Research Agent."
        )


app = FastAPI(

    title=settings.APP_NAME,

    version=settings.APP_VERSION,

    lifespan=lifespan,

)


app.include_router(auth_router)

app.include_router(papers_router)

app.include_router(conversations_router)