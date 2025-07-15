"""
Tests for SlackbotDemo.

Basic test structure for the demo bot functionality.
"""

import pytest
from unittest.mock import Mock, patch

from slackbot_demo import SlackbotDemo, Settings


class TestSlackbotDemo:
    """Test suite for SlackbotDemo."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock(spec=Settings)
        settings.slack_bot_token = "xoxb-test-token"
        settings.slack_signing_secret = "test-secret"
        settings.admin_users = ["U123456"]
        settings.permission_cache_ttl = 300
        settings.strict_mode = True
        settings.rate_limit_requests = 10
        settings.rate_limit_window = 60
        settings.enable_metrics = False
        return settings
    
    @pytest.fixture
    def mock_slack_app(self):
        """Mock Slack app for testing."""
        return Mock()
    
    def test_bot_initialization(self, mock_slack_app, mock_settings):
        """Test bot initializes correctly."""
        bot = SlackbotDemo(mock_slack_app, mock_settings)
        
        assert bot.app == mock_slack_app
        assert bot.settings == mock_settings
        assert bot.permission_manager is not None
        assert bot.command_registry is not None
        assert bot.user_manager is not None
    
    def test_menu_builder_initialization(self, mock_slack_app, mock_settings):
        """Test menu builder is initialized."""
        bot = SlackbotDemo(mock_slack_app, mock_settings)
        
        assert bot.menu_builder is not None
    
    def test_rate_limiter_initialization(self, mock_slack_app, mock_settings):
        """Test rate limiter is initialized."""
        bot = SlackbotDemo(mock_slack_app, mock_settings)
        
        assert bot.rate_limiter is not None
        assert bot.rate_limiter.max_requests == mock_settings.rate_limit_requests
        assert bot.rate_limiter.window_seconds == mock_settings.rate_limit_window


class TestConfiguration:
    """Test configuration handling."""
    
    def test_admin_user_check(self):
        """Test admin user identification."""
        from slackbot_demo.config import is_admin_user
        
        # This would need proper mocking of settings
        # For now, just test the function exists
        assert callable(is_admin_user)


if __name__ == "__main__":
    pytest.main([__file__])
