from sqlalchemy.orm import Session

from app.infrastructure.vector_search.service import VectorSearchService
from app.infrastructure.rag.context_builder import RAGContextBuilder
from app.infrastructure.llm.service import LLMService
from app.infrastructure.rag.models import (
    RetrievalResult,
    RetrievalSource,
)

from app.infrastructure.rag.reranker import RerankerService
import time


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

        start = time.perf_counter()

        # 1. Search for relevant chunks
        search_results = self.vector_search_service.search(
            db=db,
            document_id=document_id,
            query=question,
            top_k=retrieval_top_k,
            similarity_threshold=similarity_threshold,
        )

        vector_search_time = time.perf_counter() - start

        print(
            f"[LATENCY] Vector search: "
            f"{vector_search_time:.3f}s",
            flush=True,
        )

        start = time.perf_counter()

        print("========== RERANKER EXECUTED ==========")

        reranked_results = self.reranker_service.rerank(
            question=question,
            candidates=search_results,
            top_k=rerank_top_k,
        )

        reranker_time = time.perf_counter() - start

        print(
            f"[LATENCY] Reranker: "
            f"{reranker_time:.3f}s",
            flush=True,
        )

        print(
            f"Candidates returned by reranker: "
            f"{len(reranked_results)}"
        )

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

        # Start total request timer
        request_start = time.perf_counter()

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
            total_time = time.perf_counter() - request_start

            print(
                f"[LATENCY] Total request: "
                f"{total_time:.3f}s",
                flush=True,
            )

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

Rules:
1. Use only information explicitly supported by the provided context.
2. Do not use outside knowledge or make assumptions.
3. If the context does not contain enough information to answer the question, say:
   "I could not find the answer in the provided document."
4. If only part of the question can be answered from the context, answer only the supported part and clearly state that the remaining information could not be found.
5. Keep the answer concise and directly address the user's question.

Context:
{context}

Question:
{question}

Answer:
"""

        # 5. Generate answer
        llm_start = time.perf_counter()

        answer = self.llm_service.generate(
            prompt
        )

        llm_time = time.perf_counter() - llm_start

        print(
            f"[LATENCY] LLM generation: "
            f"{llm_time:.3f}s",
            flush=True,
        )

        # 6. Calculate total request time
        total_time = time.perf_counter() - request_start

        print(
            f"[LATENCY] Total request: "
            f"{total_time:.3f}s",
            flush=True,
        )

        # 7. Return answer and sources
        return {
            "answer": answer,
            "sources": retrieval.sources,
        }