import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(message)s"
)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Не добавляем handlers повторно
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    # Запись в файл с ротацией
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger