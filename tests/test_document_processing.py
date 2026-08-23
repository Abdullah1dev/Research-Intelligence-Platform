from app.infrastructure.database.session import SessionLocal
from app.features.papers.models import PaperDocument
from app.features.papers.service import DocumentProcessingService
from app.features.papers.enums import DocumentProcessingStatus
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor

#C:\Users\Laptop Arena\OneDrive\Documents\Research Intelligence Platform\app\infrastructure\database\config.py
#C:\Users\Laptop Arena\OneDrive\Documents\Research Intelligence Platform\app\features\papers\service.py
#C:\Users\Laptop Arena\OneDrive\Documents\Research Intelligence Platform\app\infrastructure\storage\local.py
db = SessionLocal()

storage = LocalStorage()
extractor = PDFExtractor()

service = DocumentProcessingService(
    storage=storage,
    pdf_extractor=extractor,
)

try:
    document = db.query(PaperDocument).filter(
        PaperDocument.id == 10
    ).first()

    if not document:
        print("Document not found")
    else:
        print("Document:", document.file_name)
        print("Initial status:", document.processing_status)

        text = service.process_document(
            db=db,
            document=document,
        )

        print("Final status:", document.processing_status)
        print("Extracted characters:", len(text))
        print(text[:500])

finally:
    db.close()