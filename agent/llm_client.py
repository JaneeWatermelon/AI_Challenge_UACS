import os

from openai import OpenAI
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from utils.logger import get_logger
from utils.environment import EnvKeys, Environment
from utils.system_prompt import SystemPromptGenerator
from actions.tools.tools import build_tools

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
            "Use the available tools to inspect and modify the workspace. "
            "Choose tools based on their descriptions and parameter schemas. "
            "Do not claim that an action was performed unless the corresponding tool succeeded. "
        )

    def ask(self, prompt: str) -> ChatCompletionMessage:
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
            logger.info(f"build_tools():\n{build_tools()}")
            logger.info(f"LLMClient starting query to LLM: {messages}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=10000,
                tools=build_tools(),
                tool_choice='auto'
            )

            message = response.choices[0].message

            logger.info(f"LLMClient got response from LLM: {response}")
            logger.info(f"LLMClient got response.choices[0] from LLM: {response.choices[0]}")
            logger.info(f"LLMClient got response.choices[0].message from LLM: {message}")
            
            return message
        except Exception as e:
            logger.exception(f"LLMClient exception: {e}")