#!/bin/bash
cd "$(dirname "$0")/../.."
ENVIRONMENT=$1
echo "Starting application in $ENVIRONMENT mode..."
pipenv run python3 -m src.main "$ENVIRONMENT"
