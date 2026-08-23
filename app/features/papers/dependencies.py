from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor
from app.features.papers.processing_service import DocumentProcessingService


def get_document_processing_service() -> DocumentProcessingService:
    storage = LocalStorage()
    pdf_extractor = PDFExtractor()

    return DocumentProcessingService(
        storage=storage,
        pdf_extractor=pdf_extractor,
    )