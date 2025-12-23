import logging
import os
import sys
from typing import Any, Dict

PII_FIELDS = {
    "name",
    "username",
    "email",
    "password",
    "token",
    "api_key",
    "secret",
    "phone",
    "address",
    "user_id",
    "new_name",
    "old_name",
}


class PIIMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "msg"):
            record.msg = self._mask_pii_in_string(str(record.msg))

        if hasattr(record, "__dict__"):
            for key, value in list(record.__dict__.items()):
                if key.lower() in PII_FIELDS:
                    setattr(record, key, "[---MASKED---]")

        return True

    def _mask_pii_in_string(self, text: str) -> str:
        return text


def setup_logger(name: str = "app logger") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # Формат логов
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    handler.addFilter(PIIMaskingFilter())

    logger.addHandler(handler)

    return logger


def mask_pii(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return data

    masked = data.copy()
    for key in masked:
        if key.lower() in PII_FIELDS:
            masked[key] = "[---MASKED---]"
        elif isinstance(masked[key], dict):
            masked[key] = mask_pii(masked[key])

    return masked


# Синглетон логгера для приложения
logger = setup_logger()
