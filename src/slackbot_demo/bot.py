"""
Slackbot Demo Implementation.

Main bot class that integrates with slackbot-permissions module
and provides interactive menu system.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

import structlog
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from slack_permissions import PermissionManager, CommandRegistry, UserManager
from slack_permissions.utils.decorators import require_permission, command
from slack_permissions.utils.exceptions import PermissionError, ValidationError

from .config import Settings, is_admin_user
from .commands import register_all_commands
from .middleware.permission_middleware import PermissionMiddleware
from .utils.menu_builder import MenuBuilder
from .utils.rate_limiter import RateLimiter


class SlackbotDemo:
    """
    Main Slackbot Demo class.
    
    Integrates slackbot-permissions with Slack Bolt framework
    to provide a feature-rich permission-based bot.
    """
    
    def __init__(self, slack_app: App, settings: Settings):
        """Initialize the demo bot."""
        self.app = slack_app
        self.settings = settings
        self.logger = structlog.get_logger()
        
        # Initialize permission system
        self.permission_manager = PermissionManager(
            cache_ttl=settings.permission_cache_ttl,
            strict_mode=settings.strict_mode
        )
        
        self.command_registry = CommandRegistry()
        self.user_manager = UserManager()
        
        # Initialize utilities
        self.menu_builder = MenuBuilder(self.command_registry, self.permission_manager)
        self.rate_limiter = RateLimiter(
            max_requests=settings.rate_limit_requests,
            window_seconds=settings.rate_limit_window
        )
        
        # Setup middleware
        self.permission_middleware = PermissionMiddleware(
            self.permission_manager,
            self.rate_limiter
        )
        
        # Register middleware
        self._setup_middleware()
        
        # Register commands
        self._setup_commands()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        self.logger.info("SlackbotDemo initialized successfully")
    
    def _setup_middleware(self) -> None:
        """Setup Slack Bolt middleware."""
        
        @self.app.middleware
        def permission_middleware(body, client, next):
            """Apply permission middleware to all requests."""
            return self.permission_middleware.process(body, client, next)
        
        @self.app.middleware
        def logging_middleware(body, logger, next):
            """Add structured logging to all requests."""
            user_id = body.get('user', {}).get('id', 'unknown')
            command = body.get('command', body.get('text', 'unknown'))
            
            with structlog.contextvars.bound_contextvars(
                user_id=user_id,
                command=command,
                timestamp=datetime.utcnow().isoformat()
            ):
                return next()
    
    def _setup_commands(self) -> None:
        """Register all bot commands."""
        
        # Register commands with the permission system
        register_all_commands(
            self.app,
            self.command_registry,
            self.permission_manager,
            self.user_manager
        )
        
        # Setup main menu command
        @self.app.command("/menu")
        def handle_menu_command(ack, body, client):
            """Handle the main menu command."""
            ack()
            self._show_interactive_menu(body, client)
        
        # Setup help command
        @self.app.command("/help")
        def handle_help_command(ack, body, client):
            """Handle help command."""
            ack()
            self._show_help(body, client)
    
    def _setup_event_handlers(self) -> None:
        """Setup Slack event handlers."""
        
        @self.app.event("app_mention")
        def handle_app_mention(body, client):
            """Handle app mentions."""
            self._show_interactive_menu(body, client)
        
        @self.app.event("message")
        def handle_direct_message(body, client):
            """Handle direct messages."""
            # Only respond to direct messages
            if body.get('event', {}).get('channel_type') == 'im':
                self._show_interactive_menu(body, client)
    
    def _show_interactive_menu(self, body: Dict[str, Any], client: WebClient) -> None:
        """Show interactive menu based on user permissions."""
        try:
            user_id = body.get('user', {}).get('id') or body.get('user_id')
            channel_id = body.get('channel', {}).get('id') or body.get('channel_id')
            
            if not user_id or not channel_id:
                self.logger.warning("Missing user_id or channel_id in menu request")
                return
            
            # Get user info
            user_info = self._get_user_info(client, user_id)
            
            # Ensure user exists in permission system
            self._ensure_user_exists(user_id, user_info)
            
            # Build menu based on permissions
            menu_blocks = self.menu_builder.build_menu(user_id)
            
            # Send interactive menu
            client.chat_postMessage(
                channel=channel_id,
                text="🤖 Available Commands",
                blocks=menu_blocks,
                user=user_id
            )
            
            self.logger.info(
                "Interactive menu displayed",
                user_id=user_id,
                channel_id=channel_id,
                commands_count=len(menu_blocks) - 1  # Exclude header
            )
            
        except SlackApiError as e:
            self.logger.error("Slack API error in menu", error=str(e))
            self._send_error_message(client, channel_id, "Failed to load menu")
        
        except Exception as e:
            self.logger.error("Unexpected error in menu", error=str(e), exc_info=True)
            self._send_error_message(client, channel_id, "An unexpected error occurred")
    
    def _show_help(self, body: Dict[str, Any], client: WebClient) -> None:
        """Show help information."""
        try:
            user_id = body.get('user_id')
            channel_id = body.get('channel_id')
            
            help_text = self._build_help_text(user_id)
            
            client.chat_postMessage(
                channel=channel_id,
                text="📚 Help & Documentation",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": help_text
                        }
                    }
                ]
            )
            
        except Exception as e:
            self.logger.error("Error showing help", error=str(e))
    
    def _build_help_text(self, user_id: str) -> str:
        """Build help text based on user permissions."""
        help_lines = [
            "🤖 *Slackbot Permissions Demo*",
            "",
            "*Available Commands:*",
            "• `/menu` - Show interactive command menu",
            "• `/help` - Show this help message",
            ""
        ]
        
        # Add commands user has access to
        available_commands = self.command_registry.get_available_commands(user_id)
        
        if available_commands:
            help_lines.append("*Your Available Commands:*")
            for cmd in available_commands:
                help_lines.append(f"• `/{cmd['name']}` - {cmd['description']}")
        else:
            help_lines.append("*No additional commands available.*")
            help_lines.append("Contact an admin to request permissions.")
        
        help_lines.extend([
            "",
            "*Need Help?*",
            "• Use `/menu` for interactive commands",
            "• Contact administrators for permission requests",
            "• Check bot status with `/status`"
        ])
        
        return "\n".join(help_lines)
    
    def _get_user_info(self, client: WebClient, user_id: str) -> Dict[str, Any]:
        """Get user information from Slack."""
        try:
            response = client.users_info(user=user_id)
            return response['user']
        except SlackApiError as e:
            self.logger.warning("Failed to get user info", user_id=user_id, error=str(e))
            return {'id': user_id, 'name': 'unknown'}
    
    def _ensure_user_exists(self, user_id: str, user_info: Dict[str, Any]) -> None:
        """Ensure user exists in permission system."""
        try:
            # Create user if doesn't exist
            self.user_manager.create_user(
                user_id=user_id,
                username=user_info.get('name', 'unknown'),
                email=user_info.get('profile', {}).get('email')
            )
            
            # Grant basic permissions to all users
            self.permission_manager.grant_permission(user_id, "read_status")
            
            # Grant admin permissions if configured
            if is_admin_user(user_id):
                admin_permissions = ["admin", "deployment", "read_logs", "manage_permissions"]
                for permission in admin_permissions:
                    self.permission_manager.grant_permission(user_id, permission)
                
                self.logger.info("Admin permissions granted", user_id=user_id)
            
        except Exception as e:
            self.logger.error("Failed to setup user", user_id=user_id, error=str(e))
    
    def _send_error_message(self, client: WebClient, channel_id: str, message: str) -> None:
        """Send error message to user."""
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ {message}",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"❌ *Error:* {message}"
                        }
                    }
                ]
            )
        except Exception as e:
            self.logger.error("Failed to send error message", error=str(e))
    
    def start(self) -> None:
        """Start the bot server."""
        try:
            # Use Socket Mode for development, HTTP for production
            if self.settings.debug:
                # Socket Mode (requires SLACK_APP_TOKEN)
                handler = SocketModeHandler(self.app, app_token=self.settings.slack_app_token)
                handler.start()
            else:
                # HTTP Mode
                self.app.start(port=self.settings.port)
                
        except Exception as e:
            self.logger.error("Failed to start bot server", error=str(e))
            raise
    
    def shutdown(self) -> None:
        """Gracefully shutdown the bot."""
        self.logger.info("Shutting down bot...")
        
        # Cleanup resources
        try:
            # Close any open connections
            # Save any pending data
            # Clear caches
            pass
        except Exception as e:
            self.logger.error("Error during shutdown", error=str(e))
        
        self.logger.info("Bot shutdown complete")
