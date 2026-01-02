# agent/answer_generator.py

from groq import Groq

client = Groq()


def generate_answer(question: str = "", context: str | None = None) -> str:
    if not question:
        return "No question provided."

    system_prompt = """
You are a helpful and honest assistant.

Rules:
- If document context is provided:
  - NEVER say that no document was provided.
  - If the document does not contain enough information to answer the question,
    say this clearly and briefly.
  - Do NOT hallucinate details that are not present in the document.
- If no document context is provided:
  - Answer normally using general knowledge.

Be concise, factual, and clear.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append(
            {
                "role": "system",
                "content": f"Document context (may be incomplete):\n{context}",
            }
        )

    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
