#!/usr/bin/env bash
# Run this ON THE PI (via SSH) to pull the latest code and restart the service.
set -euo pipefail

REPO_DIR="/home/pi/Raspberry"
SERVICE="slot-monitor"

cd "$REPO_DIR"
git pull
source .venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart "$SERVICE"
sudo systemctl status "$SERVICE" --no-pager
