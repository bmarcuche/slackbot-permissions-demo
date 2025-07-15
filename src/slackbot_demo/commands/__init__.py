"""
Command Registration Module.

Registers all bot commands with the Slack app and permission system.
"""

from slack_bolt import App
from slack_permissions import CommandRegistry, PermissionManager, UserManager

from .status_commands import register_status_commands
from .admin_commands import register_admin_commands
from .dev_commands import register_dev_commands


def register_all_commands(
    app: App,
    command_registry: CommandRegistry,
    permission_manager: PermissionManager,
    user_manager: UserManager
) -> None:
    """
    Register all bot commands.
    
    Args:
        app: Slack Bolt app instance
        command_registry: Command registry for permission system
        permission_manager: Permission manager instance
        user_manager: User manager instance
    """
    
    # Register command categories
    register_status_commands(app, command_registry, permission_manager)
    register_dev_commands(app, command_registry, permission_manager)
    register_admin_commands(app, command_registry, permission_manager, user_manager)
