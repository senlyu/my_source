#!/bin/bash
echo "Stopping and removing KMS container..."
docker stop my-kms-server && docker rm my-kms-server
