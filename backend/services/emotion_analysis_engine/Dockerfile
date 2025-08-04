FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for OpenCV and camera access
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY ../../../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy common modules
COPY ../../common /app/common

# Copy service code
COPY . /app/

# Expose port
EXPOSE 8002

# Run the service
CMD ["python", "main.py"]
