# Base Image with generic CUDA support (adjust version as needed)
FROM python:3.10-slim

# Install system dependencies for OpenCV and builds
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Requirements
COPY requirements.txt .

# Install Python Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Application Code
COPY . .

# Expose ports (FastAPI: 8000, Streamlit: 8501)
EXPOSE 8000
EXPOSE 8501

# Default command (overridden by docker-compose)
CMD ["bash"]
