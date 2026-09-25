
from sqlalchemy.orm import Session

from app.features.papers.models import (
    PaperDocument,
    DocumentChunk,
)
from app.features.papers.enums import DocumentProcessingStatus

from app.infrastructure.database.config import SessionLocal
from app.infrastructure.storage.local import LocalStorage
from app.infrastructure.document_processing.pdf import PDFExtractor
from app.infrastructure.document_processing.chunker import DocumentChunker
from app.infrastructure.embeddings.service import EmbeddingService


# ============================================================
# Document Processing Service
# ============================================================

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

        print("\n====================================")
        print("STARTING DOCUMENT PROCESSING")
        print("Document ID:", document.id)
        print("Storage Key:", document.storage_key)
        print("====================================")

        document.processing_status = (
            DocumentProcessingStatus.PROCESSING
        )

        db.commit()
        db.refresh(document)

        try:
            # ------------------------------------------------
            # 1. Get PDF path
            # ------------------------------------------------

            print("\n========== GETTING PDF PATH ==========")

            file_path = self.storage.get_path(
                document.storage_key
            )

            print("PDF path:", file_path)

            # ------------------------------------------------
            # 2. Extract text
            # ------------------------------------------------

            print("\n========== EXTRACTING TEXT ==========")

            text = self.pdf_extractor.extract_text(
                str(file_path)
            )

            print("Extracted characters:", len(text))

            if not text.strip():
                raise ValueError(
                    "No text could be extracted from the PDF"
                )

            # ------------------------------------------------
            # 3. Split text into chunks
            # ------------------------------------------------

            print("\n========== CHUNKING DOCUMENT ==========")

            chunks = self.chunker.split_text(text)

            print("Total chunks:", len(chunks))

            if not chunks:
                raise ValueError(
                    "No chunks were created from the extracted text"
                )

            for index, chunk in enumerate(
                chunks[:3],
                start=1,
            ):
                print(f"\n--- Chunk {index} ---")
                print("Length:", len(chunk))
                print(chunk[:500])

            # ------------------------------------------------
            # 4. Generate embeddings
            # ------------------------------------------------

            print("\n========== GENERATING EMBEDDINGS ==========")
            print("Chunks sent for embedding:", len(chunks))

            embeddings = (
                self.embedding_service.embed_documents(
                    chunks
                )
            )

            print(
                "Total embeddings generated:",
                len(embeddings),
            )

            if embeddings:
                print(
                    "Embedding dimensions:",
                    len(embeddings[0]),
                )

            if len(chunks) != len(embeddings):
                raise ValueError(
                    "Number of embeddings does not match "
                    "number of chunks"
                )

            # ------------------------------------------------
            # 5. Insert chunks into database
            # ------------------------------------------------

            print("\n====================================")
            print("INSERTING CHUNKS INTO DATABASE")
            print("====================================")

            print("Document ID:", document.id)
            print("Chunks to insert:", len(chunks))
            print("Embeddings to insert:", len(embeddings))

            for index, (chunk, embedding) in enumerate(
                zip(chunks, embeddings)
            ):
                print(f"\nCreating chunk {index}")

                print(
                    "Content length:",
                    len(chunk),
                )

                print(
                    "Embedding dimensions:",
                    len(embedding),
                )

                document_chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embedding,
                )

                db.add(document_chunk)

            print(
                "\nAll chunks added to SQLAlchemy session."
            )

            # ------------------------------------------------
            # 6. Commit chunks
            # ------------------------------------------------

            print("\n========== COMMITTING CHUNKS ==========")

            db.commit()

            print(
                "========== CHUNKS COMMITTED SUCCESSFULLY =========="
            )

            # ------------------------------------------------
            # 7. Verify chunks were actually saved
            # ------------------------------------------------

            print("\n========== VERIFYING DATABASE ==========")

            saved_chunks = (
                db.query(DocumentChunk)
                .filter(
                    DocumentChunk.document_id
                    == document.id
                )
                .order_by(
                    DocumentChunk.chunk_index
                )
                .all()
            )

            print(
                "Chunks actually saved:",
                len(saved_chunks),
            )

            for saved_chunk in saved_chunks[:5]:
                print(
                    f"Chunk ID: {saved_chunk.id} | "
                    f"Document ID: {saved_chunk.document_id} | "
                    f"Index: {saved_chunk.chunk_index}"
                )

            # ------------------------------------------------
            # 8. Mark document as completed
            # ------------------------------------------------

            document.processing_status = (
                DocumentProcessingStatus.COMPLETED
            )

            document.processing_error = None

            db.commit()
            db.refresh(document)

            print("\n====================================")
            print("DOCUMENT PROCESSING COMPLETED")
            print("Document ID:", document.id)
            print("Final chunk count:", len(saved_chunks))
            print("====================================\n")

            return text

        except Exception as exc:

            print("\n🔥🔥🔥 PROCESSING ERROR 🔥🔥🔥")
            print(
                "Error type:",
                type(exc).__name__,
            )
            print(
                "Error message:",
                str(exc),
            )
            print("🔥🔥🔥 END PROCESSING ERROR 🔥🔥🔥\n")

            # Roll back any failed database transaction
            db.rollback()

            document.processing_status = (
                DocumentProcessingStatus.FAILED
            )

            document.processing_error = str(exc)

            db.commit()
            db.refresh(document)

            raise


# ============================================================
# Background Document Processing
# ============================================================

def process_document_background(document_id: int):

    print("\n🔥🔥🔥 THIS IS THE BACKGROUND FUNCTION 🔥🔥🔥")
    print(f"DOCUMENT ID = {document_id}")

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # 1. Find document
        # ----------------------------------------------------

        document = (
            db.query(PaperDocument)
            .filter(
                PaperDocument.id == document_id
            )
            .first()
        )

        if not document:
            print(
                f"Document {document_id} not found"
            )
            return

        print(
            f"Found document {document.id}"
        )

        # ----------------------------------------------------
        # 2. Initialize services
        # ----------------------------------------------------

        storage = LocalStorage()

        pdf_extractor = PDFExtractor()

        chunker = DocumentChunker()

        print("\n========== INITIALIZING EMBEDDING SERVICE ==========")

        embedding_service = EmbeddingService()

        print(
            "Embedding service initialized successfully."
        )

        # ----------------------------------------------------
        # 3. Create processing service
        # ----------------------------------------------------

        processing_service = DocumentProcessingService(
            storage=storage,
            pdf_extractor=pdf_extractor,
            chunker=chunker,
            embedding_service=embedding_service,
        )

        # ----------------------------------------------------
        # 4. Process document
        # ----------------------------------------------------

        processing_service.process_document(
            db=db,
            document=document,
        )

        print(
            f"\nBackground processing finished "
            f"for document {document_id}"
        )

    except Exception as exc:

        print(
            "\n🔥🔥🔥 BACKGROUND PROCESSING FAILED 🔥🔥🔥"
        )

        print(
            "Error type:",
            type(exc).__name__,
        )

        print(
            "Error message:",
            str(exc),
        )

        print(
            "🔥🔥🔥 END BACKGROUND ERROR 🔥🔥🔥"
        )

    finally:

        db.close()

        print(
            f"Database session closed for "
            f"document {document_id}"
        )

