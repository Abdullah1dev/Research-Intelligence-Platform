from app.infrastructure.document_processing.pdf import PDFExtractor


extractor = PDFExtractor()

text = extractor.extract_text(
    "storage/papers/10/501eadc8-5362-4599-8465-0fdfb1578834.pdf"
)

print("Extracted characters:", len(text))
print(text[:1000])

