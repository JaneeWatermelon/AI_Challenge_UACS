import os

from openai import OpenAI

from utils.environment import EnvKeys, Environment


class LLMClient:

    def __init__(self, system_prompt: str = "") -> None:
        self.client = OpenAI(
            api_key=Environment.get(EnvKeys.OPENAI_API_KEY),
            base_url=Environment.get(EnvKeys.OPENAI_BASE_URL),
        )
        self.model = Environment.get(EnvKeys.LOCAL_AGENT_MODEL)
        self.system_prompt = system_prompt or (
            "You are a non-interactive coding agent. "
            "Complete the user's request autonomously. "
            "Use tools to inspect files, run commands, and apply focused diffs. "
            "Work in concise steps and explain what you changed in the final response."
        )

    def ask(self, prompt: str) -> str:
        messages = []

        if self.system_prompt:
            messages.append(
                {
                    "role": "system", 
                    "content": self.system_prompt
                }
            )
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return response.choices[0].message.content or ""