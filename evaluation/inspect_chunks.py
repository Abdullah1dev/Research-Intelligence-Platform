from app.features.users.models import User
from app.features.papers.models import Paper, PaperDocument, DocumentChunk
from app.features.conversations.models import Conversation

from app.infrastructure.database.config import SessionLocal


db = SessionLocal()

try:
    chunks = (
        db.query(DocumentChunk)
        .filter(
            DocumentChunk.document_id == 30,
            DocumentChunk.chunk_index.in_([6 , 7 , 9]),
        )
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    for chunk in chunks:
        print("\n" + "=" * 70)
        print(f"CHUNK {chunk.chunk_index}")
        print(f"Chunk ID: {chunk.id}")
        print("=" * 70)
        print(chunk.content)

finally:
    db.close()