# Data Warehouse TMS Synchronization System

Sistem ini terdiri dari 2 program Python yang melakukan sinkronisasi data dari Database A (source) ke Database B (target) dengan fitur upsert dan tracking last_synced.

## Struktur Program

1. **fact_order.py** - Program untuk sinkronisasi data fact_order
2. **fact_delivery.py** - Program untuk sinkronisasi data fact_delivery  
3. **sync_manager.py** - Program manager untuk menjalankan sinkronisasi
4. **database_utils.py** - Utility untuk koneksi database
5. **create_tables.py** - Program untuk membuat tabel di Database B
6. **show_table_structure.py** - Program untuk melihat struktur tabel
7. **config.env** - File konfigurasi database

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Database

Edit file `config.env` dengan konfigurasi database Anda:

```env
# Database Configuration for Schema A (Source)
DB_A_HOST=localhost
DB_A_PORT=5432
DB_A_NAME=your_database_a
DB_A_USER=your_username_a
DB_A_PASSWORD=your_password_a
DB_A_SCHEMA=public

# Database Configuration for Schema B (Target)
DB_B_HOST=localhost
DB_B_PORT=5432
DB_B_NAME=your_database_b
DB_B_USER=your_username_b
DB_B_PASSWORD=your_password_b
DB_B_SCHEMA=public

# Application Settings
LOG_LEVEL=INFO
BATCH_SIZE=1000
```

## Penggunaan

### 1. Menjalankan Program Individual

#### Fact Order
```bash
python fact_order.py
```

#### Fact Delivery
```bash
python fact_delivery.py
```

### 2. Menggunakan Sync Manager

#### Menjalankan kedua sinkronisasi
```bash
python sync_manager.py --sync-type both
```

#### Menjalankan sinkronisasi tertentu
```bash
# Hanya fact_order
python sync_manager.py --sync-type fact_order

# Hanya fact_delivery
python sync_manager.py --sync-type fact_delivery
```

#### Melihat status sinkronisasi
```bash
# Status semua sinkronisasi
python sync_manager.py --status

# Status sinkronisasi tertentu
python sync_manager.py --status --status-type fact_order

# Status dengan limit tertentu
python sync_manager.py --status --limit 20
```

### 3. Menggunakan Create Tables Program

#### Membuat semua tabel
```bash
python3 create_tables.py --table all
```

#### Membuat tabel tertentu
```bash
# Hanya fact_order
python3 create_tables.py --table fact_order

# Hanya fact_delivery
python3 create_tables.py --table fact_delivery

# Hanya sync_log
python3 create_tables.py --table sync_log
```

#### Force recreate tabel (drop jika sudah ada)
```bash
python3 create_tables.py --table all --force
```

#### Melihat struktur tabel
```bash
# List semua tabel
python3 show_table_structure.py --list

# Lihat struktur tabel tertentu
python3 show_table_structure.py --table fact_order
```

#### Menggunakan script interaktif
```bash
./create_tables.sh
```

## Fitur Utama

### 1. Database Connection Management
- Koneksi database disimpan dalam file `.env`
- Support untuk multiple database (A dan B)
- Error handling untuk koneksi database

### 2. Upsert Functionality
- Menggunakan PostgreSQL `ON CONFLICT` untuk upsert
- Support untuk composite primary key
- Temporary table approach untuk performa optimal

### 3. Last Synced Tracking
- Setiap tabel di Database B memiliki kolom `last_synced`
- Timestamp dengan timezone untuk tracking akurat
- Otomatis diupdate saat sinkronisasi

### 4. Sync Logging
- Tabel `sync_log` untuk tracking history sinkronisasi
- Informasi start time, end time, status, dan error message
- Query untuk melihat status sinkronisasi

### 5. Error Handling
- Comprehensive error handling di semua level
- Logging yang detail untuk debugging
- Graceful failure dengan rollback

## Struktur Tabel Database B

### tms_fact_order
```sql
CREATE TABLE tms_fact_order (
    status VARCHAR(50),
    manifest_reference VARCHAR(100),
    order_id VARCHAR(50) PRIMARY KEY,
    manifest_integration_id VARCHAR(100),
    external_expedition_type VARCHAR(50),
    driver_name VARCHAR(100),
    code VARCHAR(50),
    faktur_date DATE,
    tms_created TIMESTAMP,
    route_created DATE,
    delivery_date DATE,
    route_id VARCHAR(50),
    tms_complete TIMESTAMP,
    location_confirmation DATE,
    faktur_total_quantity NUMERIC(15,2),
    tms_total_quantity NUMERIC(15,2),
    total_return NUMERIC(15,2),
    total_net_value NUMERIC(15,2),
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### tms_fact_delivery
```sql
CREATE TABLE tms_fact_delivery (
    route_id VARCHAR(50),
    manifest_reference VARCHAR(100),
    route_detail_id VARCHAR(50),
    order_id VARCHAR(50),
    do_number VARCHAR(100),
    faktur_date DATE,
    created_date_only DATE,
    waktu TIME,
    delivery_date DATE,
    status VARCHAR(50),
    client_id VARCHAR(50),
    warehouse_id VARCHAR(50),
    origin_name VARCHAR(200),
    origin_city VARCHAR(100),
    customer_id VARCHAR(50),
    code VARCHAR(50),
    name VARCHAR(200),
    address TEXT,
    address_text TEXT,
    external_expedition_type VARCHAR(50),
    vehicle_id VARCHAR(50),
    driver_id VARCHAR(50),
    plate_number VARCHAR(20),
    driver_name VARCHAR(100),
    kenek_id VARCHAR(50),
    kenek_name VARCHAR(100),
    driver_status VARCHAR(50),
    manifest_integration_id VARCHAR(100),
    complete_time TIMESTAMP,
    net_price NUMERIC(15,2),
    quantity_delivery NUMERIC(15,2),
    quantity_faktur NUMERIC(15,2),
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (route_id, route_detail_id, order_id)
);
```

### tms_sync_log
```sql
CREATE TABLE tms_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Monitoring dan Maintenance

### 1. Log Files
Program menggunakan Python logging dengan level yang dapat dikonfigurasi di `config.env`

### 2. Performance Monitoring
- Batch processing untuk data besar
- Temporary table untuk upsert yang efisien
- Connection pooling dengan SQLAlchemy

### 3. Data Integrity
- Primary key constraints untuk mencegah duplikasi
- Upsert logic untuk update data yang sudah ada
- Timestamp tracking untuk audit trail

## Troubleshooting

### 1. Connection Issues
- Periksa konfigurasi di `config.env`
- Pastikan database dapat diakses dari server
- Periksa firewall dan network connectivity

### 2. Permission Issues
- Pastikan user database memiliki permission untuk CREATE, INSERT, UPDATE
- Periksa schema permissions

### 3. Data Issues
- Periksa log untuk error detail
- Gunakan `--status` untuk melihat history sinkronisasi
- Periksa data source di Database A

## Automation

### Cron Job Example
```bash
# Sinkronisasi setiap jam
0 * * * * cd /path/to/project && python sync_manager.py --sync-type both

# Sinkronisasi setiap hari jam 2 pagi
0 2 * * * cd /path/to/project && python sync_manager.py --sync-type both
```

### Systemd Service Example
```ini
[Unit]
Description=TMS Data Sync Service
After=network.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/python3 sync_manager.py --sync-type both
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
``` 