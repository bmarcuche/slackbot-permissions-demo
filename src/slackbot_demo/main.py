"""
Slackbot Permissions Demo - Main Application Entry Point.

A production-ready Slackbot that demonstrates the slackbot-permissions module
with interactive menus and role-based access control.
"""

import logging
import signal
import sys
from typing import NoReturn

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from .config import get_settings
from .bot import SlackbotDemo
from .utils.logging import setup_logging
from .utils.monitoring import setup_metrics


def setup_signal_handlers(app: SlackbotDemo) -> None:
    """Setup graceful shutdown signal handlers."""
    
    def signal_handler(signum: int, frame) -> NoReturn:
        """Handle shutdown signals gracefully."""
        logger = structlog.get_logger()
        logger.info("Received shutdown signal", signal=signum)
        
        # Perform cleanup
        app.shutdown()
        
        logger.info("Shutdown complete")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main() -> None:
    """Main application entry point."""
    
    # Load configuration
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings.log_level, settings.debug)
    logger = structlog.get_logger()
    
    logger.info(
        "Starting Slackbot Permissions Demo",
        version="1.0.0",
        log_level=settings.log_level,
        debug=settings.debug
    )
    
    try:
        # Setup monitoring
        if settings.enable_metrics:
            setup_metrics(settings.metrics_port)
            logger.info("Metrics enabled", port=settings.metrics_port)
        
        # Initialize Slack app
        slack_app = App(
            token=settings.slack_bot_token,
            signing_secret=settings.slack_signing_secret,
            process_before_response=True
        )
        
        # Initialize demo bot
        demo_bot = SlackbotDemo(slack_app, settings)
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(demo_bot)
        
        logger.info("Bot initialized successfully")
        
        # Start the bot
        logger.info("Starting bot server", port=settings.port)
        demo_bot.start()
        
    except Exception as e:
        logger.error("Failed to start bot", error=str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
