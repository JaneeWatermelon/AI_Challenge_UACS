"""
@file agent/actions/verdict.py
"""

from enum import Enum
from typing import Dict, Any


class ExitCode(Enum):
    """
    Exit codes representing the outcome of an action execution.

    These codes provide a standardized way to communicate
    success or failure with specific error categories.
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
    Representation of an agent action result.

    Encapsulates the exit code, human-readable details,
    and optional payload data from the action execution.
    """

    def __init__(self,
                 code: ExitCode,
                 details: str = "",
                 result: Dict[str, Any] = {}):
        """
        Initialize the verdict.

        :param code:    Exit code indicating the outcome.
        :param details: Human-readable execution details.
        :param result:  Optional payload data from the action.
        """
        self.code = code
        self.details = details
        self.result = result

    @property
    def success(self) -> bool:
        """
        Check if the action completed successfully.

        :return:    True if the exit code is SUCCESS, otherwise False.
        """
        return self.code is ExitCode.SUCCESS

    def to_json(self) -> Dict[str, Any]:
        """
        Serialize the verdict to a JSON-compatible dictionary.

        :return:    Dictionary representation of the verdict.
        """
        return {
            "code": self.code.value,
            "details": self.details,
            "result": self.result,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "ActionVerdict":
        """
        Deserialize a verdict from a JSON-compatible dictionary.

        :param data:    Dictionary containing serialized verdict data.
        :return:        A new ActionVerdict instance.
        """
        return cls(
            code=ExitCode(data["code"]),
            details=data.get("details", ""),
            result=data.get("result", {}),
        )

    def __bool__(self) -> bool:
        """
        Boolean evaluation of the verdict.

        :return:    True if the action succeeded, otherwise False.
        """
        return self.success
