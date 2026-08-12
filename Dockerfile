# Dockerfile for Hugging Face Docker Space (Free CPU Tier)
FROM python:3.10-slim

WORKDIR /app

# Install system libraries for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Hugging Face exposes port 7860
EXPOSE 7860

# Run Flask API server in simulation mode on port 7860
CMD ["python", "dashboard_api.py", "--simulate", "--port", "7860", "--host", "0.0.0.0"]
