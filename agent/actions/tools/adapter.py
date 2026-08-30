### `tools/adapter.py`

import json
from typing import Any


class ToolCallAdapter:
    """
    Converts an LLM tool call into the JSON protocol
    expected by ActionDispatcher.
    """

    @staticmethod
    def to_dispatcher_input(
        name: str,
        arguments: dict[str, Any],
    ) -> str:
        """
        Convert a single tool call to dispatcher-compatible JSON.

        Example:
            name = "exists"
            arguments = {"path": "/app"}

        Returns:
            '{"actions": [{"name": "exists", "arguments": {"path": "/app"}}]}'
        """

        payload = {
            "actions": [
                {
                    "name": name,
                    "arguments": arguments,
                }
            ]
        }

        return json.dumps(
            payload,
            ensure_ascii=False,
        )