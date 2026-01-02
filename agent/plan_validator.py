# agent/plan_validator.py

from agent.tool_registry import TOOLS

MAX_PLAN_STEPS = 5

# Tool contracts: required + optional args
TOOL_CONTRACTS = {
    "generate_answer": {
        "required": set(),
        "optional": set(),   # engine injects question + context
    },
    "retrieve_context": {
        "required": set(),   # engine injects query + user_id
        "optional": set(),
    },
    "get_tasks": {
        "required": set(),   # engine injects db + user_id
        "optional": set(),
    },
    "create_task": {
        "required": {"title"},   # planner responsibility
        "optional": {"description"},
    },
}


def validate_plan(plan: list) -> None:
    # -------------------------------
    # BASIC STRUCTURE
    # -------------------------------
    if not isinstance(plan, list):
        raise ValueError("Plan must be a list")

    if len(plan) == 0:
        raise ValueError("Plan cannot be empty")

    if len(plan) > MAX_PLAN_STEPS:
        raise ValueError(f"Plan exceeds max allowed steps ({MAX_PLAN_STEPS})")

    # -------------------------------
    # STEP VALIDATION
    # -------------------------------
    for i, step in enumerate(plan):
        if not isinstance(step, dict):
            raise ValueError(f"Plan step {i} must be a dict")

        if "tool" not in step:
            raise ValueError(f"Plan step {i} missing 'tool'")

        if "args" not in step:
            raise ValueError(f"Plan step {i} missing 'args'")

        tool = step["tool"]
        args = step["args"]

        if not isinstance(tool, str):
            raise ValueError(f"Tool name at step {i} must be a string")

        if tool not in TOOLS:
            raise ValueError(f"Tool '{tool}' is not registered")

        if tool not in TOOL_CONTRACTS:
            raise ValueError(f"Tool '{tool}' is not allowed by contract")

        if not isinstance(args, dict):
            raise ValueError(f"Args for tool '{tool}' must be a dict")

        contract = TOOL_CONTRACTS[tool]

        # -------------------------------
        # REQUIRED ARGS
        # -------------------------------
        missing = contract["required"] - args.keys()
        if missing:
            raise ValueError(
                f"Missing required args for tool '{tool}': {missing}"
            )

        # -------------------------------
        # NO EXTRA ARGS
        # -------------------------------
        allowed_args = contract["required"] | contract["optional"]
        extra = set(args.keys()) - allowed_args
        if extra:
            raise ValueError(
                f"Invalid args for tool '{tool}': {extra}"
            )
