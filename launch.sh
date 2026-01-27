#!/bin/bash
echo "🚨 THE PANIC ENGINE 🚨"
echo "Cleaning up ports..."
./cleanup-ports.sh
echo "Starting server..."
python3 server.py &
sleep 2
echo "Opening browser..."
open http://localhost:5001
echo "Server running! Press Ctrl+C to stop."
