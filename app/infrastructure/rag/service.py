from sqlalchemy.orm import Session

from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder
from app.infrastructure.llm.service import LLMService
from app.infrastructure.rag.models import (
    RetrievalResult,
    RetrievalSource,
)

from app.infrastructure.rag.reranker import RerankerService

class RAGService:

    def __init__(
        self,
        vector_search_service: VectorSearchService,
        context_builder: RAGContextBuilder,
        reranker_service: RerankerService,
        llm_service: LLMService,
        
       
    ):
        self.vector_search_service = vector_search_service
        self.context_builder = context_builder
        self.llm_service = llm_service
        self.reranker_service = reranker_service

    # Retrieval method:
    # responsible only for searching chunks and building context
    def retrieve(
        self,
        db: Session,
        document_id: int,
        question: str,
        retrieval_top_k: int = 10,
        rerank_top_k: int = 4,
        similarity_threshold: float = 0.5,
    ) -> RetrievalResult:

        # 1. Search for relevant chunks
        search_results = self.vector_search_service.search(
            db=db,
            document_id=document_id,
            query=question,
            top_k=retrieval_top_k,
            similarity_threshold=similarity_threshold,
        )
        
        print("========== RERANKER EXECUTED ==========")
        reranked_results = self.reranker_service.rerank(
            question=question,
            candidates=search_results,
            top_k=rerank_top_k,
        
        )
        
        
        
        print(f"Candidates returned by reranker: {len(reranked_results)}")
        print("========== RERANKER END ==========")

        # 2. Stop if no relevant chunks were found
        if not reranked_results:
            return RetrievalResult(
                context="",
                sources=[],
            )

        # 3. Extract chunks
        chunks = [
            result["chunk"]
            for result in reranked_results
        ]

        # 4. Build context
        context = self.context_builder.build_context(
            chunks
        )

        # 5. Stop if context could not be built
        if not context:
            return RetrievalResult(
                context="",
                sources=[],
            )

        # 6. Prepare source information
        sources = []

        for result in reranked_results:

            chunk = result["chunk"]

            sources.append(
                RetrievalSource(
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    similarity_score=result["similarity_score"],
                )
            )

        # 7. Return structured retrieval result
        return RetrievalResult(
            context=context,
            sources=sources,
        )

    # Ask method:
    # responsible for retrieval + LLM generation
    def ask(
        self,
        db: Session,
        document_id: int,
        question: str,
        retrieval_top_k: int = 10,
        rerank_top_k: int = 4,
        similarity_threshold: float = 0.5,
    
    ) -> dict:

        # 1. Retrieve relevant information
        retrieval = self.retrieve(
            db=db,
            document_id=document_id,
            question=question,
            retrieval_top_k=retrieval_top_k,
            rerank_top_k=rerank_top_k,
            similarity_threshold=similarity_threshold,
            
        )
        # 2. Stop if nothing relevant was retrieved
        if not retrieval.sources:
            return {
                "answer": (
                    "I could not find relevant information "
                    "in this document."
                ),
                "sources": [],
            }

        # 3. Get retrieved context
        context = retrieval.context

        # 4. Build grounded RAG prompt
        prompt = f"""
You are a research paper assistant.

Answer the user's question using ONLY the provided context.

If the answer is not available in the context, say:

"I could not find the answer in the provided document."

Do not make up information.
Do not use outside knowledge.

Context:
{context}

Question:
{question}

Answer:
"""

        # 5. Generate answer
        answer = self.llm_service.generate(
            prompt
        )

        # 6. Return answer and sources
        return {
            "answer": answer,
            "sources": retrieval.sources,
        }