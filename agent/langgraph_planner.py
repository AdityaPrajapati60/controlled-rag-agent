# agent/langgraph_planner.py

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
# Plan Normalization (AUTHORITATIVE)
# -----------------------------
def normalize_plan(plan: list, user_input: str) -> list:
    text = user_input.lower()

    DOC_KEYWORDS = [
        "document",
        "resume",
        "pdf",
        "uploaded",
        "file",
        "this document",
        "my document",
    ]

    tools = [step.get("tool") for step in plan]

    # ------------------------------------------------
    # FORCE RAG FOR DOCUMENT QUESTIONS
    # ------------------------------------------------
    if any(k in text for k in DOC_KEYWORDS):
        if "retrieve_context" not in tools:
            plan.insert(0, {"tool": "retrieve_context", "args": {}})
            tools.insert(0, "retrieve_context")

    normalized = []

    for step in plan:
        tool = step.get("tool")
        raw_args = step.get("args", {}) or {}

        # -----------------------------
        # generate_answer / retrieve_context / get_tasks
        # -----------------------------
        if tool in {"generate_answer", "retrieve_context", "get_tasks"}:
            normalized.append({"tool": tool, "args": {}})
            continue

        # -----------------------------
        # create_task (TITLE REQUIRED)
        # -----------------------------
        if tool == "create_task":
            title = (
                raw_args.get("title")
                or raw_args.get("task_name")
                or raw_args.get("task")
                or user_input.strip()        # 🔒 fallback
            )

            description = (
                raw_args.get("description")
                or raw_args.get("task_description")
            )

            normalized.append(
                {
                    "tool": "create_task",
                    "args": {
                        "title": title,
                        "description": description,
                    },
                }
            )
            continue

        # -----------------------------
        # unknown tool (pass-through)
        # -----------------------------
        normalized.append({"tool": tool, "args": raw_args})

    # ------------------------------------------------
    # ENSURE generate_answer IS LAST
    # ------------------------------------------------
    if not any(step["tool"] == "generate_answer" for step in normalized):
        normalized.append({"tool": "generate_answer", "args": {}})

    return normalized


# -----------------------------
# LLM Planner Node
# -----------------------------
def plan_with_llm(state: PlannerState) -> PlannerState:
    raw_plan = []

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": state["user_input"]},
            ],
        )

        raw = response.choices[0].message.content.strip()
        raw_plan = json.loads(raw)

        if not isinstance(raw_plan, list):
            raw_plan = []

    except Exception:
        # ❌ DO NOT return here
        raw_plan = []

    # ✅ ALWAYS normalize — even if LLM failed
    final_plan = normalize_plan(raw_plan, state["user_input"])

    return {
        "user_input": state["user_input"],
        "plan": final_plan,
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
