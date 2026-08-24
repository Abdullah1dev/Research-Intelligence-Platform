from sqlalchemy.orm import Session

from app.features.papers.models import PaperDocument
from app.features.papers.enums import DocumentProcessingStatus

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor

from app.infrastructure.document_processing.chunker import DocumentChunker




#Document Processing Service
class DocumentProcessingService:

    def __init__(
        self,
        storage: LocalStorage,
        pdf_extractor: PDFExtractor,
        chunker: DocumentChunker,
    ):
        self.storage = storage
        self.pdf_extractor = pdf_extractor
        self.chunker = chunker

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

            print("Extracted characters:", len(text))
            print("Total chunks:", len(chunks))

            for index, chunk in enumerate(chunks[:3], start=1):
                print(f"\n--- Chunk {index} ---")
                print(chunk[:500])

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
        
        



#Documemt process background
def process_document_background(document_id: int):
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

        processing_service = DocumentProcessingService(
            storage=storage,
            pdf_extractor=pdf_extractor,
            chunker=chunker,
        )

        processing_service.process_document(
            db=db,
            document=document,
        )

    finally:
        db.close()