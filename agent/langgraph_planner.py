from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from groq import Groq
import json

client = Groq()

# -----------------------------
# State
# -----------------------------
class PlannerState(TypedDict):
    user_input: str
    plan: List[dict]


# -----------------------------
# Planner Prompt
# -----------------------------
SYSTEM_PROMPT = """
You are a STRICT planning engine.

Your ONLY job is to decide WHICH tool(s) to call.

Rules:
- Output ONLY valid JSON
- Output a LIST
- Each step MUST be: { "tool": "<tool_name>", "args": {} }
- DO NOT explain
- DO NOT invent tools
- DO NOT add runtime arguments

Allowed tools:
- generate_answer
- retrieve_context
- get_tasks
- create_task
"""


# -----------------------------
# Plan Normalization (CRITICAL)
# -----------------------------
def normalize_plan(plan: list, user_input: str) -> list:
    text = user_input.lower()

    DOC_KEYWORDS = [
        "document",
        "this document",
        "the document",
        "uploaded file",
        "uploaded document",
        "resume",
        "pdf",
    ]

    tools = [step.get("tool") for step in plan]

    # 🔒 Deterministic RAG trigger
    if any(k in text for k in DOC_KEYWORDS):
        if "retrieve_context" not in tools:
            plan.insert(0, {"tool": "retrieve_context", "args": {}})
            tools.insert(0, "retrieve_context")

    # 🔒 If RAG used, ALWAYS follow with generate_answer
    if "retrieve_context" in tools and "generate_answer" not in tools:
        plan.append({"tool": "generate_answer", "args": {}})

    # 🔒 Enforce contract: generate_answer never has args
    for step in plan:
        if step.get("tool") == "generate_answer":
            step["args"] = {}

    return plan


# -----------------------------
# LLM Planner Node
# -----------------------------
def plan_with_llm(state: PlannerState) -> PlannerState:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": state["user_input"]},
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        # 1️⃣ Parse JSON
        plan = json.loads(raw)
        if not isinstance(plan, list):
            raise ValueError("Planner output must be a list")

        # 2️⃣ Normalize semantics (DETERMINISTIC RAG TRIGGER)
        plan = normalize_plan(plan, state["user_input"])


    except Exception:
        # 3️⃣ Safe deterministic fallback
        plan = [{"tool": "generate_answer", "args": {}}]

    return {
        "user_input": state["user_input"],
        "plan": plan,
    }


# -----------------------------
# LangGraph Definition
# -----------------------------
graph = StateGraph(PlannerState)

graph.add_node("planner", plan_with_llm)
graph.set_entry_point("planner")
graph.add_edge("planner", END)

planner_app = graph.compile()


# -----------------------------
# Public API (ENGINE CALLS THIS)
# -----------------------------
def generate_plan(user_input: str) -> list:
    result = planner_app.invoke(
        {
            "user_input": user_input,
            "plan": [],
        }
    )
    return result["plan"]
