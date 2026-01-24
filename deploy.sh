#!/bin/bash

# Detect the absolute path of this script's directory
REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_PATH="$REPO_PATH/monitor.py"

# Detect the current user running the deploy script
RUN_USER="$(whoami)"

# Define service file
SERVICE_FILE="user-monitor.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_FILE"

# Copy the template service file to /etc/systemd/system
sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"

# Replace placeholders in the service file dynamically
sudo sed -i "s|__REPO_PATH__|$REPO_PATH|g" "$SYSTEMD_PATH"
sudo sed -i "s|__SCRIPT_PATH__|$SCRIPT_PATH|g" "$SYSTEMD_PATH"
sudo sed -i "s|__USER__|$RUN_USER|g" "$SYSTEMD_PATH"

# Reload systemd, enable, and start the service
sudo systemctl daemon-reload
sudo systemctl enable user-monitor.service
sudo systemctl restart user-monitor.service

# Show status
sudo systemctl status user-monitor.service
