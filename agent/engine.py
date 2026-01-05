# agent/engine.py

from models.agent_run import AgentRun
from models.agent_action import AgentAction
from models.planner_plan import PlannerPlan

from agent.execution_limits import enforce_run_limit, AgentRateLimitError
from agent.tool_permissions import is_tool_allowed
from agent.tool_registry import TOOLS
from agent.plan_validator import validate_plan
from agent.langgraph_planner import generate_plan
from agent.intent_classifier import classify_intent
from agent.tool_timeout import time_limit, ToolTimeout

import os


# ------------------------------------------------
# TOKEN / COST CONFIG
# ------------------------------------------------
MAX_TOKENS_PER_RUN = 2000
AVG_TOKENS_PER_CHAR = 0.25
MAX_PROMPT_CHARS = 3000


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return int(len(text) * AVG_TOKENS_PER_CHAR)


# ------------------------------------------------
# RAG GATE — ENGINE IS THE ONLY AUTHORITY
# ------------------------------------------------
def is_rag_allowed(prompt: str) -> bool:
    prompt = prompt.lower()
    RAG_KEYWORDS = {
        "document",
        "resume",
        "pdf",
        "uploaded",
        "upload",
        "file",
        "my document",
        "this document",
    }
    return any(k in prompt for k in RAG_KEYWORDS)


# ------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------
def run_agent(prompt: str, user, db):

    # ------------------------------------------------
    # 0. OPS KILL SWITCH
    # ------------------------------------------------
    if os.getenv("AGENT_ENABLED", "true").lower() != "true":
        return {"error": "Agent disabled by ops"}

    # ------------------------------------------------
    # 0.5 HARD INPUT LIMIT
    # ------------------------------------------------
    if len(prompt) > MAX_PROMPT_CHARS:
        return {
            "error": "Prompt exceeds maximum allowed length",
            "budget_exceeded": True,
        }

    # ------------------------------------------------
    # 1. RATE LIMIT
    # ------------------------------------------------
    try:
        enforce_run_limit(db, user.id)
    except AgentRateLimitError as e:
        return {"error": str(e), "status": 429}

    # ------------------------------------------------
    # 2. CREATE AGENT RUN
    # ------------------------------------------------
    run = AgentRun(
        user_id=user.id,
        input=prompt,
        estimated_tokens_used=0,
        budget_exceeded=False,
    )
    db.add(run)
    db.flush()

    run.estimated_tokens_used += estimate_tokens(prompt)

    # ------------------------------------------------
    # 3. INTENT CLASSIFIER (LOGGING ONLY)
    # ------------------------------------------------
    intent_data = classify_intent(prompt) or {"intent": "ANSWER"}

    db.add(
        AgentAction(
            run_id=run.id,
            tool_name="intent_classifier",
            tool_input=prompt,
            tool_output=str(intent_data),
            status="success",
        )
    )

    # ------------------------------------------------
    # 4. PLANNING (LANGGRAPH)
    # ------------------------------------------------
    try:
        plan = generate_plan(prompt)
        validate_plan(plan)
    except Exception as e:
        run.output = f"ERROR: Planning failed: {str(e)}"
        db.commit()
        return {"error": run.output}

    # 🔎 DEBUG — PLANNER OUTPUT
    print("DEBUG PLAN:", plan)

    db.add(
        AgentAction(
            run_id=run.id,
            tool_name="planner",
            tool_input=prompt,
            tool_output=str(plan),
            status="success",
        )
    )

    # ------------------------------------------------
    # 4.5 STORE PLANNER STEPS
    # ------------------------------------------------
    planner_steps = []

    for idx, step in enumerate(plan):
        db_step = PlannerPlan(
            run_id=run.id,
            step_index=idx,
            tool_name=step["tool"],
            tool_args=step.get("args", {}),
            status="pending",
        )
        db.add(db_step)
        planner_steps.append(db_step)

    db.flush()

    # ------------------------------------------------
    # 5. EXECUTION LOOP
    # ------------------------------------------------
    result = None
    context = None

    for step in planner_steps:
        tool_name = step.tool_name
        raw_args = step.tool_args

        is_tool_allowed(user, tool_name)

        if tool_name not in TOOLS:
            result = f"ERROR: Tool '{tool_name}' not registered"
            break

        tool_fn = TOOLS[tool_name]

        # -------- ARG INJECTION --------
        if tool_name == "retrieve_context":
            args = {"query": prompt, "user_id": user.id}

        elif tool_name == "generate_answer":
            args = {"question": prompt, "context": context}

        elif tool_name == "get_tasks":
            args = {"db": db, "user_id": user.id}

        elif tool_name == "create_task":
            args = {
                "db": db,
                "user_id": user.id,
                "title": raw_args.get("title"),
                "description": raw_args.get("description"),
            }
        else:
            args = raw_args

        # -------- EXECUTE TOOL --------
        try:
            with time_limit(10):
                result = tool_fn(**args)
        except ToolTimeout:
            result = f"ERROR: Tool '{tool_name}' timed out"
            break
        except Exception as e:
            result = f"ERROR: Tool '{tool_name}' failed: {str(e)}"
            break
        if tool_name == "create_task":
            run.output = str(result)
            db.commit()
            return {
                "result": result,
                "estimated_tokens_used": run.estimated_tokens_used,
                "budget_exceeded": run.budget_exceeded,
            }

        # -------- RAG HANDLING --------
        if tool_name == "retrieve_context":

            #  No document exists
            if result is None:
                run.output = "No document is available to answer this question."
                db.commit()
                return {
                    "result": run.output,
                    "rag_used": True,
                }

            # ✅ Document exists ("" or text)
            context = result

        db.add(
            AgentAction(
                run_id=run.id,
                tool_name=tool_name,
                tool_input=str(args),
                tool_output=str(result),
                status="success",
            )
        )

    # ------------------------------------------------
    # 5.5 GUARANTEED FALLBACK (ENGINE-CONTROLLED)
    # ------------------------------------------------
    if result is None:

        # 🔒 Document questions NEVER fallback
        if is_rag_allowed(prompt):
            run.output = "The document does not contain information related to this question."
            db.commit()
            return {
                "result": run.output,
                "rag_used": True,
            }

        # ✅ Safe fallback for non-document questions
        result = TOOLS["generate_answer"](question=prompt, context=None)

    # ------------------------------------------------
    # 6. FINALIZE
    # ------------------------------------------------
    run.output = str(result)
    db.commit()

    if isinstance(result, str) and result.startswith("ERROR"):
        return {"error": result}

    return {
        "result": result,
        "estimated_tokens_used": run.estimated_tokens_used,
        "budget_exceeded": run.budget_exceeded,
    }
