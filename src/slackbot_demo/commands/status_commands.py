"""
Status and Monitoring Commands.

Commands for checking system status, health, and metrics.
"""

import json
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any

import structlog
from slack_bolt import App
from slack_permissions import CommandRegistry, PermissionManager
from slack_permissions.utils.decorators import require_permission


def register_status_commands(
    app: App,
    command_registry: CommandRegistry,
    permission_manager: PermissionManager
) -> None:
    """Register status and monitoring commands."""
    
    logger = structlog.get_logger()
    
    # Register commands with permission system
    command_registry.register_command(
        name="status",
        permission="read_status",
        description="Check system status and health",
        category="Monitoring"
    )
    
    command_registry.register_command(
        name="health",
        permission="read_status",
        description="Detailed health check",
        category="Monitoring"
    )
    
    # Status command
    @app.command("/status")
    def handle_status_command(ack, body, client):
        """Handle status command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "read_status"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have permission to check status"
            )
            return
        
        try:
            status_info = _get_system_status()
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 System Status"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:* {status_info['status']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Uptime:* {status_info['uptime']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*CPU Usage:* {status_info['cpu_percent']}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Memory Usage:* {status_info['memory_percent']}%"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                        }
                    ]
                }
            ]
            
            client.chat_postMessage(
                channel=channel_id,
                text="📊 System Status",
                blocks=blocks
            )
            
            logger.info("Status command executed", user_id=user_id)
            
        except Exception as e:
            logger.error("Status command failed", user_id=user_id, error=str(e))
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Failed to get system status"
            )
    
    # Health command
    @app.command("/health")
    def handle_health_command(ack, body, client):
        """Handle detailed health check command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "read_status"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have permission to check health"
            )
            return
        
        try:
            health_info = _get_detailed_health()
            
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "💚 Health Check"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Overall Status:* {health_info['overall_status']}\n\n*Component Status:*"
                    }
                }
            ]
            
            # Add component status
            for component, status in health_info['components'].items():
                emoji = "✅" if status['healthy'] else "❌"
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{emoji} *{component}:* {status['message']}"
                    }
                })
            
            client.chat_postMessage(
                channel=channel_id,
                text="💚 Health Check",
                blocks=blocks
            )
            
            logger.info("Health command executed", user_id=user_id)
            
        except Exception as e:
            logger.error("Health command failed", user_id=user_id, error=str(e))
            client.chat_postMessage(
                channel=channel_id,
                text="❌ Failed to get health status"
            )


def _get_system_status() -> Dict[str, Any]:
    """Get basic system status information."""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Calculate uptime (simplified)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        return {
            "status": "🟢 Healthy" if cpu_percent < 80 and memory.percent < 80 else "🟡 Warning",
            "uptime": uptime_str,
            "cpu_percent": round(cpu_percent, 1),
            "memory_percent": round(memory.percent, 1)
        }
        
    except Exception:
        return {
            "status": "❌ Error",
            "uptime": "Unknown",
            "cpu_percent": 0,
            "memory_percent": 0
        }


def _get_detailed_health() -> Dict[str, Any]:
    """Get detailed health check information."""
    components = {}
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        components["CPU"] = {
            "healthy": cpu_percent < 80,
            "message": f"{cpu_percent:.1f}% usage"
        }
    except Exception:
        components["CPU"] = {
            "healthy": False,
            "message": "Unable to check CPU"
        }
    
    # Check memory
    try:
        memory = psutil.virtual_memory()
        components["Memory"] = {
            "healthy": memory.percent < 80,
            "message": f"{memory.percent:.1f}% usage"
        }
    except Exception:
        components["Memory"] = {
            "healthy": False,
            "message": "Unable to check memory"
        }
    
    # Check disk space
    try:
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        components["Disk"] = {
            "healthy": disk_percent < 80,
            "message": f"{disk_percent:.1f}% usage"
        }
    except Exception:
        components["Disk"] = {
            "healthy": False,
            "message": "Unable to check disk"
        }
    
    # Determine overall status
    all_healthy = all(comp["healthy"] for comp in components.values())
    overall_status = "🟢 All systems healthy" if all_healthy else "🟡 Some issues detected"
    
    return {
        "overall_status": overall_status,
        "components": components
    }
