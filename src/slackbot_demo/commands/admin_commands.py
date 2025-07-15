"""
Administration Commands.

Commands for managing permissions, users, and system administration.
"""

from datetime import datetime
from typing import Dict, Any, List

import structlog
from slack_bolt import App
from slack_permissions import CommandRegistry, PermissionManager, UserManager


def register_admin_commands(
    app: App,
    command_registry: CommandRegistry,
    permission_manager: PermissionManager,
    user_manager: UserManager
) -> None:
    """Register administration commands."""
    
    logger = structlog.get_logger()
    
    # Register commands with permission system
    command_registry.register_command(
        name="admin",
        permission="admin",
        description="Admin control panel",
        category="Administration"
    )
    
    command_registry.register_command(
        name="permissions",
        permission="manage_permissions",
        description="Manage user permissions",
        category="Administration"
    )
    
    command_registry.register_command(
        name="users",
        permission="admin",
        description="Manage users",
        category="Administration"
    )
    
    # Admin panel command
    @app.command("/admin")
    def handle_admin_command(ack, body, client):
        """Handle admin panel command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "admin"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have admin permissions"
            )
            return
        
        try:
            admin_info = _get_admin_info(permission_manager, user_manager)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚙️ Admin Control Panel"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*System Overview*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Users:* {admin_info['total_users']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Active Permissions:* {admin_info['total_permissions']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Registered Commands:* {admin_info['total_commands']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Admin Users:* {admin_info['admin_users']}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*Quick Actions*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "👥 Manage Users"
                            },
                            "value": "manage_users",
                            "action_id": "admin_manage_users"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "🔐 Manage Permissions"
                            },
                            "value": "manage_permissions",
                            "action_id": "admin_manage_permissions"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📊 View Audit Log"
                            },
                            "value": "view_audit",
                            "action_id": "admin_view_audit"
                        }
                    ]
                }
            ]
            
            client.chat_postMessage(
                channel=channel_id,
                text="⚙️ Admin Control Panel",
                blocks=blocks
            )
            
            logger.info("Admin command executed", user_id=user_id)
            
        except Exception as e:
            logger.error("Admin command failed", user_id=user_id, error=str(e))
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Failed to load admin panel"
            )
    
    # Permissions management command
    @app.command("/permissions")
    def handle_permissions_command(ack, body, client):
        """Handle permissions management command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        text = body.get('text', '').strip()
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "manage_permissions"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have permission to manage permissions"
            )
            return
        
        try:
            if not text:
                # Show permissions overview
                _show_permissions_overview(client, channel_id, permission_manager, user_manager)
            else:
                # Parse command arguments
                args = text.split()
                if len(args) >= 3:
                    action = args[0].lower()  # grant/revoke
                    target_user = args[1]     # user ID or @username
                    permission = args[2]      # permission name
                    
                    if action == "grant":
                        _grant_permission(client, channel_id, permission_manager, target_user, permission, user_id)
                    elif action == "revoke":
                        _revoke_permission(client, channel_id, permission_manager, target_user, permission, user_id)
                    else:
                        _show_permissions_help(client, channel_id)
                else:
                    _show_permissions_help(client, channel_id)
            
            logger.info("Permissions command executed", user_id=user_id, args=text)
            
        except Exception as e:
            logger.error("Permissions command failed", user_id=user_id, error=str(e))
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Failed to manage permissions"
            )
    
    # Users management command
    @app.command("/users")
    def handle_users_command(ack, body, client):
        """Handle users management command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "admin"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have admin permissions"
            )
            return
        
        try:
            users_info = _get_users_info(user_manager, permission_manager)
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "👥 User Management"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Total Users:* {len(users_info)}"
                    }
                }
            ]
            
            # Add user list (limit to first 10)
            for user in users_info[:10]:
                user_text = f"*{user['username']}* (`{user['user_id']}`)\n"
                user_text += f"Permissions: {', '.join(user['permissions']) if user['permissions'] else 'None'}"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": user_text
                    }
                })
            
            if len(users_info) > 10:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"... and {len(users_info) - 10} more users"
                        }
                    ]
                })
            
            client.chat_postMessage(
                channel=channel_id,
                text="👥 User Management",
                blocks=blocks
            )
            
            logger.info("Users command executed", user_id=user_id)
            
        except Exception as e:
            logger.error("Users command failed", user_id=user_id, error=str(e))
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Failed to load user information"
            )


def _get_admin_info(permission_manager: PermissionManager, user_manager: UserManager) -> Dict[str, Any]:
    """Get admin panel information."""
    # This would normally query the actual data
    # For demo purposes, we'll return mock data
    return {
        "total_users": 15,
        "total_permissions": 42,
        "total_commands": 8,
        "admin_users": 3
    }


def _show_permissions_overview(client, channel_id: str, permission_manager: PermissionManager, user_manager: UserManager):
    """Show permissions overview."""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🔐 Permissions Overview"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Available Permissions:*\n• `read_status` - View system status\n• `deployment` - Deploy applications\n• `read_logs` - View application logs\n• `admin` - Admin panel access\n• `manage_permissions` - Manage user permissions"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Usage:*\n• `/permissions grant @user permission_name`\n• `/permissions revoke @user permission_name`\n• `/permissions` - Show this overview"
            }
        }
    ]
    
    client.chat_postMessage(
        channel=channel_id,
        text="🔐 Permissions Overview",
        blocks=blocks
    )


def _show_permissions_help(client, channel_id: str):
    """Show permissions command help."""
    client.chat_postMessage(
        channel=channel_id,
        text="❓ *Permissions Command Help*\n\n*Usage:*\n• `/permissions grant @user permission_name`\n• `/permissions revoke @user permission_name`\n• `/permissions` - Show overview\n\n*Example:*\n`/permissions grant @john deployment`"
    )


def _grant_permission(client, channel_id: str, permission_manager: PermissionManager, target_user: str, permission: str, admin_user: str):
    """Grant permission to user."""
    try:
        # Clean up user ID (remove @ if present)
        if target_user.startswith('@'):
            target_user = target_user[1:]
        
        # For demo, we'll simulate the permission grant
        success = True  # permission_manager.grant_permission(target_user, permission)
        
        if success:
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Permission `{permission}` granted to <@{target_user}>"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Failed to grant permission `{permission}` to <@{target_user}>"
            )
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error granting permission: {str(e)}"
        )


def _revoke_permission(client, channel_id: str, permission_manager: PermissionManager, target_user: str, permission: str, admin_user: str):
    """Revoke permission from user."""
    try:
        # Clean up user ID (remove @ if present)
        if target_user.startswith('@'):
            target_user = target_user[1:]
        
        # For demo, we'll simulate the permission revoke
        success = True  # permission_manager.revoke_permission(target_user, permission)
        
        if success:
            client.chat_postMessage(
                channel=channel_id,
                text=f"✅ Permission `{permission}` revoked from <@{target_user}>"
            )
        else:
            client.chat_postMessage(
                channel=channel_id,
                text=f"❌ Failed to revoke permission `{permission}` from <@{target_user}>"
            )
    except Exception as e:
        client.chat_postMessage(
            channel=channel_id,
            text=f"❌ Error revoking permission: {str(e)}"
        )


def _get_users_info(user_manager: UserManager, permission_manager: PermissionManager) -> List[Dict[str, Any]]:
    """Get users information."""
    # For demo purposes, return mock data
    return [
        {
            "user_id": "U123456",
            "username": "john.doe",
            "permissions": ["read_status", "deployment"]
        },
        {
            "user_id": "U789012",
            "username": "jane.smith",
            "permissions": ["read_status", "admin", "manage_permissions"]
        },
        {
            "user_id": "U345678",
            "username": "bob.wilson",
            "permissions": ["read_status"]
        }
    ]
