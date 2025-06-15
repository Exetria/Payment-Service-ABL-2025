FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install --yes netcat-openbsd gcc libffi-dev libssl-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /var/nameko

# Copy everything into the container
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install .

# Expose the port for the gateway service
EXPOSE 8000

# Make sure run.sh is executable
RUN chmod +x run.sh

# Run the service
CMD ["./run.sh"]
