"""
@file agent/actions/verdict.py
"""

from enum import Enum


class ExitCode(Enum):
    SUCCESS = "success"
    NO_ACTION_SELECTED = "no_action_selected"
    LOGIC_ERROR = "logic_error"
    PERMISSION_DENIED = "permission_denied"
    INVALID_ARGUMENT = "invalid_argument"
    EXECUTION_ERROR = "execution_error"


class ActionVerdict:

    def __init__(self, code: ExitCode, details: str = ""):
        self.code = code
        self.details = details


    @property
    def success(self) -> bool:
        return self.code is ExitCode.SUCCESS


    def to_json(self) -> dict:
        return {
            "code": self.code.value,
            "details": self.details,
        }


    @classmethod
    def from_json(cls, data: dict) -> "ActionVerdict":
        return cls(
            code=ExitCode(data["code"]),
            details=data.get("details", ""),
        )


    def __bool__(self) -> bool:
        return self.success
