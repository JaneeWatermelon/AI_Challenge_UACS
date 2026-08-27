from typing import List
from actions.dispatcher import ActionDispatcher
from actions.verdict import ActionVerdict

from llm_client import LLMClient

class WarerAgent:

    # def __new__(cls):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(WarerAgent, cls).__new__(cls)
    #     return cls.instance

    def __init__(self, system_prompt: str = ""):
        self.llm = LLMClient(system_prompt)
        self.dispatcher = ActionDispatcher()

    def run(self, prompt: str):
        raw_response = self.llm.ask(prompt)
        verdicts = self.dispatcher.dispatch(raw_response)
        
        def helper(verdicts: List[ActionVerdict], count: int = 1):
            if verdicts is None or count >= 255:
                # stop
                return
            else:
                raw_response = self.llm.ask(prompt)
                verdicts = self.dispatcher.dispatch(raw_response)
                helper(verdicts, count + 1)
            # TODO: Rollback Logger ?

        helper(verdicts)
