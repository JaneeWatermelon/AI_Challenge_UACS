"""
@file agent/actions/dispatcher.py
"""

from typing import List, Optional, Dict, Any

from .base import Action
from verdict import ActionVerdict, ExitCode


class ActionDispatcher:

    def __init__(self):
        pass


    def dispatch(self, raw_input: str) -> Optional[ActionVerdict]:
        parsed = self._parse(raw_input)
        action = self._select_action(parsed)

        if action is None:
            return ActionVerdict(
                ExitCode.NO_ACTION_SELECTED,
                "failed to select an action"
            )

        try:
            return action.execute()

        except Exception as e:
            return ActionVerdict(
                ExitCode.EXECUTION_ERROR,
                f"Action execution failed: {str(e)}"
            )


    def _parse(self, raw_input: str) -> Dict[str, Any]:
        # TODO: raw input parser util
        pass


    def _select_action(self, parsed: Dict[str, Any]) -> Optional[Action]:
        # TODO: actions selection workflow
        return None
