#!/bin/bash

# Slackbot Demo Setup Script
# Automates the development environment setup

set -e

echo "🤖 Setting up Slackbot Demo Development Environment"
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install slackbot-permissions in development mode
if [ -d "../slackbot-permissions" ]; then
    echo "🔗 Installing slackbot-permissions in development mode..."
    pip install -e ../slackbot-permissions
else
    echo "⚠️  slackbot-permissions not found locally, using PyPI version"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your Slack credentials"
else
    echo "✅ .env file already exists"
fi

# Create logs directory
mkdir -p logs

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
pytest tests/ -v

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Slack app credentials"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the bot: python src/slackbot_demo/main.py"
echo ""
echo "For more information, see README.md"
