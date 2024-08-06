#!/bin/bash

# Set the project directories
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
FASTAPI_PORT=8000

# Load environment variables from .env.local
if [ -f .env.local ]; then
  export $(cat .env.local | xargs)
fi

# Create and activate Python virtual environment
echo "Setting up Python environment..."
python3 -m venv $BACKEND_DIR/venv
source $BACKEND_DIR/venv/bin/activate

# Install Python packages from requirements.txt
echo "Installing Python packages from requirements.txt..."
pip install -r $BACKEND_DIR/requirements.txt

# Install React packages
echo "Setting up React environment..."
cd $FRONTEND_DIR
npm install

# Run FastAPI server
echo "Starting FastAPI server..."
cd ../$BACKEND_DIR
uvicorn main:app --host 0.0.0.0 --port $FASTAPI_PORT --reload &

# Run React frontend
echo "Starting React frontend..."
cd ../$FRONTEND_DIR
npm start
