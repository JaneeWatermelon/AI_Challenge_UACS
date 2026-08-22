"""
@file agent/actions/context.py
"""

from typing import List

from AI_Challenge_UACS.agent.actions.verdict import ActionVerdict


class Context:
    """
    dispatcher used context
    """

    def __init__(self):
        self._verdicts = []


    @property
    def verdicts(self) -> List[ActionVerdict]:
        return self._verdicts


    @property
    def done(self) -> int:
        return len(self._verdicts)


    def mark_execution_result(self, verdict) -> None:
        self._verdicts.append(verdict)


    def clear(self) -> None:
        self._verdicts.clear()
