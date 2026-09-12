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
    
    #Retrieveal method for only chunking and context building
    def retrieve(
        self,
        db: Session,
        document_id: int,
        question: str,
        top_k: int = 4,
        similarity_threshold: float = 0.5,
    ) -> dict:

        # 1. Search for relevant chunks
        search_results = self.vector_search_service.search(
            db=db,
            document_id=document_id,
            query=question,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        # 2. Stop if no relevant chunks were found
        if not search_results:
            return {
                "context": "",
                "sources": [],
            }

        # 3. Extract chunks
        chunks = [
            result["chunk"]
            for result in search_results
        ]

        # 4. Build context
        context = self.context_builder.build_context(
            chunks
        )

        if not context:
            return {
                "context": "",
                "sources": [],
            }

        # 5. Prepare source information
        sources = []

        for result in search_results:

            chunk = result["chunk"]

            sources.append(
                {
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "similarity_score": (
                        result["similarity_score"]
                    ),
                }
            )

        # 6. Return retrieval result
        return {
            "context": context,
            "sources": sources,
        }


    #Ask method for llm generation
    def ask(
        self,
        db: Session,
        document_id: int,
        question: str,
        top_k: int = 4,
        similarity_threshold: float = 0.5,
    ) -> dict:

        # 1. Retrieve relevant information
        retrieval = self.retrieve(
            db=db,
            document_id=document_id,
            question=question,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        # 2. Stop if nothing relevant was retrieved
        if not retrieval["sources"]:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in this document."
                ),
                "sources": [],
            }

        context = retrieval["context"]

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

        # 5. Return answer and sources
        return {
            "answer": answer,
            "sources": retrieval["sources"],
        }