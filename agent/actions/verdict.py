"""
@file agent/actions/verdict.py
"""

from enum import Enum
from typing import Dict, Any


class ExitCode(Enum):
    """
    результаты выполнения действия
    """

    SUCCESS = "success"
    NO_ACTION_SELECTED = "no_action_selected"
    LOGIC_ERROR = "logic_error"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    MISSED_ARGUMENT = "missed_argument"
    INVALID_ARGUMENT = "invalid_argument"
    EXECUTION_ERROR = "execution_error"
    PROTOCOL_ERROR = "protocol_error"

    def __str__(self):
        return self.value


class ActionVerdict:
    """
    представление результата действия агента
    """

    def __init__(self,
                 code: ExitCode,
                 details: str = "",
                 result: Dict[str, Any] = {}):
        """
        инициализация себя
        :param code:    код возврата
        :param details: детали выполнения
        :param result:  полезная нагрузка, данные
        """
        self.code = code
        self.details = details
        self.result = result


    @property
    def success(self) -> bool:
        return self.code is ExitCode.SUCCESS


    def to_json(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "details": self.details,
            "result": self.result,
        }


    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ActionVerdict":
        return cls(
            code=ExitCode(data["code"]),
            details=data.get("details", ""),
            result=data.get("result", {}),
        )


    def __bool__(self) -> bool:
        return self.success
