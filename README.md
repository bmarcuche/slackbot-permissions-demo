# Slackbot Permissions Demo

A minimal Slackbot that demonstrates the capabilities of the `slackbot-permissions` module with an interactive menu system and role-based access control.

## 🎯 Purpose

This demo bot showcases:
- **Interactive Menu System** - Dynamic command menus based on user permissions
- **Role-Based Access Control** - Different commands for different user roles
- **Permission Management** - Grant/revoke permissions through Slack
- **Security Features** - Input validation, audit logging, and secure defaults
- **Production Patterns** - Error handling, monitoring, and structured logging

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Slack workspace with bot permissions
- Slack app with Bot Token and Signing Secret

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd slackbot-demo
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your Slack credentials
   ```

3. **Run the Bot**
   ```bash
   python src/slackbot_demo/main.py
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Required
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret

# Optional
LOG_LEVEL=INFO
ADMIN_USERS=U123456,U789012
PERMISSION_CACHE_TTL=300
```

### Slack App Setup

1. Create a new Slack app at https://api.slack.com/apps
2. Add Bot Token Scopes:
   - `chat:write`
   - `commands`
   - `users:read`
   - `channels:read`
3. Install app to workspace
4. Copy Bot User OAuth Token and Signing Secret

## 🎮 Usage

### Available Commands

- `/menu` - Show interactive command menu
- `/status` - Check bot status (all users)
- `/deploy` - Deploy application (requires deployment permission)
- `/admin` - Admin panel (requires admin permission)
- `/permissions` - Manage user permissions (admin only)

### Permission Roles

- **User** - Basic commands (status, help)
- **Developer** - Development commands (deploy, logs)
- **Admin** - All commands + permission management

### Interactive Menu

The bot provides a dynamic menu system that shows only commands the user has permission to execute:

```
🤖 Available Commands
┌─────────────────────────────────┐
│ 📊 Status - Check system status │
│ 🚀 Deploy - Deploy application  │
│ ⚙️  Admin - Admin panel         │
└─────────────────────────────────┘
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=slackbot_demo --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

## 🔒 Security Features

- **Input Validation** - All user inputs are sanitized
- **Permission Checks** - Commands require explicit permissions
- **Audit Logging** - All actions are logged with user context
- **Rate Limiting** - Prevents command spam
- **Secure Defaults** - Fail-safe permission model

## 📊 Monitoring

The bot exposes metrics and health checks:

- **Health Check** - `GET /health`
- **Metrics** - `GET /metrics` (Prometheus format)
- **Logs** - Structured JSON logging

## 🛠️ Development

### Project Structure

```
slackbot-demo/
├── src/slackbot_demo/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── bot.py               # Slack bot implementation
│   ├── commands/            # Command handlers
│   ├── middleware/          # Permission middleware
│   ├── utils/               # Utilities and helpers
│   └── config.py            # Configuration management
├── tests/                   # Test suite
├── docs/                    # Documentation
├── scripts/                 # Development scripts
└── requirements.txt         # Dependencies
```

### Adding New Commands

1. Create command handler in `src/slackbot_demo/commands/`
2. Register command with required permissions
3. Add tests in `tests/commands/`
4. Update documentation

Example:
```python
from slackbot_permissions.utils import require_permission, command

@command(
    name="new_command",
    permission="custom_permission",
    description="Description of new command"
)
@require_permission("custom_permission")
def handle_new_command(client, message, context):
    # Command implementation
    pass
```

## 🚀 Deployment

### Docker

```bash
docker build -t slackbot-demo .
docker run -d --env-file .env slackbot-demo
```

### Production Considerations

- Use environment-specific configuration
- Enable structured logging
- Set up monitoring and alerting
- Configure proper secret management
- Implement graceful shutdown handling

## 📝 API Documentation

### Slack Commands

| Command | Permission | Description |
|---------|------------|-------------|
| `/menu` | none | Show interactive menu |
| `/status` | `read_status` | System status |
| `/deploy` | `deployment` | Deploy application |
| `/admin` | `admin` | Admin panel |
| `/permissions` | `admin` | Manage permissions |

### Permission System

The bot uses the `slackbot-permissions` module for access control:

- **Hierarchical Permissions** - Admin > Developer > User
- **Dynamic Menus** - Only show available commands
- **Audit Trail** - Log all permission changes
- **Slack Integration** - Sync with Slack user groups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Bot not responding:**
- Check Slack app permissions
- Verify bot token and signing secret
- Check bot is invited to channel

**Permission errors:**
- Ensure user has required permissions
- Check admin user configuration
- Review audit logs for details

**Connection issues:**
- Verify network connectivity
- Check Slack API status
- Review application logs

### Support

- Check the [Issues](../../issues) page
- Review [Documentation](docs/)
- Contact maintainers

---

Built with ❤️ using [slackbot-permissions](../slackbot-permissions)
