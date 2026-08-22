"""
@file agent/actions/dispatcher.py
"""

from typing import List, Optional, Dict, Any

from base import Action
from verdict import ActionVerdict, ExitCode
from AI_Challenge_UACS.agent.protocol.parser import BotResponseParser
from AI_Challenge_UACS.agent.protocol.format import BotRequiredFields


class ActionDispatcher:


    def dispatch(self, raw_input: str) -> Optional[List[ActionVerdict]]:
        parse_verdict, actions = self._parse(raw_input)

        if parse_verdict.code != ExitCode.SUCCESS:
            return [parse_verdict]

        try:
            for action in actions:
                action.execute()

        except Exception as e:
            return [
                ActionVerdict(
                    ExitCode.EXECUTION_ERROR,
                  f"execution aborted at {1}th\n"
                  f"Execution interrupted.\n"
                  f"All operations have been cancelled.\n"
                  f"No changes were applied."
                )
            ]


    def _parse(self, raw_input: str) -> tuple[ActionVerdict, List[Action]]:
        json_response = BotResponseParser.to_json(raw_input)
        parsed = BotResponseParser.parse_required_fields(json_response)

        actions_field = parsed.get(BotRequiredFields.value)
        if actions_field is None:
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field {BotRequiredFields.ACTIONS.value} missed"
            ), []

        return BotResponseParser.parse_actions(actions_field)

