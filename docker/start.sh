#!/bin/bash

# It's good practice to ensure the script exits on error
set -e

echo "Starting Genesis Core V2 API Server..."
uvicorn api.server:app --host 0.0.0.0 --port 8000
