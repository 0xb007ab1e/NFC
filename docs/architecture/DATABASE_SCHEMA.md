# NFC Reader/Writer System - Database Schema Design

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Database Overview

### Database Engine Selection
- **Primary**: SQLite (Development and simple deployments)
- **Future**: PostgreSQL (Production and multi-user environments)
- **Rationale**: SQLite for simplicity and ease of deployment, PostgreSQL for scalability

### Design Principles
- **Normalization**: 3NF (Third Normal Form) for data integrity
- **Performance**: Indexed columns for frequent queries
- **Scalability**: Designed to support future enhancements
- **Data Integrity**: Foreign keys, constraints, and validation
- **Audit Trail**: Comprehensive logging and tracking

## Core Tables

### 1. devices
**Purpose**: Store registered Android device information

```sql
CREATE TABLE devices (
    id TEXT PRIMARY KEY,                    -- Android device unique identifier
    name TEXT NOT NULL,                     -- Human-readable device name
    model TEXT,                             -- Device model (e.g., "Samsung Galaxy S21")
    android_version TEXT,                   -- Android OS version
    app_version TEXT,                       -- NFC Reader app version
    api_key TEXT UNIQUE NOT NULL,           -- Device-specific API key
    status TEXT DEFAULT 'active',           -- active, inactive, suspended
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_seen DATETIME,                     -- Last heartbeat timestamp
    capabilities TEXT,                      -- JSON: supported NFC types, connections
    settings TEXT,                          -- JSON: device-specific configuration
    metadata TEXT,                          -- JSON: additional device information
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_devices_api_key ON devices(api_key);
CREATE INDEX idx_devices_status ON devices(status);
CREATE INDEX idx_devices_last_seen ON devices(last_seen);
```

### 2. nfc_data
**Purpose**: Store NFC scan data and parsed information

```sql
CREATE TABLE nfc_data (
    id TEXT PRIMARY KEY,                    -- UUID for NFC scan
    device_id TEXT NOT NULL,               -- Reference to devices.id
    server_id INTEGER,                      -- Auto-generated server record ID
    timestamp DATETIME NOT NULL,           -- When scan occurred on device
    received_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- When received by server
    
    -- Tag Information
    tag_type TEXT NOT NULL,                -- NDEF, ISO14443A, etc.
    tag_uid TEXT,                          -- Tag unique identifier (hex)
    tag_technology TEXT,                   -- ISO14443A, MIFARE_CLASSIC, etc.
    max_transceive_length INTEGER,         -- Technical tag limitation
    
    -- Raw Data
    raw_data BLOB,                         -- Base64 decoded raw NFC data
    raw_data_b64 TEXT,                     -- Base64 encoded raw data (for API)
    data_size INTEGER,                     -- Size of raw data in bytes
    checksum TEXT,                         -- MD5 hash for integrity verification
    
    -- Parsed Data
    parsed_data TEXT,                      -- JSON: structured/parsed NFC content
    record_count INTEGER DEFAULT 0,        -- Number of NDEF records
    
    -- Metadata
    read_time_ms INTEGER,                  -- Time taken to read tag
    signal_strength INTEGER,               -- RSSI value if available
    read_attempts INTEGER DEFAULT 1,       -- Number of attempts to read
    location_lat REAL,                     -- GPS latitude
    location_lng REAL,                     -- GPS longitude
    location_accuracy REAL,                -- GPS accuracy in meters
    
    -- Processing Information
    status TEXT DEFAULT 'processed',       -- processed, failed, pending
    error_message TEXT,                    -- Error details if processing failed
    processing_time_ms INTEGER,            -- Server processing time
    
    -- Audit
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_nfc_data_device_id ON nfc_data(device_id);
CREATE INDEX idx_nfc_data_timestamp ON nfc_data(timestamp);
CREATE INDEX idx_nfc_data_received_at ON nfc_data(received_at);
CREATE INDEX idx_nfc_data_tag_type ON nfc_data(tag_type);
CREATE INDEX idx_nfc_data_status ON nfc_data(status);
CREATE INDEX idx_nfc_data_checksum ON nfc_data(checksum);
```

### 3. nfc_records
**Purpose**: Store individual NDEF records from NFC tags (normalized)

```sql
CREATE TABLE nfc_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nfc_data_id TEXT NOT NULL,             -- Reference to nfc_data.id
    record_index INTEGER NOT NULL,         -- Order within the NFC tag
    
    -- NDEF Record Structure
    tnf INTEGER NOT NULL,                  -- Type Name Format (0-7)
    type_name TEXT,                        -- Record type (e.g., "T", "U", "Sp")
    payload BLOB,                          -- Record payload (raw)
    payload_text TEXT,                     -- Human-readable payload if applicable
    payload_b64 TEXT,                      -- Base64 encoded payload
    
    -- Text Record Specific
    language_code TEXT,                    -- Language code for text records
    encoding TEXT DEFAULT 'UTF-8',        -- Text encoding
    
    -- URI Record Specific
    uri_identifier INTEGER,               -- URI identifier prefix (0x00-0x23)
    uri_content TEXT,                     -- Full URI content
    
    -- Metadata
    record_length INTEGER,                -- Size of record in bytes
    is_last_record BOOLEAN DEFAULT FALSE, -- MB (Message Begin) flag
    is_first_record BOOLEAN DEFAULT FALSE, -- ME (Message End) flag
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (nfc_data_id) REFERENCES nfc_data(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_nfc_records_nfc_data_id ON nfc_records(nfc_data_id);
CREATE INDEX idx_nfc_records_type_name ON nfc_records(type_name);
CREATE INDEX idx_nfc_records_tnf ON nfc_records(tnf);
```

### 4. connections
**Purpose**: Track device connection sessions and statistics

```sql
CREATE TABLE connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,               -- Reference to devices.id
    connection_type TEXT NOT NULL,         -- USB, WIFI
    session_id TEXT UNIQUE NOT NULL,       -- UUID for this connection session
    
    -- Connection Details
    established_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    terminated_at DATETIME,
    duration_seconds INTEGER,              -- Calculated when terminated
    
    -- Network Information (for WIFI connections)
    server_ip TEXT,                        -- Server IP address
    client_ip TEXT,                        -- Client IP address
    port INTEGER,                          -- Connection port
    
    -- USB Information (for USB connections)
    usb_device_path TEXT,                  -- USB device path
    adb_port INTEGER,                      -- ADB forwarded port
    
    -- Connection Quality Metrics
    total_requests INTEGER DEFAULT 0,      -- Total API requests in session
    successful_requests INTEGER DEFAULT 0,  -- Successful requests
    failed_requests INTEGER DEFAULT 0,     -- Failed requests
    average_latency_ms INTEGER,            -- Average response time
    total_bytes_transferred INTEGER DEFAULT 0, -- Data volume
    
    -- Status
    status TEXT DEFAULT 'active',          -- active, terminated, error
    termination_reason TEXT,               -- User, error, timeout, etc.
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_connections_device_id ON connections(device_id);
CREATE INDEX idx_connections_session_id ON connections(session_id);
CREATE INDEX idx_connections_type ON connections(connection_type);
CREATE INDEX idx_connections_status ON connections(status);
CREATE INDEX idx_connections_established_at ON connections(established_at);
```

### 5. api_logs
**Purpose**: Comprehensive API request logging and monitoring

```sql
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id TEXT UNIQUE NOT NULL,       -- UUID for request tracking
    device_id TEXT,                        -- Reference to devices.id (if applicable)
    connection_id INTEGER,                 -- Reference to connections.id
    
    -- Request Information
    method TEXT NOT NULL,                  -- GET, POST, PUT, DELETE
    endpoint TEXT NOT NULL,                -- API endpoint path
    query_params TEXT,                     -- JSON: query parameters
    headers TEXT,                          -- JSON: relevant headers
    
    -- Request Body
    request_body_size INTEGER DEFAULT 0,   -- Size in bytes
    request_body_hash TEXT,                -- MD5 hash of body (for deduplication)
    
    -- Response Information
    status_code INTEGER NOT NULL,          -- HTTP status code
    response_time_ms INTEGER NOT NULL,     -- Processing time
    response_size INTEGER DEFAULT 0,       -- Response size in bytes
    
    -- Error Information
    error_code TEXT,                       -- Application-specific error code
    error_message TEXT,                    -- Error message if applicable
    
    -- Timing
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Related Data
    nfc_data_id TEXT,                      -- Reference to nfc_data.id if applicable
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
    FOREIGN KEY (connection_id) REFERENCES connections(id) ON DELETE SET NULL,
    FOREIGN KEY (nfc_data_id) REFERENCES nfc_data(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_api_logs_device_id ON api_logs(device_id);
CREATE INDEX idx_api_logs_timestamp ON api_logs(timestamp);
CREATE INDEX idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX idx_api_logs_status_code ON api_logs(status_code);
CREATE INDEX idx_api_logs_request_id ON api_logs(request_id);
```

### 6. system_logs
**Purpose**: General system and application logging

```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,                   -- DEBUG, INFO, WARN, ERROR, CRITICAL
    source TEXT NOT NULL,                  -- Component/module name
    message TEXT NOT NULL,                 -- Log message
    
    -- Context Information
    device_id TEXT,                        -- Related device if applicable
    connection_id INTEGER,                 -- Related connection if applicable
    nfc_data_id TEXT,                      -- Related NFC data if applicable
    api_request_id TEXT,                   -- Related API request if applicable
    
    -- Detailed Information
    details TEXT,                          -- JSON: additional structured data
    stack_trace TEXT,                      -- Error stack trace if applicable
    
    -- Metadata
    thread_id TEXT,                        -- Processing thread identifier
    process_id INTEGER,                    -- Process ID
    memory_usage_mb INTEGER,               -- Memory usage at log time
    
    -- Timing
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE SET NULL,
    FOREIGN KEY (connection_id) REFERENCES connections(id) ON DELETE SET NULL,
    FOREIGN KEY (nfc_data_id) REFERENCES nfc_data(id) ON DELETE SET NULL
);

-- Indexes
CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_source ON system_logs(source);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX idx_system_logs_device_id ON system_logs(device_id);
```

### 7. configurations
**Purpose**: System and device configuration management

```sql
CREATE TABLE configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_type TEXT NOT NULL,             -- system, device, api
    config_key TEXT NOT NULL,              -- Configuration identifier
    device_id TEXT,                        -- NULL for system configs
    
    -- Configuration Data
    config_value TEXT NOT NULL,            -- JSON configuration value
    data_type TEXT NOT NULL,               -- string, integer, boolean, json
    default_value TEXT,                    -- Default value
    
    -- Metadata
    description TEXT,                      -- Human-readable description
    is_sensitive BOOLEAN DEFAULT FALSE,    -- Contains sensitive data
    is_editable BOOLEAN DEFAULT TRUE,      -- Can be modified by users
    
    -- Versioning
    version INTEGER DEFAULT 1,             -- Configuration version
    effective_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    effective_until DATETIME,              -- NULL for current config
    
    -- Audit
    created_by TEXT DEFAULT 'system',      -- Who created this config
    updated_by TEXT DEFAULT 'system',      -- Who last updated this config
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    UNIQUE(config_type, config_key, device_id, effective_from)
);

-- Indexes
CREATE INDEX idx_configurations_type_key ON configurations(config_type, config_key);
CREATE INDEX idx_configurations_device_id ON configurations(device_id);
CREATE INDEX idx_configurations_effective ON configurations(effective_from, effective_until);
```

## Views and Virtual Tables

### 1. device_summary_view
**Purpose**: Consolidated device information with statistics

```sql
CREATE VIEW device_summary_view AS
SELECT 
    d.id,
    d.name,
    d.model,
    d.status,
    d.last_seen,
    d.registered_at,
    COUNT(nd.id) as total_nfc_scans,
    COUNT(CASE WHEN nd.timestamp >= datetime('now', '-24 hours') THEN 1 END) as scans_last_24h,
    COUNT(CASE WHEN nd.status = 'processed' THEN 1 END) as successful_scans,
    COUNT(CASE WHEN nd.status = 'failed' THEN 1 END) as failed_scans,
    MAX(nd.timestamp) as last_scan_time,
    AVG(nd.processing_time_ms) as avg_processing_time,
    COUNT(DISTINCT c.id) as total_connections,
    MAX(c.established_at) as last_connection_time
FROM devices d
LEFT JOIN nfc_data nd ON d.id = nd.device_id
LEFT JOIN connections c ON d.id = c.device_id
GROUP BY d.id, d.name, d.model, d.status, d.last_seen, d.registered_at;
```

### 2. nfc_data_summary_view
**Purpose**: Enhanced NFC data view with record information

```sql
CREATE VIEW nfc_data_summary_view AS
SELECT 
    nd.*,
    d.name as device_name,
    d.model as device_model,
    COUNT(nr.id) as record_count_actual,
    GROUP_CONCAT(nr.type_name, '|') as record_types,
    c.connection_type,
    c.session_id
FROM nfc_data nd
JOIN devices d ON nd.device_id = d.id
LEFT JOIN nfc_records nr ON nd.id = nr.nfc_data_id
LEFT JOIN connections c ON nd.device_id = c.device_id 
    AND nd.received_at BETWEEN c.established_at AND COALESCE(c.terminated_at, datetime('now'))
GROUP BY nd.id;
```

## Triggers and Constraints

### 1. Update Timestamps
**Purpose**: Automatically update 'updated_at' columns

```sql
-- Devices table trigger
CREATE TRIGGER update_devices_timestamp 
    AFTER UPDATE ON devices
    FOR EACH ROW
BEGIN
    UPDATE devices SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- NFC Data table trigger
CREATE TRIGGER update_nfc_data_timestamp 
    AFTER UPDATE ON nfc_data
    FOR EACH ROW
BEGIN
    UPDATE nfc_data SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Connections table trigger
CREATE TRIGGER update_connections_timestamp 
    AFTER UPDATE ON connections
    FOR EACH ROW
BEGIN
    UPDATE connections SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### 2. Data Validation Constraints

```sql
-- Device status validation
ALTER TABLE devices ADD CONSTRAINT check_device_status 
    CHECK (status IN ('active', 'inactive', 'suspended'));

-- NFC data status validation
ALTER TABLE nfc_data ADD CONSTRAINT check_nfc_status 
    CHECK (status IN ('processed', 'failed', 'pending'));

-- Connection type validation
ALTER TABLE connections ADD CONSTRAINT check_connection_type 
    CHECK (connection_type IN ('USB', 'WIFI'));

-- Log level validation
ALTER TABLE system_logs ADD CONSTRAINT check_log_level 
    CHECK (level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'));
```

### 3. Data Integrity Triggers

```sql
-- Auto-generate server_id for nfc_data
CREATE TRIGGER auto_server_id_nfc_data
    AFTER INSERT ON nfc_data
    FOR EACH ROW
    WHEN NEW.server_id IS NULL
BEGIN
    UPDATE nfc_data SET server_id = NEW.rowid WHERE id = NEW.id;
END;

-- Update device last_seen on heartbeat
CREATE TRIGGER update_device_last_seen
    AFTER INSERT ON api_logs
    FOR EACH ROW
    WHEN NEW.endpoint = '/api/v1/connection/heartbeat' AND NEW.status_code = 200
BEGIN
    UPDATE devices SET last_seen = NEW.timestamp WHERE id = NEW.device_id;
END;
```

## Data Retention and Archival

### 1. Retention Policies
```sql
-- Clean up old API logs (older than 90 days)
CREATE TRIGGER cleanup_old_api_logs
    AFTER INSERT ON api_logs
    FOR EACH ROW
BEGIN
    DELETE FROM api_logs WHERE timestamp < datetime('now', '-90 days');
END;

-- Clean up old system logs (older than 30 days)
CREATE TRIGGER cleanup_old_system_logs
    AFTER INSERT ON system_logs
    FOR EACH ROW
BEGIN
    DELETE FROM system_logs WHERE timestamp < datetime('now', '-30 days') AND level != 'ERROR';
END;
```

### 2. Archival Tables
```sql
-- Archived NFC data for long-term storage
CREATE TABLE nfc_data_archive (
    archived_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    original_data TEXT  -- JSON dump of original nfc_data record
);
```

## Database Initialization Script

### 1. Initial Setup
```sql
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Set journal mode for better concurrency
PRAGMA journal_mode = WAL;

-- Set synchronous mode for better performance
PRAGMA synchronous = NORMAL;

-- Create all tables in order
-- (Tables creation statements from above)

-- Insert default system configurations
INSERT INTO configurations (config_type, config_key, config_value, data_type, description) VALUES
('system', 'max_devices', '10', 'integer', 'Maximum number of registered devices'),
('system', 'api_rate_limit', '100', 'integer', 'API requests per hour per device'),
('system', 'log_retention_days', '30', 'integer', 'System log retention period'),
('system', 'nfc_data_retention_days', '365', 'integer', 'NFC data retention period'),
('api', 'default_heartbeat_interval', '30', 'integer', 'Default heartbeat interval in seconds'),
('api', 'max_payload_size', '1048576', 'integer', 'Maximum API payload size in bytes');
```

## Performance Optimization

### 1. Indexing Strategy
- Primary keys: Automatic unique indexes
- Foreign keys: Explicit indexes for join performance
- Timestamp columns: For time-based queries
- Status columns: For filtering active/inactive records
- Frequently queried columns: Device ID, API endpoints

### 2. Query Optimization
- Use views for complex, frequently-used queries
- Implement pagination for large result sets
- Use EXPLAIN QUERY PLAN for query optimization
- Regular VACUUM and ANALYZE operations

### 3. Storage Optimization
- BLOB storage for binary NFC data
- JSON storage for flexible configuration data
- Efficient timestamp storage using DATETIME type
- Compression for archived data

This database schema provides a comprehensive foundation for the NFC Reader/Writer system, ensuring data integrity, performance, and scalability while supporting all required functionality for device management, NFC data storage, and system monitoring.
