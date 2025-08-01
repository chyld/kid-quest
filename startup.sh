#!/bin/bash

# Kid Quest Application Startup Script
# Starts backend and frontend services in the background

set -e

# Get the absolute path of the script's directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start backend service
cd "$SCRIPT_DIR/backend"
./start.sh &

# Start frontend service  
cd "$SCRIPT_DIR/frontend"
npm run dev &

# Wait for services to start, then turn networking off
sleep 10
curl -X POST http://localhost:8000/networking -H "Content-Type: application/json" -d '{"state": "off"}' &

# Services started - run in background
exit 0
