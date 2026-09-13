from dataclasses import dataclass


@dataclass
class RetrievalSource:
    chunk_id: int
    chunk_index: int
    content: str
    similarity_score: float


@dataclass
class RetrievalResult:
    context: str
    sources: list[RetrievalSource]