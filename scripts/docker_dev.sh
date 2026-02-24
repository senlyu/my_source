#!/bin/bash

# Ensure we are in the project root
cd "$(dirname "$0")/.."

# Define image and container names
DOCKER_IMAGE_NAME="mysource-test:latest"
CONTAINER_NAME="mysource-test-runner"
LOG_FILE="dev.log"

# Function to build the test Docker image
build() {
    echo "Building $DOCKER_IMAGE_NAME..."
    docker build -t "$DOCKER_IMAGE_NAME" -f app.dockerfile .
}

# Function to run the test container
run() {
    # Get the environment argument (e.g., dev, dev_listener, dev_reporter)
    ENVIRONMENT=${1:-dev}

    # Configuration and state directories
    LOG_DIR="log"
    HISTORY_DIR="history"
    SESSION_DIR="session"
    CONFIG_FILE="config.json"

    # Check if config.json exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Warning: $CONFIG_FILE not found. Using config.example.json for development..."
        if [ -f "config.example.json" ]; then
            cp config.example.json "$CONFIG_FILE"
        else
            echo "Error: config.example.json not found."
            exit 1
        fi
    fi

    # Create necessary directories
    mkdir -p "$LOG_DIR" "$HISTORY_DIR" "$SESSION_DIR"

    # Ensure host directories have appropriate permissions for the appuser (UID 1000)
    HOST_UID=$(id -u)
    HOST_GID=$(id -g)
    if [ "$HOST_UID" -ne 0 ]; then
        for dir in "$LOG_DIR" "$HISTORY_DIR" "$SESSION_DIR"; do
            if [ -d "$dir" ] && [ "$(stat -c %u "$dir")" != "$HOST_UID" ]; then
                chown -R "$HOST_UID":"$HOST_GID" "$dir"
            fi
        done
    fi

    # Stop and remove existing test container
    kill_container

    # Ensure image exists
    if [ -z "$(docker images -q "$DOCKER_IMAGE_NAME" 2> /dev/null)" ]; then
        echo "Image $DOCKER_IMAGE_NAME not found. Building it first..."
        build
    fi

    echo "Starting $CONTAINER_NAME in $ENVIRONMENT mode..."

    # Run the Docker container
    docker run -d --name "$CONTAINER_NAME" \
    -v "$(pwd)/$LOG_DIR:/app/$LOG_DIR" \
    -v "$(pwd)/$HISTORY_DIR:/app/$HISTORY_DIR" \
    -v "$(pwd)/$SESSION_DIR:/app/$SESSION_DIR" \
    -v "$(pwd)/$CONFIG_FILE:/app/$CONFIG_FILE:ro" \
    -v /etc/localtime:/etc/localtime:ro \
    --env APP_ENVIRONMENT="$ENVIRONMENT" \
    --network="host" \
    "$DOCKER_IMAGE_NAME" "$ENVIRONMENT"

    # Check if container started successfully
    if [ $? -ne 0 ]; then
        echo "Error: Failed to start container $CONTAINER_NAME."
        exit 1
    fi

    # Clear old dev.log and start capturing logs from the new container
    echo "Redirecting logs to $LOG_FILE..."
    > "$LOG_FILE"
    docker logs -f "$CONTAINER_NAME" > "$LOG_FILE" 2>&1 &

    echo "Container $CONTAINER_NAME is running."
    echo "Logs are being written to $LOG_FILE. Use 'tail -f $LOG_FILE' to view them."
}

# Function to stop and remove the test container
kill_container() {
    echo "Stopping and removing $CONTAINER_NAME..."
    docker rm -f "$CONTAINER_NAME" 2>/dev/null || true
}

# Main script logic
case "$1" in
    build)
        build
        ;;
    run)
        run "$2"
        ;;
    kill)
        kill_container
        ;;
    *)
        echo "Usage: $0 {build|run|kill}"
        exit 1
        ;;
esac
