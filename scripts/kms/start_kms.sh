#!/bin/bash
# Get the absolute path of the directory containing this script
DIR="$(cd "$(dirname "$0")" && pwd)"
# Resolve the project root
PROJECT_ROOT="$(cd "$DIR/../.." && pwd)"

export PYTHONPATH="$PROJECT_ROOT"

# Check if virtual environment exists in project root
VENV_PATH="$PROJECT_ROOT/kms_venv"

if [ -d "$VENV_PATH" ]; then
    echo "Activating virtual environment at $VENV_PATH..."
    . "$VENV_PATH/bin/activate"
else
    echo "Warning: Virtual environment not found at $VENV_PATH. Using system Python."
fi

echo "Starting KMS from $PROJECT_ROOT"

# Dynamically read port from config.json using python
KMS_PORT=${KMS_PORT:-$(python3 -c "
import json, os
try:
    with open('config.json', 'r') as f:
        data = json.load(f)
        kms_config = data.get('kms')
        if isinstance(kms_config, dict):
            print(kms_config.get('port', 4001))
        else:
            print(4001)
except:
    print(4001)
")}

echo "Target port: $KMS_PORT"
uvicorn kms.main:app --reload --port "$KMS_PORT" --host 0.0.0.0
