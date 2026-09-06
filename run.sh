#!/bin/bash

cd "$(dirname "$0")"

echo "Stopping old server..."
pkill -f "http.server 8000" 2>/dev/null || true

echo "Building game..."
rm -rf build
pygbag --build .

echo "Starting game server..."
cd build/web
python -m http.server 8000