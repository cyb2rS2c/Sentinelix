#!/bin/bash
set -e

REPO_PATH="$(cd "$(dirname "$0")" && pwd)"
SERVICE_FILE="user-monitor.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_FILE"

# Must be root
if [ "$EUID" -ne 0 ]; then
  echo "Run this script as root"
  exit 1
fi

cp "$SERVICE_FILE" "$SYSTEMD_PATH"

systemctl daemon-reload
systemctl enable user-monitor.service
systemctl restart user-monitor.service

systemctl status user-monitor.service
