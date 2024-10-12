#!/bin/bash

# Find the PID of the running Python application
PID=$(pgrep -f "python app.py")

if [ -n "$PID" ]; then
    echo "Stopping application (PID: $PID)"
    kill $PID
    
    # Wait for up to 10 seconds for the application to stop
    for i in {1..10}; do
        if ! ps -p $PID > /dev/null; then
            echo "Application stopped successfully."
            exit 0
        fi
        sleep 1
    done
    
    # If the application hasn't stopped after 10 seconds, force kill it
    echo "Application did not stop gracefully. Force killing..."
    kill -9 $PID
    
    if ! ps -p $PID > /dev/null; then
        echo "Application forcefully stopped."
    else
        echo "Failed to stop the application. Please check manually."
        exit 1
    fi
else
    echo "No running application found."
fi
