BACKEND_DIR="."
FASTAPI_PORT=8000

source $BACKEND_DIR/venv/bin/activate

# Install Python packages from requirements.txt
echo "Installing Python packages from requirements.txt..."
pip install -r $BACKEND_DIR/requirements.txt

# Find the PID of the process listening on port 8000
pid=$(lsof -i :$FASTAPI_PORT | grep LISTEN | awk '{print $2}')

# If a PID is found, kill the process
if [ -n "$pid" ]; then
  kill $pid
  echo "Process on port 8000 killed."
else
  echo "No process found listening on port 8000."
fi

# Run FastAPI server
echo "Starting FastAPI server..."
cd ../$BACKEND_DIR
uvicorn main:app --host 0.0.0.0 --port $FASTAPI_PORT --reload &