"""
Contains defenition of logger to store last executed actions
"""

from .base import Action
from typing import List, Optional

class ActionLogger:
    """
    Singleton logger for storing actions

    Params:
        _instance (ActionLogger | None): the only one instance of ActionLogger.
        actions (List[:obj:`Action`]): Stack which stores actions. 
    """

    _instance = None
    actions: List[Action] = []

    def __new__(cls, *args, **kwargs):
        """
        Singleton pattern
        """
        if cls._instance is None:
            cls._instance = super(ActionLogger, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    

    def __init__(self):
        """
        Creates an instance of ActionLogger
        """
        pass

    def push(self, action: Action) -> None:
        """
        Push an action to logger's stack.

        Args:
            action (:obj:`Action`): Action which is going to be pushed.
        """
        self.actions.append(action)

    @property
    def actions(self):
        """
        TODO: Property
        """
        pass

    def push_n(self, actions: List[Action]):
        """
        TODO: loop of Pushes into stack
        """
        pass

    def pop(self) -> Optional[Action]:
        """
        Pops an action from logger's stack.

        Returns:
            Action or None: if exists - popped action, else - None.
        """
        if len(self.actions) > 0:
            return self.actions.pop()
        else:
            return None
        
    def pop_n(self, n: int) -> List[Action]:
        """
        Pops the specified amount of actions from logger's stack.

        Returns:
            List[Action]: List of actions.
        """
        first_index = max(len(self.actions)-n, 0)
        result = self.actions[first_index:]
        self.actions = self.actions[:first_index]

        return result

    def len(self):
        """
        TODO: amount of actions in stack
        """
        pass
    
    def clear(self):
        """
        TODO: clear stack
        """
        pass

    def __str__(self):
        """
        TODO
        """
        pass
    
    def __repr__(self):
        """
        TODO
        """
        pass