import logging
from pathlib import Path

# shared file handler
_file_handler: logging.FileHandler | None = None


def geqo_filter(record: logging.LogRecord) -> bool:
    """So that we get logs only from geqo.
    Otherwise logs migrate from matplotlib
    """

    return record.name.startswith("geqo")


def get_logger(
    name: str | None = None,
    level: int = logging.DEBUG,
    fmt: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    log_file: str = "app.log",
) -> logging.Logger:
    """
    Configures a single shared FileHandler for all loggers in the project.
    Prevents log corruption or truncation from multiple handlers writing to

    Usage (in any script):
        logger = get_logger(__name__)
        logger.info("Something happened.")
    """
    global _file_handler

    # ensuring file handler is created only once
    if _file_handler is None:
        log_path = Path(log_file)
        formatter = logging.Formatter(fmt)
        _file_handler = logging.FileHandler(
            log_path, mode="w", encoding="utf-8", delay=False
        )
        _file_handler.setFormatter(formatter)
        _file_handler.addFilter(geqo_filter)
        _file_handler.setLevel(level)

    # getting the logger for each script
    logger = logging.getLogger(name)

    if _file_handler not in logger.handlers:
        logger.addHandler(_file_handler)

    logger.setLevel(level)
    logger.propagate = False

    return logger
