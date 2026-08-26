import os
from enum import Enum

class EnvKeys(Enum):
    """
    Available list of environment keys
    """
    LOCAL_AGENT_MODEL = "LOCAL_AGENT_MODEL"
    OPENAI_BASE_URL = "OPENAI_BASE_URL"
    OPENAI_API_KEY = "OPENAI_API_KEY"
    LOCAL_AGENT_WORKDIR = "LOCAL_AGENT_WORKDIR"

class Environment:
    """
    Describes meta class to provide safe access to evironment variables.
    It is recommended to refer to the class, not to the instance.
    """
    def __new__(cls):
        """
        Singleton pattern
        """
        if not hasattr(cls, 'instance'):
            cls.instance = super(Environment, cls).__new__(cls)
        return cls.instance

    @classmethod
    def get(cls, key: EnvKeys) -> str:
        """
        Provides access to read env variable

        Args:
            key (:obj:`EnvKeys`): The key that will be used to get the variable
        Returns:
            str: Read key
        Raises:
            ValueError: If `key` type differs from :obj:`EnvKeys`.
        """
        if key in EnvKeys:
            return os.environ.get(EnvKeys(key))
        else:
            raise ValueError(f"`key` argument have to be `EnvKeys` type, got {type(key).__name__}")
