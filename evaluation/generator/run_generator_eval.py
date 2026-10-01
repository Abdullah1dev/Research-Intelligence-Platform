from app.features.users.models import User
from app.features.papers.models import Paper, PaperDocument, DocumentChunk
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.rag.dependencies import get_rag_service

from deepeval import evaluate
from deepeval.test_case import LLMTestCase


from deepeval.evaluate import AsyncConfig , CacheConfig

from evaluation.generator.metrics import get_answer_relevancy_metric
from pathlib import Path

import json

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "research_questions.json"
)



def main():

    db = SessionLocal()

    try:
        rag_service = get_rag_service()

        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            questions = json.load(file)

        test_cases = []

        for item in questions:

            question = item["question"]
            document_id = item["document_id"]

            print(f"\n{'=' * 70}")
            print(f"Evaluating {item['id']}")
            print(f"Question: {question}")
            print("=" * 70)

            result = rag_service.ask(
                db=db,
                document_id=document_id,
                question=question,
                retrieval_top_k=10,
                rerank_top_k=4,
                similarity_threshold=0.5,
            )

            print("\nGENERATED ANSWER")
            print("=" * 70)
            print(result["answer"])

            test_case = LLMTestCase(
                input=question,
                actual_output=result["answer"],
                retrieval_context=[
                    source.content
                    for source in result["sources"]
                ],
            )

            test_cases.append(test_case)

        answer_relevancy = get_answer_relevancy_metric()

        print("\nAll test cases created. Starting DeepEval...")

        evaluate(
            test_cases=test_cases,
            metrics=[answer_relevancy],
            async_config=AsyncConfig(run_async=False),
            cache_config=CacheConfig(write_cache=False),
        )

    finally:
        db.close()