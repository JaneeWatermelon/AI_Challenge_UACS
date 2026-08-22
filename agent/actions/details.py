"""
@file agent/action/details.py
"""


def execution_aborted(at: int, reason: str) -> str:
    return (f"execution aborted at {at}th\n"
            f"Execution interrupted.\n"
            f"All operations have been cancelled.\n"
            f"No changes were applied.\n"
            f"[reason]: {reason}")

