from utils.environment import Environment, EnvKeys
from actions.dispatcher import ActionDispatcher

class WarerAgent:

    # def __new__(cls):
    #     if not hasattr(cls, "instance"):
    #         cls.instance = super(WarerAgent, cls).__new__(cls)
    #     return cls.instance

    def __init__(self):
        model_name = Environment.get(EnvKeys.LOCAL_AGENT_MODEL)
        base_url = Environment.get(EnvKeys.OPENAI_BASE_URL)
        api_key = Environment.get(EnvKeys.OPENAI_API_KEY)
        self.system_prompt = (
            "You are a non-interactive coding agent. "
            "Complete the user's request autonomously. "
            "Use tools to inspect files, run commands, and apply focused diffs. "
            "Work in concise steps and explain what you changed in the final response."
        )

    def request(self, prompt: str):
