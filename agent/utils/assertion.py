"""
@file agent/utils/assertion.py
"""

from actions.verdict import ActionVerdict, ExitCode


def safe_verdict(func):
    def wrapper(self, *args, **kwargs) -> ActionVerdict:
        try:
            return func(self, *args, **kwargs)

        except PermissionError as e:
            return ActionVerdict(ExitCode.PERMISSION_DENIED, str(e))

        except FileNotFoundError as e:
            return ActionVerdict(ExitCode.NOT_FOUND, str(e))

        except ValueError as e:
            return ActionVerdict(ExitCode.INVALID_ARGUMENT, str(e))

        except Exception as e:
            return ActionVerdict(ExitCode.EXECUTION_ERROR, str(e))

    return wrapper
