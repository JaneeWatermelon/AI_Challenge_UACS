"""
@file agent/actions/dispatcher.py
"""

from typing import List, Optional

from base import Action
from verdict import ActionVerdict, ExitCode
from AI_Challenge_UACS.agent.protocol.parser import BotResponseParser
from AI_Challenge_UACS.agent.protocol.format import BotRequiredFields, has_ignore_action
from AI_Challenge_UACS.agent.actions.context import Context
from AI_Challenge_UACS.agent.protocol.format import abort_reply


class ActionDispatcher:
    """

    """

    def __init__(self):
        self.context = Context()


    def dispatch(self, raw_input: str) -> Optional[List[ActionVerdict]]:
        self.context.clear()
        parse_verdict, actions = self._parse(raw_input)

        if parse_verdict.code != ExitCode.SUCCESS:
            return [parse_verdict]

        if has_ignore_action(actions):
            return None

        for action in actions:
            verdict = action.execute()

            if verdict.code != ExitCode.SUCCESS:
                rollback_report = self._rollback(actions[:self.context.done+1])
                return abort_reply(
                    self.context.done,
                    verdict.details,
                    {"rollback": rollback_report}
                )

            self.context.mark_execution_result(verdict)

        return self.context.verdicts


    def _parse(self, raw_input: str) -> tuple[ActionVerdict, List[Action]]:
        json_response = BotResponseParser.to_json(raw_input)
        parsed = BotResponseParser.parse_required_fields(json_response)

        actions_field = parsed.get(BotRequiredFields.value)
        if actions_field is None:
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field '{BotRequiredFields.ACTIONS.value}' missed"
            ), []

        if not isinstance(actions_field, list):
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field '{BotRequiredFields.ACTIONS.value}' has to be an array"
            ), []

        return BotResponseParser.parse_actions(actions_field)


    def _rollback(self, actions: List[Action]) -> List[ActionVerdict]:
        return [
            action.reverse() for action in actions
            if not action.readonly
        ]
