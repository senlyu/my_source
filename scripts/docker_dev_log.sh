#!/bin/bash
cd "$(dirname "$0")/.."
docker logs -f my-source-runner > ./dev.log 2>&1
