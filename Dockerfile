# Use a lightweight official Python image
FROM python:3.12-slim-bookworm

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables for uv and python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Create the virtual environment outside of /app so it isn't masked by the volume mount
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install system dependencies
# libmagic1: often needed for file type detection
# build-essential: for compiling C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libmagic1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first to leverage cache
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# We omit --frozen to allow uv to resolve the new 'docling' dependency 
# which I added to pyproject.toml but isn't in uv.lock yet.
# --no-install-project installs dependencies but not the project itself
RUN uv sync --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Install the project
RUN uv sync --no-dev

# Expose the API port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
