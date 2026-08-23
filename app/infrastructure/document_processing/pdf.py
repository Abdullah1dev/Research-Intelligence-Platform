import fitz
from pathlib import Path


class PDFExtractor:

    def extract_text(self, file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {file_path}"
            )

        text_parts = []

        with fitz.open(path) as document:
            for page in document:
                text_parts.append(page.get_text())

        return "\n".join(text_parts)