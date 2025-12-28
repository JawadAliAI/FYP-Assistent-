FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (ffmpeg for audio processing)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY .env.example .

# Expose port
EXPOSE 10000

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}
