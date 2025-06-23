# NFC Reader/Writer System - API Specifications

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## API Overview

### Base Configuration
- **Protocol**: HTTP/HTTPS
- **Data Format**: JSON
- **Authentication**: API Key / Bearer Token
- **Content-Type**: application/json
- **Character Encoding**: UTF-8

### Server Endpoints Base URLs
- **USB Connection**: http://localhost:8080/api/v1
- **WiFi Connection**: http://{server_ip}:8080/api/v1 or https://{server_ip}:8443/api/v1

## Authentication

### API Key Authentication
All requests must include authentication header:
```
Authorization: ApiKey {api_key}
```

### Device Registration
Initial device pairing process:
```
X-Device-ID: {android_device_id}
X-Device-Name: {human_readable_device_name}
```

## Core API Endpoints

### 1. Health Check and Status

#### GET /health
**Purpose**: Server health check and status verification
**Authentication**: Not required

**Request**:
```http
GET /api/v1/health HTTP/1.1
Host: server:8080
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-06-23T19:28:24Z",
  "version": "1.0.0",
  "uptime": "3600",
  "services": {
    "database": "healthy",
    "logging": "healthy",
    "usb": "available",
    "wifi": "available"
  }
}
```

**Status Codes**:
- 200: Server healthy
- 503: Server unhealthy or maintenance mode

#### GET /status
**Purpose**: Detailed server status and configuration
**Authentication**: Required

**Request**:
```http
GET /api/v1/status HTTP/1.1
Host: server:8080
Authorization: ApiKey abc123xyz
```

**Response**:
```json
{
  "server": {
    "status": "running",
    "timestamp": "2025-06-23T19:28:24Z",
    "version": "1.0.0",
    "uptime": "3600"
  },
  "connections": {
    "active_devices": 2,
    "total_sessions": 15,
    "connection_types": {
      "usb": 1,
      "wifi": 1
    }
  },
  "storage": {
    "disk_usage": "45%",
    "log_entries": 1250,
    "database_size": "15MB"
  },
  "configuration": {
    "max_devices": 10,
    "log_retention_days": 30,
    "api_version": "v1"
  }
}
```

### 2. Device Management

#### POST /devices/register
**Purpose**: Register new Android device with server
**Authentication**: Initial API key required

**Request**:
```http
POST /api/v1/devices/register HTTP/1.1
Host: server:8080
Authorization: ApiKey abc123xyz
Content-Type: application/json

{
  "device": {
    "id": "android_device_12345",
    "name": "John's Phone",
    "model": "Samsung Galaxy S21",
    "android_version": "12",
    "app_version": "1.0.0",
    "capabilities": {
      "nfc_types": ["NDEF", "ISO14443A", "MIFARE_CLASSIC"],
      "connection_types": ["USB", "WIFI"]
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "device": {
    "id": "android_device_12345",
    "registered_at": "2025-06-23T19:28:24Z",
    "api_key": "device_specific_api_key_xyz789",
    "status": "registered"
  },
  "server_info": {
    "supported_api_version": "v1",
    "max_payload_size": "1MB",
    "heartbeat_interval": 30
  }
}
```

**Status Codes**:
- 201: Device registered successfully
- 400: Invalid device information
- 409: Device already registered
- 500: Server error during registration

#### GET /devices/{device_id}
**Purpose**: Get device information and status
**Authentication**: Required

**Response**:
```json
{
  "device": {
    "id": "android_device_12345",
    "name": "John's Phone",
    "status": "online",
    "last_seen": "2025-06-23T19:25:00Z",
    "connection_type": "WIFI",
    "statistics": {
      "total_nfc_scans": 156,
      "successful_transmissions": 154,
      "failed_transmissions": 2,
      "average_response_time": "250ms"
    }
  }
}
```

### 3. NFC Data Transmission

#### POST /nfc/data
**Purpose**: Submit NFC scan data to server
**Authentication**: Required (device-specific API key)

**Request**:
```http
POST /api/v1/nfc/data HTTP/1.1
Host: server:8080
Authorization: ApiKey device_specific_api_key_xyz789
X-Device-ID: android_device_12345
Content-Type: application/json

{
  "nfc_data": {
    "id": "nfc_scan_uuid_12345",
    "timestamp": "2025-06-23T19:28:24.123Z",
    "device_id": "android_device_12345",
    "tag_info": {
      "type": "NDEF",
      "uid": "04:A1:B2:C3:D4:E5:F6",
      "technology": "ISO14443A",
      "max_transceive_length": 253
    },
    "data": {
      "raw": "base64_encoded_raw_data_here",
      "parsed": {
        "records": [
          {
            "tnf": 1,
            "type": "T",
            "payload": "Hello World",
            "language": "en",
            "encoding": "UTF-8"
          }
        ]
      }
    },
    "metadata": {
      "read_time_ms": 245,
      "signal_strength": -45,
      "read_attempts": 1,
      "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "accuracy": 10.5
      }
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "nfc_scan_uuid_12345",
    "server_id": "server_record_67890",
    "received_at": "2025-06-23T19:28:24.456Z",
    "status": "processed",
    "checksum": "md5_hash_of_data"
  },
  "server_info": {
    "processing_time_ms": 45,
    "storage_location": "logs/2025/06/23/nfc_data.log"
  }
}
```

**Status Codes**:
- 201: Data received and processed successfully
- 400: Invalid data format
- 401: Authentication failed
- 413: Payload too large
- 422: Data validation failed
- 500: Server processing error

#### POST /nfc/batch
**Purpose**: Submit multiple NFC scans in batch
**Authentication**: Required

**Request**:
```http
POST /api/v1/nfc/batch HTTP/1.1
Host: server:8080
Authorization: ApiKey device_specific_api_key_xyz789
X-Device-ID: android_device_12345
Content-Type: application/json

{
  "batch": {
    "id": "batch_uuid_12345",
    "timestamp": "2025-06-23T19:28:24Z",
    "device_id": "android_device_12345",
    "count": 3,
    "nfc_data": [
      {
        "id": "nfc_scan_1",
        "timestamp": "2025-06-23T19:28:20Z",
        // ... nfc_data structure ...
      },
      {
        "id": "nfc_scan_2",
        "timestamp": "2025-06-23T19:28:22Z",
        // ... nfc_data structure ...
      },
      {
        "id": "nfc_scan_3",
        "timestamp": "2025-06-23T19:28:24Z",
        // ... nfc_data structure ...
      }
    ]
  }
}
```

**Response**:
```json
{
  "success": true,
  "batch": {
    "id": "batch_uuid_12345",
    "received_at": "2025-06-23T19:28:24.456Z",
    "total_count": 3,
    "processed_count": 3,
    "failed_count": 0,
    "results": [
      {
        "id": "nfc_scan_1",
        "status": "processed",
        "server_id": "server_record_1001"
      },
      {
        "id": "nfc_scan_2",
        "status": "processed",
        "server_id": "server_record_1002"
      },
      {
        "id": "nfc_scan_3",
        "status": "processed",
        "server_id": "server_record_1003"
      }
    ]
  }
}
```

### 4. Connection Management

#### POST /connection/heartbeat
**Purpose**: Maintain connection alive and report device status
**Authentication**: Required

**Request**:
```http
POST /api/v1/connection/heartbeat HTTP/1.1
Host: server:8080
Authorization: ApiKey device_specific_api_key_xyz789
X-Device-ID: android_device_12345
Content-Type: application/json

{
  "heartbeat": {
    "timestamp": "2025-06-23T19:28:24Z",
    "device_id": "android_device_12345",
    "connection_type": "WIFI",
    "device_status": {
      "battery_level": 85,
      "nfc_enabled": true,
      "storage_available": "2.5GB",
      "app_version": "1.0.0"
    },
    "statistics": {
      "pending_transmissions": 0,
      "cache_size": "125KB",
      "uptime": "7200"
    }
  }
}
```

**Response**:
```json
{
  "success": true,
  "server_time": "2025-06-23T19:28:24.789Z",
  "next_heartbeat": "2025-06-23T19:28:54Z",
  "commands": [
    {
      "type": "config_update",
      "payload": {
        "heartbeat_interval": 30,
        "batch_size": 10
      }
    }
  ]
}
```

#### GET /connection/info
**Purpose**: Get connection information and settings
**Authentication**: Required

**Response**:
```json
{
  "connection": {
    "device_id": "android_device_12345",
    "type": "WIFI",
    "established_at": "2025-06-23T19:20:00Z",
    "last_activity": "2025-06-23T19:28:20Z",
    "quality": {
      "latency_ms": 25,
      "packet_loss": 0,
      "bandwidth": "good"
    }
  },
  "settings": {
    "heartbeat_interval": 30,
    "batch_size": 10,
    "retry_attempts": 3,
    "timeout_seconds": 30
  }
}
```

### 5. Configuration Management

#### GET /config
**Purpose**: Get device-specific configuration from server
**Authentication**: Required

**Response**:
```json
{
  "config": {
    "device_id": "android_device_12345",
    "updated_at": "2025-06-23T19:00:00Z",
    "settings": {
      "nfc": {
        "auto_scan": true,
        "scan_timeout_ms": 5000,
        "supported_types": ["NDEF", "ISO14443A", "MIFARE_CLASSIC"]
      },
      "communication": {
        "preferred_connection": "WIFI",
        "heartbeat_interval": 30,
        "batch_size": 10,
        "retry_attempts": 3,
        "timeout_seconds": 30
      },
      "data": {
        "include_location": true,
        "include_metadata": true,
        "cache_size_mb": 50
      },
      "ui": {
        "theme": "auto",
        "notifications_enabled": true,
        "sound_enabled": false
      }
    }
  }
}
```

#### POST /config
**Purpose**: Update device configuration
**Authentication**: Required

**Request**:
```json
{
  "config_update": {
    "device_id": "android_device_12345",
    "settings": {
      "communication": {
        "heartbeat_interval": 60,
        "batch_size": 20
      }
    }
  }
}
```

### 6. Logging and Monitoring

#### GET /logs
**Purpose**: Retrieve server logs (admin/debug endpoint)
**Authentication**: Admin API key required

**Query Parameters**:
- `level`: DEBUG|INFO|WARN|ERROR
- `device_id`: Filter by device
- `start_date`: ISO8601 date
- `end_date`: ISO8601 date
- `limit`: Number of entries (default: 100, max: 1000)

**Response**:
```json
{
  "logs": [
    {
      "id": "log_entry_12345",
      "timestamp": "2025-06-23T19:28:24.123Z",
      "level": "INFO",
      "source": "nfc_processor",
      "message": "NFC data processed successfully",
      "device_id": "android_device_12345",
      "nfc_data_id": "nfc_scan_uuid_12345",
      "metadata": {
        "processing_time_ms": 45,
        "connection_type": "WIFI"
      }
    }
  ],
  "pagination": {
    "total_count": 1250,
    "returned_count": 100,
    "has_more": true,
    "next_cursor": "cursor_token_xyz"
  }
}
```

## Error Responses

### Standard Error Format
All error responses follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": "Detailed error information",
    "timestamp": "2025-06-23T19:28:24Z",
    "request_id": "req_12345",
    "documentation_url": "https://docs.example.com/errors/ERROR_CODE"
  }
}
```

### Common Error Codes

#### Authentication Errors (401)
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or expired",
    "details": "API key 'abc123' not found in registered devices"
  }
}
```

#### Validation Errors (422)
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request data validation failed",
    "details": {
      "field_errors": [
        {
          "field": "nfc_data.timestamp",
          "code": "INVALID_FORMAT",
          "message": "Timestamp must be in ISO8601 format"
        }
      ]
    }
  }
}
```

#### Server Errors (500)
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An internal server error occurred",
    "details": "Error processing NFC data",
    "request_id": "req_12345"
  }
}
```

## Rate Limiting

### Rate Limit Headers
All responses include rate limiting information:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 3600
```

### Rate Limit Exceeded (429)
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": "100 requests per hour limit exceeded",
    "retry_after": 3600
  }
}
```

## Webhooks (Future Enhancement)

### Webhook Registration
For future real-time notifications:

#### POST /webhooks
```json
{
  "webhook": {
    "url": "https://client.example.com/webhook",
    "events": ["nfc_data_received", "device_status_changed"],
    "secret": "webhook_secret_key"
  }
}
```

## API Versioning

### Version Header
```
Accept: application/vnd.nfc-reader.v1+json
```

### URL Versioning (Current)
```
/api/v1/endpoint
```

## Testing Endpoints

### POST /test/nfc-data
**Purpose**: Submit test NFC data for development/testing
**Authentication**: Test API key

**Request**:
```json
{
  "test_data": {
    "scenario": "basic_ndef_text",
    "device_id": "test_device_001",
    "count": 5
  }
}
```

### GET /test/health
**Purpose**: Extended health check with test results
**Authentication**: Not required

This API specification provides a comprehensive interface for communication between the Android NFC Reader/Writer application and the PC server, ensuring reliable data transmission, proper error handling, and extensibility for future enhancements.
