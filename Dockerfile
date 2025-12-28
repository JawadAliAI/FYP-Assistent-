FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    wget \
    git \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Piper TTS binary
RUN wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    && tar -xzf piper_amd64.tar.gz \
    && mv piper/piper /usr/local/bin/ \
    && chmod +x /usr/local/bin/piper \
    && rm -rf piper piper_amd64.tar.gz

# Download Piper voice model (en_US-lessac-medium)
RUN mkdir -p /app/models \
    && wget -q -O /app/models/en_US-lessac-medium.onnx \
    https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx \
    && wget -q -O /app/models/en_US-lessac-medium.onnx.json \
    https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY .env.example .

# Set environment variables for Piper
ENV PIPER_EXECUTABLE=/usr/local/bin/piper
ENV PIPER_MODEL_PATH=/app/models/en_US-lessac-medium.onnx

# Expose port
EXPOSE 10000

# Run the application
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-10000}
