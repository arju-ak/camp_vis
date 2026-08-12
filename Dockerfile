# Dockerfile for Hugging Face Spaces (Flask Backend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt-get/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "numpy<2.0.0"

# Copy application files
COPY . .

# Hugging Face Spaces expose port 7860
EXPOSE 7860

# Run Flask backend API in simulation mode on port 7860
CMD ["python", "dashboard_api.py", "--simulate", "--port", "7860"]
