"""
@file agent/actions/workspace/ignore.py
"""

from typing import Dict, Any, override

from actions.base import Action
from actions.verdict import ActionVerdict, ExitCode
from actions.register import ActionRegister
from utils.assertion import safe_verdict


@ActionRegister.register("ignore")
class ActionIgnore(Action):
    """
    Action that signals the end of a session.

    This action is used to explicitly ignore a model's reply,
    indicating that no further actions should be processed.
    """

    def __init__(self, arguments: Dict[str, Any]):
        """
        Initialize the ignore action.

        :param arguments:   Dictionary of arguments (unused for this action).
        """
        super().__init__(
            ActionIgnore._registered_name,
            "ignoring a reply",
            arguments,
            True
        )

    @override
    def to_json(self) -> Dict[str, Any]:
        """
        Serialize the action to a JSON-compatible dictionary.

        :return:    Dictionary representation of the action.
        """
        return {
            "name": self.name,
            "description": self.description,
        }

    @override
    def execute(self) -> ActionVerdict:
        """
        Execute the ignore action.

        Simply returns a success verdict indicating the reply was ignored.

        :return:    Success verdict with "ignored" details.
        """
        return ActionVerdict(
            ExitCode.SUCCESS,
            "ignored"
        )

    @override
    @safe_verdict
    def reverse(self) -> "ActionIgnore":
        """
        Return the reverse action.

        Since this is a read-only action, it reverses to itself.

        :return:    The same action instance.
        """
        return self
