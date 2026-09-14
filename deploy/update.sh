#!/usr/bin/env bash
# Run this ON THE PI (via SSH) to pull the latest code and restart the service.
set -euo pipefail

REPO_DIR="/home/rasp/RepairSensor"
SERVICE="slot-monitor"

cd "$REPO_DIR"
git pull
sudo systemctl restart "$SERVICE"
sudo systemctl status "$SERVICE" --no-pager
