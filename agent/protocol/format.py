"""
@file agent/protocol/format.py
"""

from enum import Enum
from typing import List, Dict, Any

from agent.actions.verdict import ActionVerdict, ExitCode
from agent.actions.workspace.ignore import ActionIgnore
from agent.actions.base import Action
from agent.actions.details import execution_aborted


class BotRequiredFields(Enum):
    ACTIONS = "actions"             # array


class ActionFields(Enum):
    ACTION = "action"               # string
    ARGUMENTS = "arguments"         # arguments


class OptionalFields(Enum):
    ID = "id"                       # string


class AgentRequiredFields(Enum):
    RESULTS = "results"             # array
    STOPPED_EARLY = "stopped_early" # bool
    EXECUTED = "executed"           # int
    TOTAL = "total"                 # int


class ResultItem(Enum):
    ACTION = "action"               # string | null
    EXIT_CODE = "exit_code"         # string
    MESSAGE = "message"             # string


class AgentOptionalFields(Enum):
    DATA = "data"                   # obj
    ID = "id"                       # string
    REASON = "reason"               # string (if stopped early)
    ERROR = "error"                 # string


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
