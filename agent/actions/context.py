"""
@file agent/actions/context.py
"""

from typing import List

from actions.verdict import ActionVerdict


class Context:
    """
    dispatcher used context
    используется диспатчером во
    время цикла выполнения транзакции
    """

    def __init__(self):
        """
        инициализация себя
        """
        self._verdicts = []

    @property
    def verdicts(self) -> List[ActionVerdict]:
        return self._verdicts

    @property
    def done(self) -> int:
        return len(self._verdicts)

    def mark_execution_result(self, verdict) -> None:
        """
        регистрация последнего выполненного действия
        :param verdict: результат последнего действия
        :return:    ничего
        """
        self._verdicts.append(verdict)

    def clear(self) -> None:
        """
        очистка контекста
        """
        self._verdicts.clear()
