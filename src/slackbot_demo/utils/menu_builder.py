"""
Menu Builder Utility.

Creates dynamic Slack Block Kit menus based on user permissions.
"""

from typing import List, Dict, Any
import structlog

from slack_permissions import CommandRegistry, PermissionManager


class MenuBuilder:
    """Builds interactive Slack menus based on user permissions."""
    
    def __init__(self, command_registry: CommandRegistry, permission_manager: PermissionManager):
        """Initialize menu builder."""
        self.command_registry = command_registry
        self.permission_manager = permission_manager
        self.logger = structlog.get_logger()
    
    def build_menu(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Build interactive menu blocks for user.
        
        Args:
            user_id: Slack user ID
            
        Returns:
            List of Slack Block Kit blocks
        """
        try:
            # Get commands user has access to
            available_commands = self.command_registry.get_available_commands(user_id)
            
            if not available_commands:
                return self._build_no_commands_menu()
            
            # Build menu blocks
            blocks = [
                self._build_header_block(),
                self._build_divider_block()
            ]
            
            # Group commands by category
            categorized_commands = self._categorize_commands(available_commands)
            
            # Add command sections
            for category, commands in categorized_commands.items():
                if commands:
                    blocks.extend(self._build_category_section(category, commands))
            
            # Add footer
            blocks.extend([
                self._build_divider_block(),
                self._build_footer_block()
            ])
            
            return blocks
            
        except Exception as e:
            self.logger.error("Failed to build menu", user_id=user_id, error=str(e))
            return self._build_error_menu()
    
    def _build_header_block(self) -> Dict[str, Any]:
        """Build menu header block."""
        return {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🤖 Available Commands"
            }
        }
    
    def _build_divider_block(self) -> Dict[str, Any]:
        """Build divider block."""
        return {"type": "divider"}
    
    def _build_category_section(self, category: str, commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build a category section with commands."""
        blocks = []
        
        # Category header
        if category != "General":
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{self._get_category_emoji(category)} {category}*"
                }
            })
        
        # Command buttons
        for command in commands:
            blocks.append(self._build_command_block(command))
        
        return blocks
    
    def _build_command_block(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Build a single command block."""
        emoji = self._get_command_emoji(command['name'])
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *{command['name'].title()}*\n{command['description']}"
            },
            "accessory": {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": f"Run /{command['name']}"
                },
                "value": command['name'],
                "action_id": f"run_command_{command['name']}"
            }
        }
    
    def _build_footer_block(self) -> Dict[str, Any]:
        """Build menu footer block."""
        return {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "💡 *Tip:* You can also type commands directly (e.g., `/status`)"
                }
            ]
        }
    
    def _build_no_commands_menu(self) -> List[Dict[str, Any]]:
        """Build menu when user has no available commands."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🔒 *No Commands Available*\n\nYou don't have permission to use any commands yet.\nContact an administrator to request access."
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📞 Need help? Use `/help` for more information"
                    }
                ]
            }
        ]
    
    def _build_error_menu(self) -> List[Dict[str, Any]]:
        """Build error menu when menu building fails."""
        return [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "❌ *Error Loading Menu*\n\nSorry, there was an error loading your available commands.\nPlease try again or contact support."
                }
            }
        ]
    
    def _categorize_commands(self, commands: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize commands by type."""
        categories = {
            "General": [],
            "Development": [],
            "Administration": [],
            "Monitoring": []
        }
        
        for command in commands:
            category = self._get_command_category(command['name'])
            if category in categories:
                categories[category].append(command)
            else:
                categories["General"].append(command)
        
        return categories
    
    def _get_command_category(self, command_name: str) -> str:
        """Get category for command."""
        category_map = {
            "status": "Monitoring",
            "health": "Monitoring",
            "metrics": "Monitoring",
            "deploy": "Development",
            "build": "Development",
            "logs": "Development",
            "admin": "Administration",
            "permissions": "Administration",
            "users": "Administration"
        }
        
        return category_map.get(command_name.lower(), "General")
    
    def _get_category_emoji(self, category: str) -> str:
        """Get emoji for category."""
        emoji_map = {
            "General": "📋",
            "Development": "🚀",
            "Administration": "⚙️",
            "Monitoring": "📊"
        }
        
        return emoji_map.get(category, "📋")
    
    def _get_command_emoji(self, command_name: str) -> str:
        """Get emoji for command."""
        emoji_map = {
            "status": "📊",
            "health": "💚",
            "deploy": "🚀",
            "build": "🔨",
            "admin": "⚙️",
            "permissions": "🔐",
            "users": "👥",
            "logs": "📝",
            "help": "❓",
            "menu": "📋"
        }
        
        return emoji_map.get(command_name.lower(), "🔹")
