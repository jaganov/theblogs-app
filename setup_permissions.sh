#!/bin/bash

# Setup script for The Blogs application
echo "Setting up The Blogs application..."

# Create necessary directories
echo "Creating directories..."
mkdir -p media staticfiles logs

# Set proper permissions (assuming UID 1000 for app user)
echo "Setting permissions..."
chmod -R 755 media
chmod -R 755 staticfiles
chmod -R 755 logs

# If running on Linux, set ownership to UID 1000
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Setting ownership on Linux..."
    sudo chown -R 1000:1000 media
    sudo chown -R 1000:1000 staticfiles
    sudo chown -R 1000:1000 logs
fi

echo "Setup complete!"
echo "You can now run: docker compose up -d" 