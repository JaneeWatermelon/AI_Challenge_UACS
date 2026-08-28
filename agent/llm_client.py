import os

from openai import OpenAI

from utils.logger import get_logger
from utils.environment import EnvKeys, Environment
from utils.system_prompt import SystemPromptGenerator

logger = get_logger(__name__)

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
        ) + SystemPromptGenerator.build()

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

        try:
            logger.info("LLMClient starting query to LLM")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=10000
            )

            result = response.choices[0].message.content
            logger.info(f"LLMClient got response from LLM: {result}")

            return result or ""
        except Exception as e:
            logger.exception(f"LLMClient exception: {result}")
            print(f"OpenAI error: {e}")