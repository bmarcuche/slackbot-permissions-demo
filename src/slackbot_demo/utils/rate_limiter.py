"""
Rate Limiter Utility.

Simple in-memory rate limiter for preventing command spam.
"""

import time
from typing import Dict, List
from collections import defaultdict, deque


class RateLimiter:
    """Simple sliding window rate limiter."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, user_id: str) -> bool:
        """
        Check if request is allowed for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] <= now - self.window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, user_id: str) -> int:
        """
        Get remaining requests for user in current window.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of remaining requests
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests
        while user_requests and user_requests[0] <= now - self.window_seconds:
            user_requests.popleft()
        
        return max(0, self.max_requests - len(user_requests))
    
    def get_reset_time(self, user_id: str) -> float:
        """
        Get time when rate limit resets for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Unix timestamp when limit resets
        """
        user_requests = self.requests[user_id]
        
        if not user_requests:
            return time.time()
        
        return user_requests[0] + self.window_seconds
    
    def clear_user(self, user_id: str) -> None:
        """
        Clear rate limit data for user.
        
        Args:
            user_id: User identifier
        """
        if user_id in self.requests:
            del self.requests[user_id]
    
    def clear_all(self) -> None:
        """Clear all rate limit data."""
        self.requests.clear()
