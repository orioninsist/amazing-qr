# Use a specific version of Python for stability
FROM python:3.10-slim

# Set environment variables to ensure Python output is sent straight to terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for Pillow and other libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Install the package itself
RUN pip install .

# Create a directory for outputs
RUN mkdir -p /app/output

# Set the default command to show help
ENTRYPOINT ["amzqr"]
CMD ["--help"]
