import json

from app.infrastructure.llm.service import LLMService


class AnalysisService:

    def __init__(
        self,
        llm_service: LLMService,
        max_characters: int = 12000,
    ):
        self.llm_service = llm_service
        self.max_characters = max_characters

    def analyze(
        self,
        text: str,
    ) -> dict:

        if not text or not text.strip():
            raise ValueError(
                "No content available for analysis"
            )

        document_text = text[
            :self.max_characters
        ]

        prompt = f"""
You are an AI research paper analysis assistant.

Analyze the provided document and extract research
information.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "research_domain": "...",
    "key_topics": [
        "...",
        "..."
    ],
    "methodology": "...",
    "key_findings": [
        "...",
        "..."
    ],
    "limitations": "...",
    "future_work": "..."
}}

Rules:

- Use ONLY the provided document.
- Do not invent information.
- If information is not available, use:
  "Not clearly stated in the document."
- Return valid JSON only.
- Do not use markdown.
- Do not add explanations outside JSON.

Document Content:

{document_text}
"""

        response = self.llm_service.generate(
            prompt
        )

        try:
            return json.loads(response)

        except json.JSONDecodeError:
            raise ValueError(
                "LLM returned invalid JSON"
            )