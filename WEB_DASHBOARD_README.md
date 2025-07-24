# TMS Data Warehouse Web Dashboard

## Overview
Web dashboard untuk monitoring status sinkronisasi data TMS Data Warehouse secara real-time.

## Features
- 📊 **Real-time Status Monitoring**: Melihat status sinkronisasi terbaru
- 📈 **Sync History**: Riwayat sinkronisasi dengan detail lengkap
- 🔄 **Quick Actions**: Tombol untuk menjalankan sinkronisasi langsung dari web
- ⚡ **Auto-refresh**: Update otomatis setiap 30 detik
- 📱 **Responsive Design**: Tampilan yang responsif untuk desktop dan mobile

## Installation

### 1. Install Dependencies
```bash
pip3 install flask==3.0.0
```

### 2. Setup Environment Variables (Optional)
Tambahkan ke `config.env`:
```bash
# Web Dashboard Configuration
WEB_HOST=0.0.0.0
WEB_PORT=5000
```

## Usage

### Method 1: Manual Start
```bash
# Start dashboard
python3 web_dashboard.py

# Atau menggunakan script
chmod +x start_dashboard.sh
./start_dashboard.sh
```

### Method 2: Systemd Service (Recommended for Production)
```bash
# Copy service file
sudo cp tms-dashboard.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable tms-dashboard
sudo systemctl start tms-dashboard

# Check status
sudo systemctl status tms-dashboard

# View logs
sudo journalctl -u tms-dashboard -f
```

### Method 3: Background Process
```bash
# Start in background
nohup python3 web_dashboard.py > dashboard.log 2>&1 &

# Check if running
ps aux | grep web_dashboard

# Stop process
pkill -f web_dashboard.py
```

## Access Dashboard
Setelah dashboard berjalan, akses melalui browser:
```
http://your-server-ip:5000
```

## Dashboard Features

### 1. Statistics Cards
- **Total Sync Records**: Jumlah total record sinkronisasi
- **Successful Syncs**: Jumlah sinkronisasi yang berhasil
- **Failed Syncs**: Jumlah sinkronisasi yang gagal
- **Last Sync**: Waktu sinkronisasi terakhir

### 2. Quick Actions
- **🔄 Sync Both Tables**: Sinkronisasi kedua table (fact_order + fact_delivery)
- **📋 Sync Fact Order**: Sinkronisasi table fact_order saja
- **🚚 Sync Fact Delivery**: Sinkronisasi table fact_delivery saja
- **📊 Refresh Status**: Refresh status manual
- **📋 Order Status**: Lihat status khusus fact_order
- **🚚 Delivery Status**: Lihat status khusus fact_delivery

### 3. Sync History Table
Menampilkan riwayat sinkronisasi dengan kolom:
- **Sync Type**: Jenis sinkronisasi (both/fact_order/fact_delivery)
- **Start Time**: Waktu mulai sinkronisasi
- **End Time**: Waktu selesai sinkronisasi
- **Status**: Status sinkronisasi (SUCCESS/FAILED/RUNNING)
- **Records**: Jumlah record yang diproses
- **Error**: Pesan error (jika ada)

## API Endpoints

### GET /api/status
Mendapatkan status sinkronisasi dalam format JSON:
```json
{
  "stats": {
    "total_syncs": 15,
    "successful_syncs": 12,
    "failed_syncs": 3,
    "last_sync": "2025-07-24 00:48:32"
  },
  "sync_history": [
    {
      "sync_type": "both",
      "start_time": "2025-07-24 00:46:35",
      "end_time": "2025-07-24 00:48:32",
      "status": "SUCCESS",
      "records_processed": 2583,
      "error_message": null
    }
  ]
}
```

### GET /sync/{sync_type}
Menjalankan sinkronisasi:
- `/sync/both` - Sinkronisasi kedua table
- `/sync/fact_order` - Sinkronisasi fact_order
- `/sync/fact_delivery` - Sinkronisasi fact_delivery

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `WEB_HOST` | `0.0.0.0` | Host untuk web server |
| `WEB_PORT` | `5000` | Port untuk web server |
| `LOG_LEVEL` | `INFO` | Level logging |

### Customization
Untuk mengubah tampilan atau menambah fitur:
1. Edit `HTML_TEMPLATE` di `web_dashboard.py`
2. Tambahkan endpoint baru di bagian bawah file
3. Restart service jika menggunakan systemd

## Troubleshooting

### Dashboard tidak bisa diakses
1. Cek apakah service berjalan:
   ```bash
   sudo systemctl status tms-dashboard
   ```

2. Cek port yang digunakan:
   ```bash
   netstat -tlnp | grep 5000
   ```

3. Cek firewall:
   ```bash
   sudo ufw status
   sudo ufw allow 5000
   ```

### Error "Module not found"
1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Cek Python path:
   ```bash
   which python3
   python3 -c "import flask"
   ```

### Dashboard tidak update
1. Cek log untuk error:
   ```bash
   sudo journalctl -u tms-dashboard -f
   ```

2. Cek koneksi database:
   ```bash
   python3 test_connection.py
   ```

## Security Considerations

### Production Deployment
1. **Use HTTPS**: Setup SSL certificate dengan nginx/apache
2. **Authentication**: Tambahkan login system jika diperlukan
3. **Firewall**: Batasi akses ke IP tertentu
4. **Rate Limiting**: Batasi request per IP

### Example Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring

### Log Files
- **Systemd logs**: `sudo journalctl -u tms-dashboard`
- **Application logs**: Check console output atau log file

### Health Check
```bash
# Check if dashboard is responding
curl http://localhost:5000/api/status

# Check service status
sudo systemctl is-active tms-dashboard
```

## Support
Untuk bantuan atau pertanyaan, silakan hubungi tim development. 