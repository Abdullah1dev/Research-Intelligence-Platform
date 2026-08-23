from app.infrastructure.database.session import SessionLocal
from app.features.papers.models import PaperDocument
from app.features.papers.service import DocumentProcessingService
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor

#C:\Users\Laptop Arena\OneDrive\Documents\Research Intelligence Platform\app\features\papers\service.py
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
        # Save the real storage key
        original_storage_key = document.storage_key

        # Give the service a path that does not exist
        document.storage_key = "papers/10/non_existing_file.pdf"

        try:
            service.process_document(
                db=db,
                document=document,
            )

        except Exception as exc:
            print("Processing failed as expected")
            print("Error:", exc)

        print("Final status:", document.processing_status)
        print("Processing error:", document.processing_error)

        # Restore the real storage key
        document.storage_key = original_storage_key
        db.commit()

finally:
    db.close()