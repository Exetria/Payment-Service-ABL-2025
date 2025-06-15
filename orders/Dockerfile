FROM python:3.10-slim

# ---- Install system dependencies ----
RUN apt-get update && \
    apt-get install --yes netcat-openbsd gcc libffi-dev libssl-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---- Set environment variables ----
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ---- Create and set working directory ----
WORKDIR /var/nameko

# ---- Copy project files ----
COPY . .

# ---- Install Python dependencies ----
RUN pip install --upgrade pip && \
    pip install .

# ---- Make run.sh executable ----
RUN chmod +x run.sh

# ---- Expose the port for the service ----
EXPOSE 8000

# ---- Run the service ----
CMD ["./run.sh"]
