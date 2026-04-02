import logging
from pathlib import Path

from src.config import settings
from src.utils.request_context import get_request_id


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


def configure_logging() -> None:
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    Path(settings.server_out_log_path).touch(exist_ok=True)
    Path(settings.server_error_log_path).touch(exist_ok=True)

    log_format = "%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s"
    formatter = logging.Formatter(log_format)
    request_id_filter = RequestIdFilter()

    out_handler = logging.FileHandler(settings.server_out_log_path, encoding="utf-8")
    out_handler.setLevel(logging.INFO)
    out_handler.setFormatter(formatter)
    out_handler.addFilter(request_id_filter)

    error_handler = logging.FileHandler(settings.server_error_log_path, encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.addFilter(request_id_filter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(request_id_filter)

    root_logger.setLevel(settings.app_log_level)
    root_logger.addHandler(out_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
