"""
@file agent/format.py
"""

from enum import Enum


class BotRequiredFields(Enum):
    ACTIONS = "actions"             # array

    class ActionFields(Enum):
        ACTION = "action"           # string
        ARGUMENTS = "arguments"     # arguments

        class OptionalFields(Enum):
            ID = "id"               # string

    def __str__(self):
        return self.value


class AgentRequiredFields(Enum):
    RESULTS = "results"             # array
    STOPPED_EARLY = "stopped_early" # bool
    EXECUTED = "executed"           # int
    TOTAL = "total"                 # int

    class ResultItem(Enum):
        ACTION = "action"           # string | null
        EXIT_CODE = "exit_code"     # string
        MESSAGE = "message"         # string

        class OptionalFields(Enum):
            DATA = "data"           # obj
            ID = "id"               # string
            REASON = "reason"       # string (if stopped early)
            ERROR = "error"         # string
