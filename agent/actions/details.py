"""
@file agent/action/details.py
"""


def execution_aborted(at: int, reason: str) -> str:
    """
    Generate a templated response message for the model when execution is aborted.

    This is used to notify the agent that the execution pipeline was interrupted
    at a specific step, providing the reason for the failure.

    :param at:      Index of the action that caused the crash.
    :param reason:  Human-readable description of the failure reason.
    :return:        Formatted message string to be passed back to the model.
    """
    return (f"execution aborted at {at}th\n"
            f"Execution interrupted.\n"
            f"All operations have been cancelled.\n"
            f"No changes were applied.\n"
            f"[reason]: {reason}")
