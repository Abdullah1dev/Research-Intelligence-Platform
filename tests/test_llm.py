from app.infrastructure.llm.service import LLMService


llm = LLMService()

response = llm.generate(
    "Explain artificial intelligence in one short paragraph."
)

print(response)