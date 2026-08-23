"""
@file agent/protocol/parser.py
"""

import json
from typing import List, Dict, Any

from AI_Challenge_UACS.agent.actions.register import ActionRegister
from AI_Challenge_UACS.agent.protocol.format import *
from AI_Challenge_UACS.agent.actions.verdict import ExitCode, ActionVerdict


class BotResponseParser:
    """
    parsing bot response by `protocol.py` rules
    """

    @staticmethod
    def to_json(raw_input: str) -> Dict[str, Any]:
        return json.loads(raw_input)


    @staticmethod
    def parse_required_fields(response: Dict[str, Any]) -> Dict[str, Any]:
        res = {}

        for field in BotRequiredFields:
            res[field.value] = response[field.value]

        return res


    @staticmethod
    def parse_actions(actions: List[Dict[str, Any]]) -> tuple[ActionVerdict, List[Action]]:
        agent_todo = []

        for action in actions:
            name = action[ActionFields.ACTION.value]
            arguments = action[ActionFields.ARGUMENTS.value]
            action_type = ActionRegister.get_action(name)

            if action_type is None:
                return ActionVerdict(
                    ExitCode.PROTOCOL_ERROR,
                    f"unknown action {name}"
                ), []

            action = action_type.from_arguments(arguments)
            agent_todo.append(action)

        return ActionVerdict(
            ExitCode.SUCCESS,
            "actions are parsed",
        ), agent_todo
