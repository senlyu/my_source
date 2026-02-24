#!/bin/bash
# Get the absolute path of the directory containing this script
DIR="$(cd "$(dirname "$0")" && pwd)"
# Resolve the project root (two levels up from scripts/kms/)
PROJECT_ROOT="$(cd "$DIR/../.." && pwd)"

echo "Building KMS Docker image from $PROJECT_ROOT/kms..."
docker build -t my-kms "$PROJECT_ROOT/kms"
