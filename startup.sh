#!/bin/bash

echo "--- Starting startup.sh on $(date) ---"
echo "Current directory: $(pwd)"
echo "Listing files in current directory:"
ls -la

echo "Installing Python dependencies from requirements.txt..."
# Use 'pip3 explicitly for Python 3 environments for clarity
# Add -v for verbose output to see what pip is doing
# Use --no-cache-dir to prevent issues with cached packages if they get corrupted
pip install -r requirements.txt --no-cache-dir

# Check if pip install failed and exit if it did
if [ $? -ne 0 ]; then
    echo "ERROR: pip install failed. Check logs above for details."
    exit 1
fi
echo "Python dependencies installed successfully."

echo "Verifying 'requests' installation:"
pip freeze | grep requests
if [ $? -ne 0 ]; then
    echo "ERROR: 'requests' module not found after installation attempt!"
    exit 1
else
    echo "'requests' module verified."
fi

echo "Starting Gunicorn..."
# Ensure 'app:app' correctly points to your Flask app object (e.g., myapp:app if in myapp.py)
gunicorn --bind 0.0.0.0:${WEBSITES_PORT:-8000} app:app

echo "Gunicorn command issued. Check Gunicorn's own logs for further app startup."