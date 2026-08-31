### `tools/adapter.py`

import json
from typing import Any
from openai.types.chat.chat_completion_message import ChatCompletionMessage


class ToolCallAdapter:
    """
    Converts an LLM tool call into the JSON protocol
    expected by ActionDispatcher.
    """

    @staticmethod
    def to_dispatcher_input(message: ChatCompletionMessage) -> str:
        """
        Convert message.tool_calls to dispatcher-compatible JSON.

        Example result:

        {
            "actions": [
                {
                    "action": "create",
                    "arguments": {
                        "path": "/app/bye.txt",
                        "content": ["Bye"]
                    }
                }
            ]
        }
        """

        actions = []

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            actions.append({
                "action": name,
                "arguments": arguments,
            })

        payload = {
            "actions": actions,
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
        )