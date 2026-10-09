print(">>> FILE STARTED", flush=True)

from app.features.users.models import User
from app.features.papers.models import Paper, PaperDocument, DocumentChunk
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal

print(">>> RAG DEPENDENCY IMPORTED", flush=True)
from app.infrastructure.rag.dependencies import get_rag_service

from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import AsyncConfig, CacheConfig

from evaluation.generator.metrics import get_faithfulness_metric

print(">>> METRICS IMPORTED", flush=True)

from pathlib import Path
import json


BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "datasets"
    / "research_questions.json"
)


def main():

    print(">>> MAIN STARTED", flush=True)

    db = SessionLocal()

    print(">>> DATABASE SESSION CREATED", flush=True)

    try:

        print(">>> BEFORE get_rag_service()", flush=True)

        rag_service = get_rag_service()

        print(">>> AFTER get_rag_service()", flush=True)

        with open(
            DATASET_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            questions = json.load(file)

        test_cases = []

        # --------------------------------------------------------
        # Q1 ONLY — first Faithfulness test
        # --------------------------------------------------------

        for item in questions[4:5]:

            question = item["question"]
            document_id = item["document_id"]

            print(f"\n{'=' * 70}")
            print(f"Evaluating {item['id']}")
            print(f"Question: {question}")
            print("=" * 70)

            # ----------------------------------------------------
            # Run the actual RAG pipeline
            # ----------------------------------------------------

            result = rag_service.ask(
                db=db,
                document_id=document_id,
                question=question,
                retrieval_top_k=10,
                rerank_top_k=4,
                similarity_threshold=0.5,
            )

            # ----------------------------------------------------
            # Show generated answer
            # ----------------------------------------------------

            print("\nGENERATED ANSWER")
            print("=" * 70)
            print(result["answer"])

            # ----------------------------------------------------
            # Create DeepEval test case
            # ----------------------------------------------------

            test_case = LLMTestCase(
                input=question,
                actual_output=result["answer"],
                retrieval_context=[
                    source.content
                    for source in result["sources"]
                ],
            )

            test_cases.append(test_case)

        # --------------------------------------------------------
        # Create Faithfulness judge
        # --------------------------------------------------------

        faithfulness = get_faithfulness_metric()

        print("\nAll test cases created. Starting DeepEval...")

        
        evaluate(
            test_cases=test_cases,
            metrics=[faithfulness],
            async_config=AsyncConfig(run_async=False),
            cache_config=CacheConfig(write_cache=False),
        )

    finally:

        db.close()


if __name__ == "__main__":
    main()