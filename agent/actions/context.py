"""
@file agent/actions/context.py
"""

from typing import List

from actions.verdict import ActionVerdict


class Context:
    """
    Execution context used by the dispatcher during a transaction cycle.

    Maintains the history of executed actions and their results.
    """

    def __init__(self):
        """
        Initialize an empty context.
        """
        self._verdicts: List[ActionVerdict] = []

    @property
    def verdicts(self) -> List[ActionVerdict]:
        """
        Get the list of all verdicts recorded in this context.

        :return:    List of execution verdicts.
        """
        return self._verdicts

    @property
    def done(self) -> int:
        """
        Get the number of executed actions recorded.

        :return:    Total count of verdicts.
        """
        return len(self._verdicts)

    def mark_execution_result(self, verdict: ActionVerdict) -> None:
        """
        Record the verdict of the most recently executed action.

        Appends the verdict to the internal history list.

        :param verdict: The result of the last executed action.
        :return:        None
        """
        self._verdicts.append(verdict)

    def clear(self) -> None:
        """
        Clear all recorded verdicts from the context.

        Resets the execution history.
        """
        self._verdicts.clear()
