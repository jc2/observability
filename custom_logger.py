import logging
from typing import Any, Dict, List

import structlog
from elasticapm.handlers.structlog import structlog_processor


def edit_event_name(
    logger: logging.Logger, method_name: str, event_dict: Dict[Any, Any]
) -> Dict[Any, Any]:
    """Edit the event dict to change the event name so we don't clobber Elastic indices"""
    event = event_dict.pop("event")
    event_dict["message"] = event
    return event_dict

def add_traceback_to_message(
    logger: logging.Logger, method_name: str, event_dict: Dict[Any, Any]
) -> Dict[Any, Any]:
    if "exception" in event_dict:
        event_dict["message"] += f"\n{event_dict['exception']}"
        event_dict.pop("exception")
    return event_dict


def get_logger(app_name, log_level=logging.DEBUG):
    shared_processors: List[Any] = [
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(),
        structlog_processor,
        edit_event_name,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        add_traceback_to_message
    ]

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    structlog_formatter: Any = structlog.stdlib.ProcessorFormatter(
        processor=structlog.processors.JSONRenderer(),
        foreign_pre_chain=shared_processors,
    )
    new_logger = logging.getLogger(app_name)
    handler = logging.FileHandler(f"{app_name}_custom.log")
    handler.setFormatter(structlog_formatter)
    new_logger.addHandler(handler)
    new_logger.setLevel(log_level)
    return new_logger


def runtime_logging(f):
    def wrapper(*args, **kwargs):
        logger.debug(f"Starting {f.__name__}")
        a = f(*args, **kwargs)
        logger.debug(f"Ending {f.__name__}")
        return a
    wrapper.__name__ = f.__name__
    return wrapper


if __name__ == "__main__":
    logger = get_logger('test')