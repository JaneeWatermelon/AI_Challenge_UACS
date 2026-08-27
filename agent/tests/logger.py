from actions.logger import ActionLogger
from actions.workspace.modify import ActionModify
from actions.workspace.read import ActionRead
from actions.workspace.tree import ActionTree
from utils.paths import FsService

if __name__ == "__main__":
    action1 = ActionRead(
        {
            "arg1": 1,
            "arg2": 2,
            "arg3": 3,
        },
        FsService()
    )
    action2 = ActionModify(
        {
            "arg1": 1,
            "arg2": 2,
            "arg3": 3,
        },
        FsService()
    )
    action3 = ActionTree(
        {
            "arg1": 1,
            "arg2": 2,
            "arg3": 3,
        },
        FsService()
    )

    # Пример 1: Базовое использование
    print("Пример 1: Базовое использование")

    logger1 = ActionLogger()

    logger1.push(action1)
    logger1.push(action2)
    logger1.push(action3)

    print(f"Текущие действия: {logger1.actions}")

    popped = logger1.pop()
    print(f"Извлечено: {popped}")
    print(f"Осталось: {logger1.actions}")

    # Пример 2: Демонстрация Singleton
    print()
    print("Пример 2: Демонстрация Singleton")

    logger2 = ActionLogger()
    logger2.push(action1)

    print(f"logger1.actions: {logger1.actions}")
    print(f"logger2.actions: {logger2.actions}")
    print(f"Один ли это объект? {logger1 is logger2}")  # True

    # Пример 3: Извлечение и добавление нескольких действий
    print()
    print("Пример 3: Извлечение и добавление нескольких действий")

    logger3 = ActionLogger()
    # Очищаем предыдущие действия
    logger3.actions = []

    logger3.push_n([
        action1,
        action2,
        action3,
    ])

    print(f"До pop_n: {logger3.actions}")

    popped_n = logger3.pop_n(3)
    print(f"Извлечено 3 действия: {popped_n}")
    print(f"Осталось: {logger3.actions}")

    # Пример 4: pop_n с n больше размера стека
    print()
    print("Пример 4: pop_n с n больше размера стека")

    logger4 = ActionLogger()

    logger4.actions = []

    logger4.push(action1)
    logger4.push(action2)
    logger4.push(action3)

    print(f"До: {logger4.actions}")
    popped_all = logger4.pop_n(10)
    print(f"Запрошено 10")
    print(f"Извлечено: {popped_all}")
    print(f"Осталось: {logger4.actions}")

    # Пример 5: pop на пустом стеке
    print()
    print("Пример 5: pop на пустом стеке")

    logger5 = ActionLogger()
    logger5.actions = []

    result = logger5.pop()
    print(f"Результат pop на пустом стеке: {result}")

    # Пример 6: прямое пирсвоение
    print()
    print("Пример 6: прямое пирсвоение")

    logger6 = ActionLogger()
    logger6.clear()
    logger6.push_n(action1)

    print(f"До присвоения: {logger6.actions}")
    logger6.actions = [
        action1,
        action2,
        action3,
    ]
    print(f"После присвоения: {logger6.actions}")

    # Пример 7: отладка
    print()
    print("Пример 7: отладка")

    logger6 = ActionLogger()

    print(f"len: {len(logger6)}")
    print(f"str: {str(logger6)}")
    print(f"repr: {repr(logger6)}")
