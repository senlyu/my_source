# --- Stage 1: Build Stage (used to install dependencies) ---
# Use Python 3.13 base image
FROM python:3.13-slim AS builder

# Set environment variables to prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Set Python output to be unbuffered, which helps in viewing logs in real-time
ENV PYTHONUNBUFFERED 1

# Install necessary system dependencies (e.g., build-essential, git, etc.)
# Pipenv can also be installed here
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && pip install pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy Pipfile and Pipfile.lock files
# This is to leverage Docker's caching mechanism
COPY Pipfile Pipfile.lock /app/

# Install dependencies to a temporary virtual environment or system path
# Here, they are installed to /usr/local/lib/python3.13/site-packages
RUN PIPENV_VENV_IN_PROJECT=off pipenv install --system --deploy 


# --- Stage 2: Runtime Stage (lean runtime environment) ---
# Use the same base image, but without build tools
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV TZ=America/Los_Angeles

# Create a non-root user
# Use the more common UID/GID 1000:1000
RUN groupadd -r appuser && useradd -r -u 1000 -g appuser appuser

# Set the working directory and ensure permissions
WORKDIR /app
RUN chown appuser:appuser /app

# Copy dependencies installed in the build stage
# Use --chown to ensure correct ownership
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Switch to a non-root user
USER appuser

# Copy the application code
# Use --chown to ensure correct ownership
COPY --chown=appuser:appuser . .

# Define the command to execute when the container starts (modify according to your actual main application file)
# Note: config.json will be mounted via volume, not copied into the image
ENTRYPOINT ["python", "-m", "src.main"]
CMD ["prod"]
