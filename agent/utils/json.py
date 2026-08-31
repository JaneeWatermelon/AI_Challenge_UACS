import json
from utils.logger import get_logger

logger = get_logger(__name__)

def recursive_serializer(obj, seen=None):
    if seen is None:
        seen = set()

    # Защита от циклических ссылок
    obj_id = id(obj)

    if obj_id in seen:
        return "<circular reference>"

    seen.add(obj_id)

    try:
        if hasattr(obj, "to_json"):
            data = obj.to_json()
            return {
                key: recursive_serializer(value, seen)
                for key, value in data.items()
            }

        if hasattr(obj, "__dict__"):
            return {
                key: recursive_serializer(value, seen)
                for key, value in obj.__dict__.items()
            }

        if isinstance(obj, dict):
            return {
                key: recursive_serializer(value, seen)
                for key, value in obj.items()
            }

        if isinstance(obj, (list, tuple)):
            return [
                recursive_serializer(item, seen)
                for item in obj
            ]

        return obj

    except Exception as e:
        logger.exception(f"recursive_serializer error: {e}")

    finally:
        seen.remove(obj_id)

if __name__ == "__main__":
    # Пример использования
    class NestedObject:
        def __init__(self, name, details):
            self.name = name
            self.details = details  # Это может быть другой объект или словарь

    nested_data = NestedObject("Пример", {"nested_key": "nested_value", "numbers": [1, 2, 3]})

    # Сериализуем объект
    serialized_data = json.dumps(nested_data, default=recursive_serializer)
    print(serialized_data)