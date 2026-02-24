#!/bin/bash
# Get the absolute path of the directory containing this script
DIR="$(cd "$(dirname "$0")" && pwd)"
# Resolve the project root (two levels up from scripts/kms/)
PROJECT_ROOT="$(cd "$DIR/../.." && pwd)"

# Ensure history directory exists for mounting
mkdir -p "$PROJECT_ROOT/history/kms"

# Dynamically read port from config.json
KMS_PORT=$(python3 -c "
import json, os
try:
    with open('$PROJECT_ROOT/config.json', 'r') as f:
        data = json.load(f)
        kms_config = data.get('kms')
        if isinstance(kms_config, dict):
            print(kms_config.get('port', 4001))
        else:
            print(4001)
except:
    print(4001)
")

echo "Starting KMS Docker container on port $KMS_PORT..."
docker run -d \
  --name my-kms-server \
  -p "$KMS_PORT:$KMS_PORT" \
  -e "KMS_PORT=$KMS_PORT" \
  -v "$PROJECT_ROOT/config.json:/app/config.json:ro" \
  -v "$PROJECT_ROOT/history/kms:/app/history" \
  --restart unless-stopped \
  my-kms

echo "KMS is running. Check logs with: docker logs -f my-kms-server"
