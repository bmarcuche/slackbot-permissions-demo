"""
Permission Middleware.

Middleware for handling permission checks and rate limiting.
"""

from typing import Dict, Any, Callable
import structlog

from slack_permissions import PermissionManager
from ..utils.rate_limiter import RateLimiter


class PermissionMiddleware:
    """Middleware for permission checking and rate limiting."""
    
    def __init__(self, permission_manager: PermissionManager, rate_limiter: RateLimiter):
        """Initialize permission middleware."""
        self.permission_manager = permission_manager
        self.rate_limiter = rate_limiter
        self.logger = structlog.get_logger()
    
    def process(self, body: Dict[str, Any], client, next: Callable) -> Any:
        """
        Process request through permission middleware.
        
        Args:
            body: Slack request body
            client: Slack client
            next: Next middleware function
            
        Returns:
            Result of next middleware or None if blocked
        """
        try:
            user_id = self._extract_user_id(body)
            
            if not user_id:
                self.logger.warning("No user ID found in request")
                return next()
            
            # Check rate limiting
            if not self.rate_limiter.is_allowed(user_id):
                self.logger.warning("Rate limit exceeded", user_id=user_id)
                self._send_rate_limit_message(client, body)
                return
            
            # Log request
            self.logger.info(
                "Processing request",
                user_id=user_id,
                command=self._extract_command(body)
            )
            
            # Continue to next middleware
            return next()
            
        except Exception as e:
            self.logger.error("Permission middleware error", error=str(e), exc_info=True)
            return next()  # Continue on error to avoid breaking the bot
    
    def _extract_user_id(self, body: Dict[str, Any]) -> str:
        """Extract user ID from request body."""
        # Try different locations where user ID might be
        user_id = (
            body.get('user_id') or
            body.get('user', {}).get('id') or
            body.get('event', {}).get('user')
        )
        
        return user_id
    
    def _extract_command(self, body: Dict[str, Any]) -> str:
        """Extract command from request body."""
        return (
            body.get('command') or
            body.get('text', '').split()[0] if body.get('text') else 'unknown'
        )
    
    def _send_rate_limit_message(self, client, body: Dict[str, Any]) -> None:
        """Send rate limit exceeded message."""
        try:
            channel_id = (
                body.get('channel_id') or
                body.get('channel', {}).get('id') or
                body.get('event', {}).get('channel')
            )
            
            if channel_id:
                client.chat_postMessage(
                    channel=channel_id,
                    text="⚠️ Rate limit exceeded. Please wait before sending another command.",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "⚠️ *Rate Limit Exceeded*\n\nYou're sending commands too quickly. Please wait a moment before trying again."
                            }
                        }
                    ]
                )
        except Exception as e:
            self.logger.error("Failed to send rate limit message", error=str(e))
