# agent/tool_registry.py

from typing import Callable, Dict, Any

from agent.task_tools import get_tasks, create_task
from rag.retrieve import retrieve_context
from agent.answer_generator import generate_answer


# ------------------------------------------------------------------
# Tool registry
# ------------------------------------------------------------------
# Single source of truth for:
# - What the agent can do
# - How tools are called
# - What arguments are expected
#
# No decorators
# No classes
# No frameworks
# ------------------------------------------------------------------

TOOLS: Dict[str, Callable[..., Any]] = {
    "create_task": create_task,
    "get_tasks": get_tasks,
    "retrieve_context": retrieve_context,
    "generate_answer": generate_answer,
}


# ------------------------------------------------------------------
# Optional helper (NOT REQUIRED, but safe)
# ------------------------------------------------------------------

def get_tool(tool_name: str) -> Callable[..., Any]:
    """
    Fetch a tool from the registry.
    Raises KeyError if tool does not exist.
    """
    try:
        return TOOLS[tool_name]
    except KeyError:
        raise KeyError(f"Tool '{tool_name}' is not registered")
