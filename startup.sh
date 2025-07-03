#!/bin/bash

echo "--- Starting startup.sh ---"
echo "Installing Python dependencies..."
# This command is crucial. Use 'pip3' for explicit Python 3 if needed.
pip install -r requirements.txt
# If the above line fails, the script will continue. Add error checking:
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies."
    exit 1 # Exit with an error code
fi
echo "Dependencies installed successfully."

echo "Starting Gunicorn..."
# Ensure 'app:app' correctly points to your Flask app object
gunicorn --bind 0.0.0.0:${WEBSITES_PORT:-8000} app:app
echo "Gunicorn command executed."