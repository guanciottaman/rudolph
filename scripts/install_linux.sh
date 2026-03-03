#!/bin/bash
set -e

# Python compatibile
PYTHON=$(command -v python3)
$PYTHON -m venv ./venv
source ./venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

# Systemd user service
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/rudolph.service <<EOL
[Unit]
Description=Rudolph App in background
After=network.target

[Service]
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=5
WorkingDirectory=$(pwd)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOL

systemctl --user daemon-reload
systemctl --user enable rudolph.service
systemctl --user start rudolph.service

echo "Rudolph installed and running!"