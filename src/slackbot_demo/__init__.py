"""
Slackbot Permissions Demo.

A production-ready demonstration of the slackbot-permissions module
with interactive menus and role-based access control.
"""

__version__ = "1.0.0"
__title__ = "slackbot-demo"
__description__ = "Demo Slackbot showcasing slackbot-permissions module"
__author__ = "Bruno Marcuche"
__email__ = "bruno.marcuche@gmail.com"
__url__ = "https://github.com/bmarcuche/slackbot-demo"
__license__ = "MIT"

from .bot import SlackbotDemo
from .config import Settings, get_settings

__all__ = [
    "SlackbotDemo",
    "Settings",
    "get_settings"
]
