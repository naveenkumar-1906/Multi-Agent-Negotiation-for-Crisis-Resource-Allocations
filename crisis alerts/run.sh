#!/bin/bash

echo "🚀 Starting Crisis Resource Allocation System..."

# Kill existing processes on ports 8000 and 3001
echo "🔄 Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null

# Start backend server
echo "🖥️  Starting backend server..."
cd "/Users/naveenkumar/Desktop/crisis alerts"
source venv/bin/activate
cd backend
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting frontend server..."
cd "/Users/naveenkumar/Desktop/crisis alerts/frontend"
python3 -m http.server 3001 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 2

echo "✅ System started successfully!"
echo "📊 Dashboard: http://localhost:3001"
echo "🔧 Backend API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
