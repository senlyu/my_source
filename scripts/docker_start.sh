#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Configuration and state directories
LOG_DIR="log"
HISTORY_DIR="history"
SESSION_DIR="session"
CONFIG_FILE="config.json"

# Check if config.json exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: $CONFIG_FILE not found. Please create it from config.example.json."
    exit 1
fi

# Create necessary directories if they don't exist
mkdir -p "$LOG_DIR" "$HISTORY_DIR" "$SESSION_DIR"

# Ensure host directories have appropriate permissions for the appuser (UID 1000)
# This assumes the user running scripts/docker_start.sh has permissions to chown these.
# If the host user is not 1000, this might require adjustment or manual chown.
# For simplicity, setting ownership to the current user (assuming it's the appuser in the container)
# You might need to adjust UID/GID based on your host environment
HOST_UID=$(id -u)
HOST_GID=$(id -g)

# Only chown if the current user is not root, and if the directories don't have expected ownership
if [ "$HOST_UID" -ne 0 ]; then
    if [ "$(stat -c %u "$LOG_DIR")" != "$HOST_UID" ]; then
        chown -R "$HOST_UID":"$HOST_GID" "$LOG_DIR"
    fi
    if [ "$(stat -c %u "$HISTORY_DIR")" != "$HOST_UID" ]; then
        chown -R "$HOST_UID":"$HOST_GID" "$HISTORY_DIR"
    fi
    if [ "$(stat -c %u "$SESSION_DIR")" != "$HOST_UID" ]; then
        chown -R "$HOST_UID":"$HOST_GID" "$SESSION_DIR"
    fi
fi


# Define the Docker image name
DOCKER_IMAGE_NAME="my-source:latest"
CONTAINER_NAME="my-source-runner"

# Get the environment argument (e.g., prod, dev)
ENVIRONMENT=${1:-prod} # Default to 'prod' if no argument is provided

# Stop and remove the container if it already exists
docker rm -f my-source-runner 2>/dev/null || true

echo "Starting application in $ENVIRONMENT mode..."

# Run the Docker container
docker run -d --rm --name "$CONTAINER_NAME" \
-v "$(pwd)/$LOG_DIR:/app/$LOG_DIR" \
-v "$(pwd)/$HISTORY_DIR:/app/$HISTORY_DIR" \
-v "$(pwd)/$SESSION_DIR:/app/$SESSION_DIR" \
-v "$(pwd)/$CONFIG_FILE:/app/$CONFIG_FILE:ro" \
-v /etc/localtime:/etc/localtime:ro \
--env APP_ENVIRONMENT="$ENVIRONMENT" \
--network="host" \
"$DOCKER_IMAGE_NAME" "$ENVIRONMENT"
