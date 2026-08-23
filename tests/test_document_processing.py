from app.features.papers.service import DocumentProcessingService
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor


storage = LocalStorage()
extractor = PDFExtractor()

service = DocumentProcessingService(
    storage=storage,
    pdf_extractor=extractor,
)

print("DocumentProcessingService created successfully")