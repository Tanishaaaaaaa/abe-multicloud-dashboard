# Use Ubuntu as base image
FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including mpfr-dev and libmpc-dev
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    libgmp-dev \
    libmpfr-dev \  
    libmpc-dev \  
    wget \
    git \
    flex \
    bison \
    curl \
    libssl-dev \
    cmake \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install PBC from source
RUN wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz && \
    tar -xvzf pbc-0.5.14.tar.gz && \
    cd pbc-0.5.14 && \
    ./configure && \
    make && \
    make install && \
    ldconfig && \
    cd .. && rm -rf pbc-0.5.14*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p uploads decrypted abe/keys

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python3", "app.py"]
