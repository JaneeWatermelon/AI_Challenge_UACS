"""
@file agent/actions/dispatcher.py
"""

from typing import List, Optional

from actions.base import Action
from actions.context import Context
from actions.verdict import ActionVerdict, ExitCode
from protocol.format import BotRequiredFields, has_ignore_action
from protocol.format import abort_reply
from protocol.parser import BotResponseParser


class ActionDispatcher:
    """
    Принимает сообщения от модели,
    парсит действия и мониторит их выполнение
    в случае неудачи выполняет откат
    """

    def __init__(self):
        """
        инициализация контекста
        """
        self.context = Context()


    def dispatch(self, raw_input: str) -> Optional[List[ActionVerdict]]:
        """
        выполнение команд полученных от модели
        :param raw_input:   текстовый ответ от модели
        :return:            Нон если ответ не требуется, список результатов по каждому действию
        """
        self.context.clear()
        parse_verdict, actions = self._parse(raw_input)

        # parsing step verification
        if parse_verdict.code != ExitCode.SUCCESS:
            return [parse_verdict]  # parsing issue

        # explicit ignore command check
        if has_ignore_action(actions):
            return None # ignore flag

        # execution
        for action in actions:
            verdict = action.execute()

            # rollback check
            if verdict.code != ExitCode.SUCCESS:
                rollback_report = self._rollback(actions[:self.context.done+1])
                return abort_reply(
                    self.context.done,
                    verdict.details,
                    {
                        "rollback": rollback_report,
                        "runtime": self.context.verdicts
                    }
                )

            self.context.mark_execution_result(verdict)

        # agent reply verdicts
        return self.context.verdicts


    def _parse(self, raw_input: str) -> tuple[ActionVerdict, List[Action]]:
        """
        получает команды от модели из текста
        :param raw_input:   текстовый ответ от модели
        :return:            вердикт по парсингу и список действий на выполнение
        """
        json_response = BotResponseParser.to_json(raw_input)
        parsed = BotResponseParser.parse_required_fields(json_response)

        # 'actions' required field check
        actions_field = parsed.get(BotRequiredFields.ACTIONS.value)
        if actions_field is None:
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field '{BotRequiredFields.ACTIONS.value}' missed"
            ), []

        # field instance check (see format.py)
        if not isinstance(actions_field, list):
            return ActionVerdict(
                ExitCode.PROTOCOL_ERROR,
                f"required field '{BotRequiredFields.ACTIONS.value}' has to be an array"
            ), []

        return BotResponseParser.parse_actions(actions_field)


    def _rollback(self, actions: List[Action]) -> List[ActionVerdict]:
        """
        откатывает все не ридонли действия
        :param actions: очередь на выполнение, где произошли траблы
        :return:        отчет по откату каждого действия
        """
        return [
            action.reverse() for action in actions
            if not action.readonly
        ]
