#!/bin/bash

# Production start script for Render deployment

# Use PORT environment variable from Render, default to 8000 for local
PORT=${PORT:-8000}

# Start the application with uvicorn
exec uvicorn app:app --host 0.0.0.0 --port $PORT --workers 1
