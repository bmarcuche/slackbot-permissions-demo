"""
Logging Configuration.

Setup structured logging with appropriate formatters and handlers.
"""

import logging
import sys
from typing import Any, Dict

import structlog


def setup_logging(log_level: str = "INFO", debug: bool = False) -> None:
    """
    Setup structured logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug: Enable debug mode with more verbose output
    """
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.add_logger_name,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s" if debug else None,
        stream=sys.stdout
    )
    
    # Reduce noise from third-party libraries
    logging.getLogger("slack_bolt").setLevel(logging.WARNING)
    logging.getLogger("slack_sdk").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Create application logger
    logger = structlog.get_logger("slackbot_demo")
    logger.info("Logging configured", level=log_level, debug=debug)
