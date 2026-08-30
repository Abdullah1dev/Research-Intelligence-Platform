from sqlalchemy.orm import Session

from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder
from app.infrastructure.llm.service import LLMService


class RAGService:

    def __init__(
        self,
        vector_search_service: VectorSearchService,
        context_builder: RAGContextBuilder,
        llm_service: LLMService,
    ):
        self.vector_search_service = vector_search_service
        self.context_builder = context_builder
        self.llm_service = llm_service

    def ask(
        self,
        db: Session,
        document_id: int,
        question: str,
        top_k: int = 4,
    ) -> str:

        # 1. Retrieve relevant chunks
        chunks = self.vector_search_service.search(
            db=db,
            document_id=document_id,
            query=question,
            top_k=4,
        )

        # 2. Build context
        context = self.context_builder.build_context(
            chunks
        )

        if not context:
            return "I could not find relevant information in this document."

        # 3. Build RAG prompt
        prompt = f"""
You are a research paper assistant.

Answer the user's question using ONLY the provided context.

If the answer is not available in the context, say:

"I could not find the answer in the provided document."

Do not make up information.

Context:
{context}

Question:
{question}

Answer:
"""

        # 4. Generate answer
        answer = self.llm_service.generate(
            prompt
        )

        return answer