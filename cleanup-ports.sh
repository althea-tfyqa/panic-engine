#!/bin/bash
# Crown Affair - Port Cleanup Script
# Kills lingering Python servers and shows port status

echo "🧹 Cleaning up ports..."

# Kill Python servers
pkill -f "python.*server.py" 2>/dev/null
pkill -f "python.*http.server" 2>/dev/null
pkill -f "python.*oracle_server" 2>/dev/null

sleep 1

echo "✅ Python servers stopped"
echo ""
echo "📊 Current port status (common dev ports):"
lsof -iTCP -sTCP:LISTEN -n -P | grep -E ':(5000|5001|5002|8000|8080|3000)\b' || echo "   All clear! 🎉"
