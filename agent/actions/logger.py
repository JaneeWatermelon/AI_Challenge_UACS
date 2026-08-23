"""
Contains defenition of logger to store last executed actions
"""

from .base import Action
from typing import List, Optional, Any

class ActionLogger:
    """
    Singleton logger for storing actions

    Params:
        _instance (ActionLogger | None): the only one instance of ActionLogger.
        actions (List[:obj:`Action`]): Stack which stores actions. 
    """

    _instance = None
    _actions: List[Action] = []

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

    def _check_actions(self, actions: List[Any]) -> bool:
        """
        Checks if 

        Args:
            value (List[:obj:`Action`]): List of actions which is going to replace old stack.
        Returns:
            bool: True if all actions' type is Action
        Raises:
            TypeError: If any `action` type in the list is not :obj:`Action`.
        """
        i = 0
        while i < len(actions):
            if not isinstance(actions[i], Action):
                raise TypeError(f"actions[{i}] must be an Action instance, got {type(actions[i]).__name__}")
            i += 1

        return True

    @property
    def actions(self) -> List[Action]:
        """
        GET property for _actions
        """
        return self._actions
    
    @actions.setter
    def actions(self, value: List[Action]) -> None:
        """
        SET property for _actions

        Args:
            value (List[:obj:`Action`]): List of actions which is going to replace old stack.
        """
        self._check_actions(value)
        self._actions = value

    def push(self, action: Action) -> None:
        """
        Push an action to logger's stack.

        Args:
            action (:obj:`Action`): Action which is going to be pushed.
        Raises:
            TypeError: If `action` type is not :obj:`Action`.
        """
        if not isinstance(action, Action):
            raise TypeError(f"`action` must be an Action instance, got {type(action).__name__}")
        
        self._actions.append(action)

    def push_n(self, actions: List[Action]) -> None:
        """
        Push actions to logger's stack.

        Args:
            actions (List[:obj:`Action`]): List of actions which is going to be pushed.
        Raises:
            TypeError: If `action` type is not :obj:`Action`.
        """
        self._check_actions(actions)
        for action in actions:
            self.push(action)

    def pop(self) -> Optional[Action]:
        """
        Pops an action from logger's stack.

        Returns:
            Action or None: if exists - popped action, else - None.
        """
        if len(self.actions) > 0:
            return self._actions.pop()
        else:
            return None
        
    def pop_n(self, n: int) -> List[Action]:
        """
        Pops the specified amount of actions from logger's stack.

        Returns:
            List[Action]: List of actions.
        """
        first_index = max(len(self.actions)-n, 0)
        result = self._actions[first_index:]
        self._actions = self._actions[:first_index]

        return result
    
    def clear(self) -> None:
        """
        Clear the stack
        """
        self._actions.clear()

    def __len__(self):
        return len(self._actions)

    def __str__(self):
        return f"ActionLogger(actions={self._actions})"
    
    def __repr__(self):
        return {
            "count": len(self),
            "actions": self._actions
        }