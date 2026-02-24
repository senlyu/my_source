#!/bin/bash
cd "$(dirname "$0")/../.."
docker build -t my-source:latest -f app.dockerfile .
