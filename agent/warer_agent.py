import json
import time
from typing import List
from actions.dispatcher import ActionDispatcher
from actions.verdict import ActionVerdict

from utils.json import recursive_serializer
from utils.logger import get_logger
from llm_client import LLMClient

logger = get_logger(__name__)

class WarerAgent:

    # def __new__(cls):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(WarerAgent, cls).__new__(cls)
    #     return cls.instance

    def __init__(self, system_prompt: str = "", rate_limit: int = None):
        self.llm = LLMClient(system_prompt)
        self.dispatcher = ActionDispatcher()
        self.rate_limit = min(max(0, rate_limit), 100)

    def _clear_response(self, response: str) -> str:
        try:
            response = response[response.index("{"):response.rindex("}") + 1]
        except ValueError as e:
            logger.exception("response is not JSON type")

        return response

    def run(self, prompt: str):
        raw_response = self.llm.ask(prompt)
        response = self._clear_response(raw_response)
        verdicts = self.dispatcher.dispatch(response)
        
        def helper(verdicts: List[ActionVerdict], count: int = 1):
            if verdicts is None or count >= 255:
                # stop
                return
            else:
                if not self.rate_limit is None:
                    time.sleep(self.rate_limit)

                # serialized_verdicts = list(map(lambda x: x.to_json(), verdicts))
                serialized_verdicts = json.dumps(verdicts, default=recursive_serializer)
                raw_response = self.llm.ask(serialized_verdicts)
                response = self._clear_response(raw_response)
                verdicts = self.dispatcher.dispatch(response)
                helper(verdicts, count + 1)
            # TODO: Rollback Logger ?

        helper(verdicts)
