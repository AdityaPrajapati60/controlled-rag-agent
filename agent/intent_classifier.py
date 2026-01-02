# agent/intent_classifier.py

import json
from groq import Groq

client = Groq()  # uses GROQ_API_KEY from env

SYSTEM_PROMPT = """
You are an intent classifier.

Classify the user input into ONE intent:

- CREATE_TASK → user explicitly asks to create/add a task
- LIST_TASKS → user asks to list/show tasks
- ASK_DOC → user asks about resume, documents, skills, qualification
- ANSWER → everything else

Rules:
- Do NOT guess.
- Do NOT hallucinate.
- CREATE_TASK only if explicit.

If intent is CREATE_TASK, extract:
{
  "intent": "CREATE_TASK",
  "task": {
    "title": "...",
    "description": "..."
  }
}

Return ONLY valid JSON.
"""

VALID_INTENTS = {"CREATE_TASK", "LIST_TASKS", "ASK_DOC", "ANSWER"}

def classify_intent(user_input: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        if not content:
            return {"intent": "ANSWER"}

        data = json.loads(content)

        intent = data.get("intent")
        if intent not in VALID_INTENTS:
            return {"intent": "ANSWER"}

        if intent == "CREATE_TASK":
            task = data.get("task") or {}
            return {
                "intent": "CREATE_TASK",
                "task": {
                    "title": task.get("title"),
                    "description": task.get("description"),
                },
            }

        return {"intent": intent}

    except Exception:
        # ABSOLUTE GUARANTEE
        return {"intent": "ANSWER"}
