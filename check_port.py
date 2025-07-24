#!/usr/bin/env python3
"""
Port Checker for TMS Web Dashboard
Check if port 5000 is available and suggest alternatives
"""

import socket
import subprocess
import sys
import os

def check_port(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=5000, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if check_port(port):
            return port
    return None

def get_process_using_port(port):
    """Get process information using a specific port"""
    try:
        # For Linux/Mac
        result = subprocess.run(['lsof', '-i', f':{port}'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # Skip header
                return lines[1]  # Return first process using the port
    except FileNotFoundError:
        try:
            # For Windows
            result = subprocess.run(['netstat', '-ano'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        return line
        except FileNotFoundError:
            pass
    return None

def main():
    print("🔍 TMS Web Dashboard Port Checker")
    print("=" * 40)
    
    # Check port 5000
    port_5000_available = check_port(5000)
    
    if port_5000_available:
        print("✅ Port 5000 is AVAILABLE")
        print("   You can use the default configuration")
    else:
        print("❌ Port 5000 is NOT AVAILABLE")
        
        # Check what's using port 5000
        process_info = get_process_using_port(5000)
        if process_info:
            print(f"   Process using port 5000: {process_info}")
        
        # Find alternative port
        print("\n🔍 Looking for alternative ports...")
        alt_port = find_available_port(5001, 20)
        
        if alt_port:
            print(f"✅ Found available port: {alt_port}")
            print(f"   You can use: WEB_PORT={alt_port}")
        else:
            print("❌ No available ports found in range 5001-5020")
            print("   Please check your system or use a different port range")
    
    # Show current configuration
    print("\n📋 Current Configuration:")
    web_host = os.getenv('WEB_HOST', '0.0.0.0')
    web_port = os.getenv('WEB_PORT', '5000')
    print(f"   WEB_HOST: {web_host}")
    print(f"   WEB_PORT: {web_port}")
    
    # Show usage instructions
    print("\n🚀 Usage Instructions:")
    print("1. If port 5000 is available:")
    print("   python3 web_dashboard.py")
    print("   # or")
    print("   ./start_dashboard.sh")
    
    if not port_5000_available and alt_port:
        print(f"\n2. If using alternative port {alt_port}:")
        print(f"   WEB_PORT={alt_port} python3 web_dashboard.py")
        print(f"   # or")
        print(f"   export WEB_PORT={alt_port}")
        print(f"   python3 web_dashboard.py")
    
    print("\n3. For production (systemd service):")
    print("   sudo cp tms-dashboard.service /etc/systemd/system/")
    print("   sudo systemctl enable tms-dashboard")
    print("   sudo systemctl start tms-dashboard")
    
    # Show all ports in range
    print("\n📊 Port Status (5000-5020):")
    for port in range(5000, 5021):
        status = "✅ AVAILABLE" if check_port(port) else "❌ IN USE"
        print(f"   Port {port}: {status}")

if __name__ == "__main__":
    main() 