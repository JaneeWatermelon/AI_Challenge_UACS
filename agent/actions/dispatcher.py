"""
@file agent/actions/dispatcher.py
"""
import json
from typing import List, Optional

from actions.base import Action
from actions.context import Context
from actions.verdict import ActionVerdict, ExitCode
from protocol.format import BotRequiredFields, has_ignore_action
from protocol.format import abort_reply
from protocol.parser import BotResponseParser


class ActionDispatcher:
    """
    Receives messages from the model, parses actions,
    and monitors their execution.

    In case of failure, it performs a rollback of all non-readonly actions.
    """

    def __init__(self):
        """
        Initialize the dispatcher with an empty execution context.
        """
        self.context = Context()

    def dispatch(self, raw_input: str) -> Optional[List[ActionVerdict]]:
        """
        Execute commands received from the model.

        :param raw_input:   Textual response from the model.
        :return:            None if no response is required,
                            otherwise a list of verdicts for each action.
        """
        self.context.clear()
        parse_verdict, actions = self._parse(raw_input)

        # Parsing step verification
        if parse_verdict.code != ExitCode.SUCCESS:
            return [parse_verdict]  # Parsing issue

        # Explicit ignore command check
        if has_ignore_action(actions):
            return None  # Ignore flag

        # Execution
        for action in actions:
            verdict = action.execute()

            # Rollback check
            if verdict.code != ExitCode.SUCCESS:
                rollback_report = self._rollback(actions[:self.context.done + 1])
                return abort_reply(
                    self.context.done,
                    verdict.details,
                    {
                        "rollback": rollback_report,
                        "runtime": self.context.verdicts
                    }
                )

            self.context.mark_execution_result(verdict)

        # Agent reply verdicts
        return self.context.verdicts

    def _parse(self, raw_input: str) -> tuple[ActionVerdict, List[Action]]:
        """
        Parse actions from the model's response text.

        :param raw_input:   Textual response from the model.
        :return:            A tuple containing:
                            - parsing verdict
                            - list of actions to execute
        """
        try:
            json_response = BotResponseParser.to_json(raw_input)
            parsed = BotResponseParser.parse_required_fields(json_response)

        except KeyError as e:
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field missed: {str(e)}"
            ), []

        except json.JSONDecodeError as e:
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"given non-json input: {str(e)}"
            ), []

        actions_field = parsed.get(BotRequiredFields.ACTIONS.value)

        # Field instance check (see format.py)
        if not isinstance(actions_field, list):
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field '{BotRequiredFields.ACTIONS.value}' has to be an array"
            ), []

        return BotResponseParser.parse_actions(actions_field)

    def _rollback(self, actions: List[Action]) -> List[ActionVerdict]:
        """
        Roll back all non-readonly actions in reverse order.

        :param actions: The queue of actions that were executed
                        (or attempted) before the failure.
        :return:        A report containing the verdict of each rollback operation.
        """
        return [
            action.reverse() for action in actions
            if not action.readonly
        ]
