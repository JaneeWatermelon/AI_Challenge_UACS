"""
@file agent/utils/system_propmpt.py
"""

from typing import List, Tuple

from actions.base import Action
from actions.register import ActionRegister
from protocol.format import Format


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
    def build(tools_used: bool=True) -> str:
        """
        Build a complete system prompt from all registered actions.

        :return:    Formatted system prompt string.
        """
        if tools_used:
            return SystemPromptGenerator._build_tools_prompt()

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

    @staticmethod
    def _build_tools_prompt() -> str:
        """
        Build the protocol instructions for the agent using tools variable.

        This describes how the agent should interpret incoming messages
        and what to do in different scenarios.

        :return: Protocol instruction string.
        """
        return (
            "You will receive messages in two formats. If you receive plain text, "
            "treat it as an instruction and respond with a JSON object containing "
            "the actions you want to execute. If you receive a JSON object with "
            "a 'results' field, it contains the results of your previous actions. "
            "If the results shows success, continue with the next actions or send "
            "an ignore action to finish. If the results shows an error, either "
            "retry with corrected arguments or send ignore. If you receive an "
            "unknown format or are unsure what to do, always respond with ignore. "
            "Never include any text outside the JSON response."
        )
