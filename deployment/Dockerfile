FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create necessary directories
RUN mkdir -p config examples evaluation_results

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV HEALTH_CHECK_PORT=8081
ENV GENERATE_SAMPLE_DATA=true

# Make scripts executable
RUN chmod +x start-service.sh

# OpenShift runs containers as a random user, so we need to make directories writable
RUN chmod -R 777 /app

# Expose ports for Streamlit and health check
EXPOSE 8080 8081

# Command to run the startup script
CMD ["./start-service.sh"]