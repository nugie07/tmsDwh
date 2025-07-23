# Create Tables Program Documentation

Program ini dibuat khusus untuk membuat tabel di Database B berdasarkan query dari program `fact_order` dan `fact_delivery`.

## Fitur Utama

### 1. **Struktur Tabel Lengkap**
- ✅ Semua kolom dari query fact_order dan fact_delivery
- ✅ Kolom `last_synced` untuk tracking sinkronisasi
- ✅ Kolom `created_at` dan `updated_at` untuk audit trail
- ✅ Primary key dan composite primary key yang sesuai
- ✅ Indexes untuk performa optimal
- ✅ Triggers untuk auto-update `updated_at`

### 2. **Fleksibilitas Pembuatan Tabel**
- ✅ Membuat semua tabel sekaligus
- ✅ Membuat tabel tertentu saja
- ✅ Force recreate (drop dan create ulang)
- ✅ Skip jika tabel sudah ada

### 3. **Monitoring dan Validasi**
- ✅ Program untuk melihat struktur tabel
- ✅ List semua tabel yang ada
- ✅ Validasi keberadaan tabel

## Struktur Tabel yang Dibuat

### Tabel `tms_fact_order`

```sql
CREATE TABLE tms_fact_order (
    -- Columns from the fact_order query
    status VARCHAR(50),
    manifest_reference VARCHAR(100),
    order_id VARCHAR(50),
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
    
    -- Additional tracking columns
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Primary key
    PRIMARY KEY (order_id)
);
```

**Indexes:**
- `idx_tms_fact_order_faktur_date` - untuk query berdasarkan tanggal faktur
- `idx_tms_fact_order_route_id` - untuk query berdasarkan route
- `idx_tms_fact_order_last_synced` - untuk tracking sinkronisasi

### Tabel `tms_fact_delivery`

```sql
CREATE TABLE tms_fact_delivery (
    -- Columns from the fact_delivery query
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
    
    -- Additional tracking columns
    last_synced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Composite primary key
    PRIMARY KEY (route_id, route_detail_id, order_id)
);
```

**Indexes:**
- `idx_tms_fact_delivery_route_id` - untuk query berdasarkan route
- `idx_tms_fact_delivery_order_id` - untuk query berdasarkan order
- `idx_tms_fact_delivery_faktur_date` - untuk query berdasarkan tanggal faktur
- `idx_tms_fact_delivery_delivery_date` - untuk query berdasarkan tanggal delivery
- `idx_tms_fact_delivery_last_synced` - untuk tracking sinkronisasi
- `idx_tms_fact_delivery_driver_id` - untuk query berdasarkan driver
- `idx_tms_fact_delivery_vehicle_id` - untuk query berdasarkan vehicle

### Tabel `tms_sync_log`

```sql
CREATE TABLE tms_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) NOT NULL,
    records_processed INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_tms_sync_log_sync_type` - untuk query berdasarkan tipe sinkronisasi
- `idx_tms_sync_log_start_time` - untuk query berdasarkan waktu mulai
- `idx_tms_sync_log_status` - untuk query berdasarkan status

## Cara Penggunaan

### 1. **Menggunakan Command Line**

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

### 2. **Melihat Struktur Tabel**

#### List semua tabel
```bash
python3 show_table_structure.py --list
```

#### Lihat struktur tabel tertentu
```bash
python3 show_table_structure.py --table fact_order
```

### 3. **Menggunakan Script Interaktif**
```bash
./create_tables.sh
```

Script ini akan memberikan menu interaktif dengan pilihan:
1. Create all tables
2. Create fact_order table only
3. Create fact_delivery table only
4. Create sync_log table only
5. Force recreate all tables
6. Show table structure
7. List all tables

## Fitur Tambahan

### 1. **Auto-update Triggers**
Setiap tabel memiliki trigger yang otomatis mengupdate kolom `updated_at` saat ada perubahan data.

### 2. **Timezone Support**
Semua kolom timestamp menggunakan `TIMESTAMP WITH TIME ZONE` untuk mendukung multiple timezone.

### 3. **Data Type Optimization**
- `VARCHAR` dengan length yang sesuai untuk menghemat storage
- `NUMERIC(15,2)` untuk nilai uang dengan presisi 2 desimal
- `TEXT` untuk field yang mungkin panjang (address)

### 4. **Performance Indexes**
Indexes dibuat untuk kolom-kolom yang sering digunakan dalam query:
- Primary key columns
- Foreign key columns
- Date columns untuk filtering
- Tracking columns untuk monitoring

## Troubleshooting

### 1. **Table Already Exists**
Jika tabel sudah ada, program akan skip pembuatan tabel tersebut. Gunakan `--force` untuk drop dan recreate.

### 2. **Permission Issues**
Pastikan user database memiliki permission untuk:
- CREATE TABLE
- CREATE INDEX
- CREATE TRIGGER
- DROP TABLE (jika menggunakan --force)

### 3. **Connection Issues**
Pastikan konfigurasi di `config.env` sudah benar dan Database B dapat diakses.

## Best Practices

### 1. **Backup Database**
Selalu backup database sebelum menjalankan `--force` option.

### 2. **Test di Development**
Test pembuatan tabel di environment development terlebih dahulu.

### 3. **Monitor Storage**
Indexes akan menambah storage usage, monitor space disk secara berkala.

### 4. **Regular Maintenance**
Jalankan `VACUUM` dan `ANALYZE` secara berkala untuk optimalisasi performa. 