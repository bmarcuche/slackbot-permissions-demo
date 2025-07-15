"""
Monitoring and Metrics.

Setup Prometheus metrics and health checks.
"""

import time
from typing import Dict, Any
from threading import Thread

import structlog
from prometheus_client import Counter, Histogram, Gauge, start_http_server


# Metrics
COMMAND_COUNTER = Counter(
    'slackbot_commands_total',
    'Total number of commands processed',
    ['command', 'user_id', 'status']
)

COMMAND_DURATION = Histogram(
    'slackbot_command_duration_seconds',
    'Time spent processing commands',
    ['command']
)

ACTIVE_USERS = Gauge(
    'slackbot_active_users',
    'Number of active users'
)

PERMISSION_CHECKS = Counter(
    'slackbot_permission_checks_total',
    'Total number of permission checks',
    ['result']
)

RATE_LIMIT_HITS = Counter(
    'slackbot_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['user_id']
)


def setup_metrics(port: int = 8080) -> None:
    """
    Setup Prometheus metrics server.
    
    Args:
        port: Port to serve metrics on
    """
    logger = structlog.get_logger()
    
    try:
        # Start metrics server in background thread
        def start_server():
            start_http_server(port)
            logger.info("Metrics server started", port=port)
        
        thread = Thread(target=start_server, daemon=True)
        thread.start()
        
    except Exception as e:
        logger.error("Failed to start metrics server", error=str(e))


def record_command(command: str, user_id: str, status: str, duration: float) -> None:
    """
    Record command execution metrics.
    
    Args:
        command: Command name
        user_id: User ID (anonymized for privacy)
        status: Command status (success/error)
        duration: Execution duration in seconds
    """
    # Anonymize user ID for privacy
    anonymized_user = f"user_{hash(user_id) % 10000}"
    
    COMMAND_COUNTER.labels(
        command=command,
        user_id=anonymized_user,
        status=status
    ).inc()
    
    COMMAND_DURATION.labels(command=command).observe(duration)


def record_permission_check(result: str) -> None:
    """
    Record permission check result.
    
    Args:
        result: Check result (allowed/denied)
    """
    PERMISSION_CHECKS.labels(result=result).inc()


def record_rate_limit_hit(user_id: str) -> None:
    """
    Record rate limit hit.
    
    Args:
        user_id: User ID (anonymized)
    """
    anonymized_user = f"user_{hash(user_id) % 10000}"
    RATE_LIMIT_HITS.labels(user_id=anonymized_user).inc()


def update_active_users(count: int) -> None:
    """
    Update active users gauge.
    
    Args:
        count: Number of active users
    """
    ACTIVE_USERS.set(count)


def get_health_status() -> Dict[str, Any]:
    """
    Get application health status.
    
    Returns:
        Health status dictionary
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "components": {
            "slack_api": "healthy",
            "permission_system": "healthy",
            "rate_limiter": "healthy"
        }
    }
