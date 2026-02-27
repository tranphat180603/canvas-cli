FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Copy all files
COPY . .

# Install Python dependencies using uv sync
RUN uv sync --no-dev

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

# Expose port (use default of 8000 if PORT not set)
EXPOSE 8000
ARG PORT
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD sh -c 'curl -f http://localhost:${PORT:-8000}/health || exit 1'

# Run the FastMCP server with HTTP transport
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["uv run python -m canvas_cli.server_fastmcp"]
