import json
import time
from typing import List
from actions.dispatcher import ActionDispatcher
from actions.verdict import ActionVerdict

from utils.json import recursive_serializer
from utils.logger import get_logger
from actions.tools.adapter import ToolCallAdapter
from llm_client import LLMClient
from openai.types.chat.chat_completion_message import ChatCompletionMessage

logger = get_logger(__name__)

class WarerAgent:

    # def __new__(cls):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(WarerAgent, cls).__new__(cls)
    #     return cls.instance

    def __init__(self, system_prompt: str = "", rate_limit: int = 0):
        self.llm = LLMClient(system_prompt)
        self.dispatcher = ActionDispatcher()
        self.rate_limit = min(max(0, rate_limit), 100)

    def _clear_response(self, response: str) -> str:
        try:
            response = response[response.index("{"):response.rindex("}") + 1]
        except ValueError as e:
            logger.exception("response is not JSON type")

        return response

    def _get_raw_input(self, message: ChatCompletionMessage) -> str:
        if message.tool_calls:
            raw_input = ToolCallAdapter.to_dispatcher_input(message)
        else:
            # raw_input = message.content
            raw_input = None

        if raw_input is None:
            raw_input = str({
                "actions": [
                    {
                        "action": "ignore"
                    }
                ]
            })

        return raw_input

    def run(self, prompt: str):
        message = self.llm.ask(prompt)

        raw_input = self._get_raw_input(message)

        verdicts = self.dispatcher.dispatch(raw_input)
        
        def helper(verdicts: List[ActionVerdict], count: int = 1):
            if verdicts is None or count >= 255:
                # stop
                return
            else:
                if not self.rate_limit is None:
                    time.sleep(self.rate_limit)

                serialized_verdicts = str(list(map(lambda x: x.to_json(), verdicts)))
                message = self.llm.ask(serialized_verdicts)
                
                raw_input = self._get_raw_input(message)
        
                verdicts = self.dispatcher.dispatch(raw_input)
                helper(verdicts, count + 1)
            # TODO: Rollback Logger ?

        helper(verdicts)
