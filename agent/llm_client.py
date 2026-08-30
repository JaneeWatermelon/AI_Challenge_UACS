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
            "Work in concise steps. "
            "Return the response only in JSON format WITHOUT any highlighter like ```json etc. Only raw JSON. "
            "You have to start from '{' and end by '}'"
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
            logger.info(f"LLMClient starting query to LLM: {messages}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=10000,
            )

            content = response.choices[0].message.content
            reasoning = response.choices[0].message.reasoning

            logger.info(f"LLMClient got response from LLM: {response}")
            logger.info(f"LLMClient got response.choices[0] from LLM: {response.choices[0]}")
            logger.info(f"LLMClient got response.choices[0].message from LLM: {response.choices[0].message}")
            logger.info(f"LLMClient got response.choices[0].message.content from LLM: {response.choices[0].message.content}")
            logger.info(f"LLMClient got response.choices[0].message.reasoning from LLM: {response.choices[0].message.reasoning}")

            result = content

            if content is None:
                if reasoning is None:
                    raise ValueError("LLMClient response is None")
                result = reasoning
            
            return result
        except Exception as e:
            logger.exception(f"LLMClient exception: {e}")
            print(f"OpenAI error: {e}")