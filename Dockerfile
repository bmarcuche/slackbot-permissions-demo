# Multi-stage build for production-ready container
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r slackbot && useradd -r -g slackbot slackbot

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/slackbot/.local

# Copy application code
COPY src/ ./src/
COPY .env.example .env

# Set ownership
RUN chown -R slackbot:slackbot /app

# Switch to non-root user
USER slackbot

# Add local bin to PATH
ENV PATH=/home/slackbot/.local/bin:$PATH

# Expose ports
EXPOSE 3000 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "-m", "slackbot_demo.main"]
