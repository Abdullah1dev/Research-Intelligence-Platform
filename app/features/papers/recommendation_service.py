from sqlalchemy.orm import Session

from app.features.papers.models import Paper
from app.infrastructure.external_apis.semantic_scholar.service import (
    SemanticScholarService,
)


class PaperRecommendationService:

    def __init__(
        self,
        semantic_scholar: SemanticScholarService,
    ):
        self.semantic_scholar = semantic_scholar

    def get_recommendations(
        self,
        db: Session,
        paper_id: int,
        user_id: int,
        limit: int = 5,
    ) -> list[dict]:

        # Find the user's paper
        paper = (
            db.query(Paper)
            .filter(
                Paper.id == paper_id,
                Paper.owner_id == user_id,
            )
            .first()
        )

        if not paper:
            raise ValueError("Paper not found.")

        # Make sure the paper has a DOI
        if not paper.doi:
            raise ValueError(
                "This paper does not have a DOI."
            )

        # Ask Semantic Scholar for recommendations
        recommendations = (
            self.semantic_scholar.recommend_papers(
                paper_id=f"DOI:{paper.doi}",
                limit=limit,
            )
        )

        return recommendations