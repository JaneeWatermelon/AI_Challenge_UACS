"""
@file agent/protocol/format.py
"""

from enum import Enum
from typing import List, Dict, Any

from actions.base import Action
from actions.details import execution_aborted
from actions.verdict import ActionVerdict, ExitCode
from actions.workspace.ignore import ActionIgnore


class BotRequiredFields(Enum):
    ACTIONS = "actions"  # array


class ActionFields(Enum):
    ACTION = "action"  # string
    ARGUMENTS = "arguments"  # arguments


class OptionalFields(Enum):
    ID = "id"  # string


class AgentRequiredFields(Enum):
    RESULTS = "results"  # array
    STOPPED_EARLY = "stopped_early"  # bool
    EXECUTED = "executed"  # int
    TOTAL = "total"  # int


class ResultItem(Enum):
    ACTION = "action"  # string | null
    EXIT_CODE = "exit_code"  # string
    MESSAGE = "message"  # string


class AgentOptionalFields(Enum):
    DATA = "data"  # obj
    ID = "id"  # string
    REASON = "reason"  # string (if stopped early)
    ERROR = "error"  # string


def has_ignore_action(actions: List[Action]) -> bool:
    return any(isinstance(action, ActionIgnore) for action in actions)


def abort_reply(at: int,
                reason: str,
                data: Dict[str, Any]
                ) -> List[ActionVerdict]:
    return [
        ActionVerdict(
            ExitCode.EXECUTION_ERROR,
            execution_aborted(at, reason),
            data
        )
    ]


class Format:
    """
    Protocol format definitions and utilities.
    """

    @staticmethod
    def build_fields_description() -> str:
        """
        Build a recursive field description for all protocol enums.
        Shows each enum class name and its fields with values and descriptions.

        :return:    Formatted field description string.
        """
        enums = [
            BotRequiredFields,
            ActionFields,
            OptionalFields,
            AgentRequiredFields,
            ResultItem,
            AgentOptionalFields,
        ]

        output = "./protocol/\n"

        for enum_cls in enums:
            output += Format._format_enum(enum_cls)
            output += "\n"

        return output

    @staticmethod
    def _format_enum(enum_cls: type[Enum]) -> str:
        """
        Format a single enum class.

        :param enum_cls:    The enum class to format.
        :return:            Formatted enum string.
        """
        # Directory style header: ./
        lines = [f"./{enum_cls.__name__}/"]

        # List each member like a file
        for member in enum_cls:
            lines.append(f"    {member.name} => {member.value}")

        return "\n".join(lines)

    @staticmethod
    def build_response_format() -> str:
        """
        Build a description of the expected response format for the bot.
        """
        return (
            "RESPONSE FORMAT\n\n"
            "Request:\n"
            "{\n"
            '  "actions": [\n'
            "    {\n"
            '      "action": "name",\n'
            '      "arguments": { ... }\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Response:\n"
            "{\n"
            f'  "{AgentRequiredFields.RESULTS.value}": [\n'
            "    {\n"
            f'      "{ResultItem.ACTION.value}": "name",\n'
            f'      "{ResultItem.EXIT_CODE.value}": "success|error",\n'
            f'      "{ResultItem.MESSAGE.value}": "..."\n'
            "    }\n"
            "  ],\n"
            f'  "{AgentRequiredFields.STOPPED_EARLY.value}": false,\n'
            f'  "{AgentRequiredFields.EXECUTED.value}": N,\n'
            f'  "{AgentRequiredFields.TOTAL.value}": N\n'
            "}\n\n"
            "If no action: { \"actions\": [ { \"action\": \"ignore\" } ] }\n"
            "On error: stopped_early=true, reason/error fields added."
        )
