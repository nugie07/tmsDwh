# 🚀 TMS Web Dashboard - Server Deployment Guide

## Overview
Panduan lengkap untuk deploy TMS Web Dashboard ke server production agar bisa run terus dan diakses via domain.

## Prerequisites
- Server Linux (Ubuntu/CentOS/Debian)
- Python 3.7+
- Git
- Root access atau sudo privileges

## Step 1: Server Setup

### 1.1 Connect ke Server
```bash
ssh root@your-server-ip
# atau
ssh your-username@your-server-ip
```

### 1.2 Update System
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 1.3 Install Dependencies
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv git curl wget

# CentOS/RHEL
sudo yum install -y python3 python3-pip git curl wget
```

## Step 2: Clone Repository

### 2.1 Clone dari GitHub
```bash
cd /home
git clone https://github.com/nugie07/tmsDwh.git
cd tmsDwh
```

### 2.2 Setup Environment
```bash
# Copy config template
cp config.env.example config.env

# Edit config dengan credentials server
nano config.env
```

## Step 3: Check Port Availability

### 3.1 Run Port Checker
```bash
python3 check_port.py
```

### 3.2 Jika Port 5000 Terpakai
```bash
# Cek apa yang menggunakan port 5000
sudo lsof -i :5000
# atau
sudo netstat -tlnp | grep :5000

# Kill process jika perlu
sudo kill -9 <PID>
```

## Step 4: Production Deployment

### 4.1 Method 1: Auto Deployment Script (Recommended)
```bash
# Make script executable
chmod +x deploy_dashboard.sh

# Run deployment script
sudo ./deploy_dashboard.sh
```

### 4.2 Method 2: Manual Setup
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# Create systemd service
sudo cp tms-dashboard.service /etc/systemd/system/

# Edit service file dengan port yang benar
sudo nano /etc/systemd/system/tms-dashboard.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable tms-dashboard
sudo systemctl start tms-dashboard
```

## Step 5: Firewall Configuration

### 5.1 UFW (Ubuntu)
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow web dashboard port
sudo ufw allow 5000/tcp

# Check status
sudo ufw status
```

### 5.2 iptables (CentOS)
```bash
# Allow port 5000
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT

# Save rules
sudo service iptables save
```

## Step 6: Domain Setup (Optional)

### 6.1 Nginx Reverse Proxy
```bash
# Install nginx
sudo apt install nginx

# Create nginx config
sudo nano /etc/nginx/sites-available/tms-dashboard
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tms-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6.2 SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 7: Monitoring & Maintenance

### 7.1 Check Service Status
```bash
# Service status
sudo systemctl status tms-dashboard

# View logs
sudo journalctl -u tms-dashboard -f

# Check if running
curl http://localhost:5000/api/status
```

### 7.2 Monitoring Scripts
```bash
# Monitor dashboard
./monitor_dashboard.sh

# Restart dashboard
./restart_dashboard.sh
```

### 7.3 Auto-restart on Failure
```bash
# Edit service file
sudo nano /etc/systemd/system/tms-dashboard.service

# Add these lines under [Service]:
Restart=always
RestartSec=10
```

## Step 8: Security Hardening

### 8.1 Change Default Port
```bash
# Edit config.env
WEB_PORT=8080

# Update nginx config
proxy_pass http://127.0.0.1:8080;
```

### 8.2 Basic Authentication
```bash
# Install apache2-utils
sudo apt install apache2-utils

# Create password file
sudo htpasswd -c /etc/nginx/.htpasswd admin

# Add to nginx config
location / {
    auth_basic "Restricted Access";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:5000;
}
```

### 8.3 IP Whitelist
```bash
# Add to nginx config
allow 192.168.1.0/24;
allow 10.0.0.0/8;
deny all;
```

## Step 9: Backup & Recovery

### 9.1 Backup Configuration
```bash
# Create backup directory
mkdir -p /backup/tms-dashboard

# Backup important files
cp config.env /backup/tms-dashboard/
cp tms-dashboard.service /backup/tms-dashboard/
cp -r /etc/nginx/sites-available/tms-dashboard /backup/tms-dashboard/
```

### 9.2 Recovery Script
```bash
#!/bin/bash
# recovery.sh
echo "Restoring TMS Dashboard..."

# Stop service
sudo systemctl stop tms-dashboard

# Restore files
cp /backup/tms-dashboard/config.env .
cp /backup/tms-dashboard/tms-dashboard.service /etc/systemd/system/

# Reload and start
sudo systemctl daemon-reload
sudo systemctl start tms-dashboard

echo "Recovery complete!"
```

## Step 10: Troubleshooting

### 10.1 Common Issues

#### Dashboard tidak bisa diakses
```bash
# Check service
sudo systemctl status tms-dashboard

# Check port
sudo netstat -tlnp | grep :5000

# Check firewall
sudo ufw status

# Check logs
sudo journalctl -u tms-dashboard -n 50
```

#### Database Connection Error
```bash
# Test connection
python3 test_connection.py

# Check config
cat config.env

# Check network
ping database-server-ip
```

#### Permission Issues
```bash
# Fix permissions
sudo chown -R root:root /home/tmsDwh
sudo chmod -R 755 /home/tmsDwh
```

### 10.2 Performance Issues
```bash
# Check memory usage
free -h

# Check CPU usage
top

# Check disk space
df -h

# Check process
ps aux | grep web_dashboard
```

## Step 11: Updates & Maintenance

### 11.1 Update Code
```bash
# Pull latest changes
git pull origin main

# Restart service
sudo systemctl restart tms-dashboard
```

### 11.2 Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/tms-dashboard

# Add:
/var/log/tms-dashboard/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
```

## Quick Commands Reference

```bash
# Start dashboard
sudo systemctl start tms-dashboard

# Stop dashboard
sudo systemctl stop tms-dashboard

# Restart dashboard
sudo systemctl restart tms-dashboard

# Check status
sudo systemctl status tms-dashboard

# View logs
sudo journalctl -u tms-dashboard -f

# Check port
sudo netstat -tlnp | grep :5000

# Monitor
./monitor_dashboard.sh

# Update
git pull && sudo systemctl restart tms-dashboard
```

## Access URLs

- **Local**: http://localhost:5000
- **Server IP**: http://your-server-ip:5000
- **Domain**: http://your-domain.com (if configured)

## Support

Jika ada masalah:
1. Check logs: `sudo journalctl -u tms-dashboard -f`
2. Check status: `sudo systemctl status tms-dashboard`
3. Test connection: `python3 test_connection.py`
4. Monitor: `./monitor_dashboard.sh` 