from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor
from app.features.papers.processing_service import DocumentProcessingService
from app.infrastructure.document_processing.chunker import DocumentChunker




    

def get_document_processing_service() -> DocumentProcessingService:
    storage = LocalStorage()
    pdf_extractor = PDFExtractor()
    chunker = DocumentChunker()

    return DocumentProcessingService(
        storage=storage,
        pdf_extractor=pdf_extractor,
        chunker=chunker,
    )