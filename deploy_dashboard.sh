#!/bin/bash

# TMS Web Dashboard Production Deployment Script
# This script sets up the web dashboard for production use

set -e  # Exit on any error

echo "🚀 TMS Web Dashboard Production Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    print_error "config.env file not found!"
    echo "Please create config.env with your database configuration."
    exit 1
fi

# Check Python and dependencies
print_header "Checking Python and Dependencies"

if ! command -v python3 &> /dev/null; then
    print_error "Python3 is not installed"
    exit 1
fi

print_status "Python3 found: $(python3 --version)"

# Install/upgrade pip if needed
python3 -m pip --version >/dev/null 2>&1 || {
    print_status "Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py --user
    rm get-pip.py
}

# Install required packages
print_status "Installing Python dependencies..."
pip3 install -r requirements.txt

# Check port availability
print_header "Checking Port Availability"

# Run port checker
python3 check_port.py

# Ask user for port preference
read -p "Enter port number for web dashboard (default: 5000): " WEB_PORT
WEB_PORT=${WEB_PORT:-5000}

# Validate port
if ! python3 -c "import socket; socket.socket().bind(('localhost', $WEB_PORT))" 2>/dev/null; then
    print_warning "Port $WEB_PORT is not available. Checking alternatives..."
    python3 check_port.py
    read -p "Enter available port number: " WEB_PORT
fi

# Create systemd service file with correct port
print_header "Creating Systemd Service"

SERVICE_FILE="/etc/systemd/system/tms-dashboard.service"
CURRENT_DIR=$(pwd)

cat > "$SERVICE_FILE" << EOF
[Unit]
Description=TMS Data Warehouse Web Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
Environment=PATH=/usr/bin:/usr/local/bin
Environment=WEB_HOST=0.0.0.0
Environment=WEB_PORT=$WEB_PORT
ExecStart=/usr/bin/python3 $CURRENT_DIR/web_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_status "Systemd service file created: $SERVICE_FILE"

# Reload systemd
print_status "Reloading systemd..."
systemctl daemon-reload

# Enable and start service
print_status "Enabling and starting tms-dashboard service..."
systemctl enable tms-dashboard
systemctl start tms-dashboard

# Check service status
print_header "Service Status"
systemctl status tms-dashboard --no-pager

# Setup firewall (if ufw is available)
if command -v ufw &> /dev/null; then
    print_header "Configuring Firewall"
    if ufw status | grep -q "Status: active"; then
        print_status "UFW is active. Adding rule for port $WEB_PORT..."
        ufw allow $WEB_PORT/tcp
        print_status "Firewall rule added for port $WEB_PORT"
    else
        print_warning "UFW is not active. Consider enabling it for security."
    fi
else
    print_warning "UFW not found. Please configure firewall manually for port $WEB_PORT"
fi

# Create log directory
LOG_DIR="/var/log/tms-dashboard"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Create monitoring script
print_header "Creating Monitoring Scripts"

cat > "monitor_dashboard.sh" << 'EOF'
#!/bin/bash
# TMS Dashboard Monitoring Script

echo "=== TMS Dashboard Status ==="
echo "Service Status:"
systemctl is-active tms-dashboard

echo -e "\nRecent Logs:"
journalctl -u tms-dashboard --no-pager -n 20

echo -e "\nPort Status:"
netstat -tlnp | grep :5000 || echo "Port 5000 not found"

echo -e "\nProcess Status:"
ps aux | grep web_dashboard | grep -v grep || echo "No web_dashboard process found"
EOF

chmod +x monitor_dashboard.sh

# Create restart script
cat > "restart_dashboard.sh" << 'EOF'
#!/bin/bash
# TMS Dashboard Restart Script

echo "Restarting TMS Dashboard..."
sudo systemctl restart tms-dashboard
sleep 3
echo "Status after restart:"
sudo systemctl status tms-dashboard --no-pager
EOF

chmod +x restart_dashboard.sh

# Final instructions
print_header "Deployment Complete!"
echo ""
print_status "Dashboard is now running on: http://$(hostname -I | awk '{print $1}'):$WEB_PORT"
echo ""
print_status "Useful Commands:"
echo "  Check status:     sudo systemctl status tms-dashboard"
echo "  View logs:        sudo journalctl -u tms-dashboard -f"
echo "  Restart service:  sudo systemctl restart tms-dashboard"
echo "  Stop service:     sudo systemctl stop tms-dashboard"
echo "  Monitor:          ./monitor_dashboard.sh"
echo "  Restart:          ./restart_dashboard.sh"
echo ""
print_status "Dashboard will automatically start on boot"
print_status "Logs are available in systemd journal"
echo ""
print_warning "For security in production:"
echo "  - Consider using HTTPS with nginx/apache"
echo "  - Add authentication if needed"
echo "  - Configure firewall rules"
echo "  - Monitor logs regularly" 