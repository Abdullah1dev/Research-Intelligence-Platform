from sqlalchemy.orm import Session

from app.features.papers.models import PaperDocument
from app.features.papers.enums import DocumentProcessingStatus

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor

from app.infrastructure.document_processing.chunker import DocumentChunker
from app.infrastructure.embeddings.service import EmbeddingService

from app.features.papers.models import (
    PaperDocument,
    DocumentChunk,
)


#Document Processing Service
class DocumentProcessingService:

    def __init__(
        self,
        storage: LocalStorage,
        pdf_extractor: PDFExtractor,
        chunker: DocumentChunker,
        embedding_service: EmbeddingService,
    ):
        self.storage = storage
        self.pdf_extractor = pdf_extractor
        self.chunker = chunker
        self.embedding_service = embedding_service

    def process_document(
        
        self,
        db: Session,
        document: PaperDocument,
    ) -> str:

        document.processing_status = (
            DocumentProcessingStatus.PROCESSING
        )

        db.commit()
        db.refresh(document)

        try:
            file_path = self.storage.get_path(
                document.storage_key
            )

            text = self.pdf_extractor.extract_text(
                str(file_path)
            )

            chunks = self.chunker.split_text(text)

            if not chunks:
                raise ValueError(
                    "No text could be extracted from the PDF"
                )

            embeddings = self.embedding_service.embed_documents(
                chunks
            )

            if len(chunks) != len(embeddings):
                raise ValueError(
                    "Number of embeddings does not match "
                    "number of chunks"
                )

            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            ):
                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                )

                db.add(document_chunk)

            db.commit()

            print(
                "Extracted characters:",
                len(text),
            )

            print(
                "Total chunks:",
                len(chunks),
            )

            print(
                "Total embeddings:",
                len(embeddings),
            )

            for index, chunk in enumerate(
                chunks[:3],
                start=1,
            ):
                print(
                    f"\n--- Chunk {index} ---"
                )

                print(
                    chunk[:500]
                )

            document.processing_status = (
                DocumentProcessingStatus.COMPLETED
            )

            document.processing_error = None

            db.commit()
            db.refresh(document)

            return text

        except Exception as exc:
            document.processing_status = (
                DocumentProcessingStatus.FAILED
            )

            document.processing_error = str(exc)

            db.commit()
            db.refresh(document)

            raise


#Background Document Processing
def process_document_background(document_id: int):
    print("🔥🔥🔥 THIS IS THE BACKGROUND FUNCTION 🔥🔥🔥")
    print(f"DOCUMENT ID = {document_id}")
    db = SessionLocal()

    try:
        document = (
            db.query(PaperDocument)
            .filter(PaperDocument.id == document_id)
            .first()
        )

        if not document:
            print(f"Document {document_id} not found")
            return

        storage = LocalStorage()
        pdf_extractor = PDFExtractor()
        chunker = DocumentChunker()
        print("GENERATING EMBEDDINGS...")
        embedding_service = EmbeddingService()
        print("GENERATING EMBEDDINGS...")

        processing_service = DocumentProcessingService(
            storage=storage,
            pdf_extractor=pdf_extractor,
            chunker=chunker,
            embedding_service=embedding_service,
        )

        processing_service.process_document(
            db=db,
            document=document,
        )

    except Exception as exc:
        print(
            f"Document processing failed: {exc}"
        )

    finally:
        db.close()