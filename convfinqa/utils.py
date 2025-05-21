from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Iterable


def stringify(value: Any) -> str:
    """Return a clean string whether *value* is a list or already a str."""
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return "\n".join(map(str, value))
    return str(value)


def configure_logging(log_file: str | Path = "convfinqa.log") -> logging.Logger:
    """Configure & return a root logger shared across the app."""
    logger = logging.getLogger("convfinqa")
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    logger.setLevel(logging.INFO)

    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter(fmt))

    file_handler = logging.FileHandler(str(log_file), encoding="utf-8", mode="w")
    file_handler.setFormatter(logging.Formatter(fmt))

    logger.handlers.clear()
    logger.addHandler(stream)
    logger.addHandler(file_handler)
    return logger


def json_dumps(obj: Any) -> str:
    """Dump *obj* to JSON with UTF-8 safely preserved."""
    return json.dumps(obj, ensure_ascii=False, indent=2)
