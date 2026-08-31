from app.infrastructure.llm.service import LLMService


class SummarizationService:

    def __init__(
        self,
        llm_service: LLMService,
        max_characters: int = 12000,
    ):
        self.llm_service = llm_service
        self.max_characters = max_characters

    def summarize(
        self,
        text: str,
    ) -> str:

        if not text or not text.strip():
            return "No content available for summarization."

        # Limit the text sent to the LLM
        document_text = text[
            :self.max_characters
        ]

        prompt = f"""
You are an AI research paper assistant.

Analyze the following research paper content and provide
a clear and concise summary.

Your response should include:

1. Summary
2. Main Objective
3. Key Findings
4. Key Contributions

Use only the provided document content.

Do not invent information that is not present
in the document.

Document Content:
{document_text}

Response:
"""

        summary = self.llm_service.generate(
            prompt
        )

        return summary.strip()