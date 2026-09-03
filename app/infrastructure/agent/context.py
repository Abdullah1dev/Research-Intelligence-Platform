from dataclasses import dataclass

from sqlalchemy.orm import Session


@dataclass
class ResearchAgentContext:

    db: Session