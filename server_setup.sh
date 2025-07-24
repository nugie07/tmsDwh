#!/bin/bash

# Quick Server Setup for TMS Web Dashboard
# Run this script on your server for quick deployment

set -e

echo "🚀 TMS Web Dashboard - Quick Server Setup"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
print_status "Server IP: $SERVER_IP"

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
print_status "Installing dependencies..."
apt install -y python3 python3-pip python3-venv git curl wget nginx

# Clone repository
if [ ! -d "/home/tmsDwh" ]; then
    print_status "Cloning repository..."
    cd /home
    git clone https://github.com/nugie07/tmsDwh.git
    cd tmsDwh
else
    print_status "Repository already exists, updating..."
    cd /home/tmsDwh
    git pull origin main
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    print_warning "config.env not found!"
    print_status "Creating config.env template..."
    cat > config.env << EOF
# Database A (Source) Configuration
DB_A_HOST=your-db-host
DB_A_PORT=5432
DB_A_NAME=your-db-name
DB_A_USER=your-db-user
DB_A_PASSWORD=your-db-password

# Database B (Target) Configuration
DB_B_HOST=your-db-host
DB_B_PORT=5432
DB_B_NAME=your-db-name
DB_B_USER=your-db-user
DB_B_PASSWORD=your-db-password

# Application Configuration
LOG_LEVEL=INFO
BATCH_SIZE=1000

# Web Dashboard Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000
EOF
    
    print_warning "Please edit config.env with your database credentials:"
    print_status "nano config.env"
    read -p "Press Enter after editing config.env..."
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check port availability
print_status "Checking port availability..."
python3 check_port.py

# Ask for port
read -p "Enter port for web dashboard (default: 5000): " WEB_PORT
WEB_PORT=${WEB_PORT:-5000}

# Create systemd service
print_status "Creating systemd service..."
cat > /etc/systemd/system/tms-dashboard.service << EOF
[Unit]
Description=TMS Data Warehouse Web Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/tmsDwh
Environment=PATH=/usr/bin:/usr/local/bin
Environment=WEB_HOST=0.0.0.0
Environment=WEB_PORT=$WEB_PORT
ExecStart=/usr/bin/python3 /home/tmsDwh/web_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable and start service
print_status "Starting dashboard service..."
systemctl enable tms-dashboard
systemctl start tms-dashboard

# Setup firewall
print_status "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow $WEB_PORT/tcp
ufw status

# Create nginx config
print_status "Setting up nginx reverse proxy..."
cat > /etc/nginx/sites-available/tms-dashboard << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:$WEB_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/tms-dashboard /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# Create monitoring scripts
print_status "Creating monitoring scripts..."
cat > /home/tmsDwh/monitor_dashboard.sh << 'EOF'
#!/bin/bash
echo "=== TMS Dashboard Status ==="
echo "Service Status:"
systemctl is-active tms-dashboard

echo -e "\nRecent Logs:"
journalctl -u tms-dashboard --no-pager -n 10

echo -e "\nPort Status:"
netstat -tlnp | grep :5000 || echo "Port 5000 not found"

echo -e "\nProcess Status:"
ps aux | grep web_dashboard | grep -v grep || echo "No web_dashboard process found"
EOF

chmod +x /home/tmsDwh/monitor_dashboard.sh

cat > /home/tmsDwh/restart_dashboard.sh << 'EOF'
#!/bin/bash
echo "Restarting TMS Dashboard..."
systemctl restart tms-dashboard
sleep 3
echo "Status after restart:"
systemctl status tms-dashboard --no-pager
EOF

chmod +x /home/tmsDwh/restart_dashboard.sh

# Test dashboard
print_status "Testing dashboard..."
sleep 5
if curl -s http://localhost:$WEB_PORT/api/status > /dev/null; then
    print_status "✅ Dashboard is running successfully!"
else
    print_warning "⚠️  Dashboard might not be ready yet. Check logs:"
    journalctl -u tms-dashboard -n 10
fi

# Final instructions
echo ""
print_status "🎉 Setup Complete!"
echo ""
print_status "Dashboard URLs:"
echo "  Local: http://localhost:$WEB_PORT"
echo "  Server: http://$SERVER_IP:$WEB_PORT"
echo "  Nginx: http://$SERVER_IP"
echo ""
print_status "Useful Commands:"
echo "  Check status: systemctl status tms-dashboard"
echo "  View logs: journalctl -u tms-dashboard -f"
echo "  Restart: systemctl restart tms-dashboard"
echo "  Monitor: /home/tmsDwh/monitor_dashboard.sh"
echo ""
print_warning "Next Steps:"
echo "  1. Configure domain (optional)"
echo "  2. Setup SSL certificate (optional)"
echo "  3. Add authentication (optional)"
echo "  4. Monitor logs regularly"
echo ""
print_status "Dashboard will auto-start on boot!" 