"""Custom logger."""
import logging

from client import settings


def logger(name: str) -> logging.Logger:
    """Custom logger."""
    # Configure logging
    custom_logger: logging.Logger = logging.getLogger(name)

    # Create logging handler
    f_handler = logging.FileHandler(settings.log_file)
    c_handler = logging.StreamHandler()
    f_handler.setLevel(logging.ERROR)
    c_handler.setLevel(logging.INFO)

    # Create logging formatter and add it to the handler
    f_format: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    c_format: logging.Formatter = logging.Formatter(
        "%(name)s - %(levelname)s - %(message)s"
    )
    f_handler.setFormatter(f_format)
    c_handler.setFormatter(c_format)

    # Add the handlers to the logger
    custom_logger.addHandler(f_handler)
    custom_logger.addHandler(c_handler)

    return custom_logger
