#!/bin/bash

# Update system
sudo apt update
sudo apt install -y python3-pip python3-venv nginx

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Setup Nginx
sudo tee /etc/nginx/sites-available/insurance-bot << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the Nginx site
sudo ln -sf /etc/nginx/sites-available/insurance-bot /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Create a systemd service for the backend
sudo tee /etc/systemd/system/insurance-bot.service << EOF
[Unit]
Description=Insurance Bot Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/gunicorn app:app --workers 4 --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start insurance-bot
sudo systemctl enable insurance-bot

echo "Backend deployment complete!"
