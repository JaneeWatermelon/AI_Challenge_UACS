from actions.register import ActionRegister

from utils.logger import get_logger

logger = get_logger(__name__)

def build_tools():
    tools = []

    logger.info(ActionRegister.get_all_actions())

    for name, action_cls in ActionRegister.get_all_actions():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": action_cls({}).description,
                "parameters": action_cls.parameters_schema(),
            },
        })

    return tools