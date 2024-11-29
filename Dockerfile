FROM python:3.10-slim

# Ensure the package index is updated and install system dependencies
WORKDIR /mma-social-network

# Copy project files into the container
COPY . /mma-social-network

# Install system dependencies, including build-essential
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Make startup script executable
RUN chmod +x startup.sh

# Expose the application port
EXPOSE 5000

# Set working directory and run the application
WORKDIR /mma-social-network/src
CMD ["python3", "app.py"]
