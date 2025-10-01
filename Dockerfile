# Dockerfile for Bravo Sensor Viewer v2.0.0
# Multi-stage build for optimized container size

# Build stage
FROM python:3.11-slim as builder

LABEL maintainer="Pierre Rouaze"
LABEL version="2.0.0"
LABEL description="Bravo Sensor Viewer - Professional Force Calibration Tool"

# Install system dependencies needed for building
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    libhidapi-dev \
    libusb-1.0-0-dev \
    libudev-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage  
FROM python:3.11-slim

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    # GUI and display
    qt5-default \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5core5a \
    # USB/HID device access
    libhidapi-hidraw0 \
    libhidapi-libusb0 \
    libusb-1.0-0 \
    udev \
    # X11 forwarding for GUI
    xauth \
    x11-apps \
    # Utilities
    usbutils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create application user (non-root for security)
RUN groupadd -r sensorapp && \
    useradd -r -g sensorapp -G plugdev sensorapp

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=sensorapp:sensorapp . .

# Create directories for logs and config
RUN mkdir -p /app/logs /app/config && \
    chown -R sensorapp:sensorapp /app

# USB device access rules
RUN echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="046d", MODE="0666", GROUP="plugdev"' > /etc/udev/rules.d/99-hidraw-permissions.rules && \
    echo 'SUBSYSTEM=="hidraw", ATTRS{idVendor}=="046d", MODE="0666", GROUP="plugdev"' >> /etc/udev/rules.d/99-hidraw-permissions.rules

# Environment variables
ENV PYTHONPATH="/app:/app/Vibration_test_scripts/pyhidpp"
ENV QT_X11_NO_MITSHM=1
ENV DISPLAY=:0
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER sensorapp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command - can be overridden
CMD ["python", "bravo_sensor_viewer.py"]