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

        # Resolve Semantic Scholar ID if it hasn't been stored yet
        if not paper.semantic_scholar_id:

            semantic_paper = (
                self.semantic_scholar.search_paper(
                    title=paper.title,
                )
            )

            if not semantic_paper:
                raise ValueError(
                    "Paper could not be found in Semantic Scholar."
                )

            semantic_paper_id = semantic_paper.get(
                "paperId"
            )

            if not semantic_paper_id:
                raise ValueError(
                    "Semantic Scholar paper ID was not returned."
                )

            # Save the resolved ID for future requests
            paper.semantic_scholar_id = semantic_paper_id

            db.commit()

        else:
            semantic_paper_id = paper.semantic_scholar_id

        # Get recommendations using the Semantic Scholar paper ID
        recommendations = (
            self.semantic_scholar.recommend_papers(
                paper_id=semantic_paper_id,
                limit=limit,
            )
        )

        return recommendations