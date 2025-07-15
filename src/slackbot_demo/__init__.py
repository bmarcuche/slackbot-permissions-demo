"""
Slackbot Permissions Demo.

A production-ready demonstration of the slackbot-permissions module
with interactive menus and role-based access control.
"""

import os

__version__ = "1.0.0"
__title__ = "slackbot-demo"
__description__ = "Demo Slackbot showcasing slackbot-permissions module"
__author__ = os.getenv("PACKAGE_AUTHOR", "Slackbot Demo Contributors")
__email__ = os.getenv("PACKAGE_AUTHOR_EMAIL", "contributors@example.com")
__url__ = os.getenv("PACKAGE_URL", "https://github.com/your-org/slackbot-permissions-demo")
__license__ = "MIT"

from .bot import SlackbotDemo
from .config import Settings, get_settings

__all__ = [
    "SlackbotDemo",
    "Settings",
    "get_settings"
]
