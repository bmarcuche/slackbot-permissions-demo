# Contributing to Slackbot Permissions Demo

Thank you for your interest in contributing to the Slackbot Permissions Demo! This project showcases the capabilities of the `slackbot-permissions` module through a production-ready Slackbot implementation.

## 🚀 Quick Start

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone git@github.com:YOUR_ORG/slackbot-permissions-demo.git
   cd slackbot-permissions-demo
   ```
3. **Set up development environment**
   ```bash
   ./scripts/setup.sh
   ```
4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.8+
- Git
- Slack workspace for testing (optional)

### Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install slackbot-permissions in development mode
pip install -e ../slackbot-permissions  # if available locally
```

### Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your Slack credentials (for testing)
# SLACK_BOT_TOKEN=xoxb-your-token
# SLACK_SIGNING_SECRET=your-secret
```

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=slackbot_demo --cov-report=html

# Specific test categories
pytest -m unit
pytest -m integration
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/slackbot_demo
```

## 📝 Code Style

### Python Style
- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 88 characters
- Use type hints for all functions

### Documentation
- Clear docstrings for all public functions
- Include examples for complex functionality
- Update README.md for significant changes

### Example Code Style
```python
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

def process_command(
    user_id: str, 
    command: str, 
    permissions: List[str]
) -> Optional[Dict[str, str]]:
    """
    Process a user command with permission validation.
    
    Args:
        user_id: Slack user ID
        command: Command to execute
        permissions: List of user permissions
        
    Returns:
        Command result or None if unauthorized
        
    Example:
        >>> process_command("U123", "status", ["read_status"])
        {"status": "success", "message": "System healthy"}
    """
    logger.info("Processing command", user_id=user_id, command=command)
    
    # Implementation here
    return {"status": "success"}
```

## 🏗️ Architecture Guidelines

### Adding New Commands
1. Create command handler in appropriate module (`commands/`)
2. Register with CommandRegistry
3. Define required permissions
4. Add comprehensive tests
5. Update documentation

### Command Structure
```python
def register_my_commands(app, command_registry, permission_manager):
    """Register custom commands."""
    
    # Register with permission system
    command_registry.register_command(
        name="my_command",
        permission="my_permission",
        description="Description of command",
        category="Category"
    )
    
    @app.command("/my_command")
    def handle_my_command(ack, body, client):
        """Handle my custom command."""
        ack()
        
        user_id = body.get('user_id')
        channel_id = body.get('channel_id')
        
        # Check permissions
        if not permission_manager.check_permission(user_id, "my_permission"):
            client.chat_postMessage(
                channel=channel_id,
                text="❌ You don't have permission for this command"
            )
            return
        
        # Command implementation
        # ...
```

### Security Considerations
- Always validate user permissions
- Sanitize all user inputs
- Use structured logging with context
- Handle errors gracefully
- Follow principle of least privilege

## 🔄 Pull Request Process

### Before Submitting
- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] No linting errors
- [ ] Type checking passes
- [ ] Documentation updated
- [ ] Security review completed

### PR Description
Use the provided template and include:
- Clear description of changes
- Type of change (bug fix, feature, etc.)
- Testing performed
- Security considerations
- Documentation updates

### Review Process
1. Automated checks must pass
2. At least one maintainer review
3. Address feedback
4. Maintainer will merge when approved

## 🐛 Bug Reports

When reporting bugs:
1. Use the bug report template
2. Include reproduction steps
3. Provide environment details
4. Add relevant logs
5. Include screenshots if applicable

## 💡 Feature Requests

For new features:
1. Use the feature request template
2. Describe the use case
3. Propose implementation approach
4. Consider backwards compatibility

## 📚 Documentation

### Types of Documentation
- **Code Comments** - For complex logic
- **Docstrings** - For all public functions
- **README** - For setup and usage
- **Architecture** - For system design
- **API Docs** - For external interfaces

### Documentation Standards
- Clear and concise language
- Include examples where helpful
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

## 🎯 Project Goals

This project aims to:
- Demonstrate `slackbot-permissions` module capabilities
- Provide a production-ready Slackbot example
- Showcase security best practices
- Serve as a reference implementation

## 🤝 Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow the code of conduct

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and ideas
- **Code Review** - Tag maintainers for review

## 🏆 Recognition

Contributors will be:
- Listed in the contributors section
- Mentioned in release notes
- Invited to join as maintainers for significant contributions

---

Thank you for contributing to the Slackbot Permissions Demo! 🎉
