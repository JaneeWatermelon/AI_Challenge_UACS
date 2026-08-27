"""
@file agent/utils/system_propmpt.py
"""

from typing import List, Tuple

from agent.actions.base import Action
from agent.actions.register import ActionRegister
from agent.protocol.format import Format


class SystemPromptGenerator:
    """
    Generates a system prompt for the AI agent.

    The prompt includes:
        - List of all registered actions with their descriptions
        - Protocol field definitions
        - Expected response format

    This prompt is used to inform the agent about available commands
    and how to communicate with the system.
    """

    @staticmethod
    def build() -> str:
        """
        Build a complete system prompt from all registered actions.

        :return:    Formatted system prompt string.
        """
        actions = ActionRegister.get_all_actions()

        if not actions:
            raise RuntimeError("No actions already registered")

        return SystemPromptGenerator._build_prompt(actions)

    @staticmethod
    def _build_prompt(actions: List[Tuple[str, type[Action]]]) -> str:
        """
        Build a prompt with available actions.

        :param actions: List of (name, class) tuples.
        :return:        Formatted prompt string.
        """
        prompt = "AVAILABLE ACTIONS\n\n"

        for name, action_cls in actions:
            instance = action_cls({})
            readonly_marker = "[READ-ONLY]" if instance.readonly else "[READ-WRITE]"
            prompt += f"{name} {readonly_marker}:\n{instance.description}\n\n"

        prompt += Format.build_fields_description()
        prompt += Format.build_response_format()

        return prompt
