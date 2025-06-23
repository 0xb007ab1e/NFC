# NFC Reader/Writer System - Communication Protocols

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Protocol Overview

### Communication Methods
1. **USB Connection**: Direct device-to-PC communication via ADB bridge
2. **WiFi Connection**: Network-based communication via HTTP/HTTPS API
3. **Fallback Mechanisms**: Automatic switching between connection types
4. **Offline Mode**: Local caching with synchronization when connected

## USB Communication Protocol

### 1. USB Connection Architecture

```
┌─────────────────────┐    USB Cable    ┌─────────────────────┐
│   Android Device    │◄──────────────►│      PC Server      │
│                     │                 │                     │
│ ┌─────────────────┐ │                 │ ┌─────────────────┐ │
│ │ NFC Reader App  │ │                 │ │   Server App    │ │
│ └─────────────────┘ │                 │ └─────────────────┘ │
│          │          │                 │          │          │
│ ┌─────────────────┐ │                 │ ┌─────────────────┐ │
│ │ Android ADB     │ │                 │ │   ADB Server    │ │
│ │ Debug Bridge    │ │                 │ │   (PC)          │ │
│ └─────────────────┘ │                 │ └─────────────────┘ │
│          │          │                 │          │          │
│ ┌─────────────────┐ │                 │ ┌─────────────────┐ │
│ │ USB Stack       │ │                 │ │ USB Driver      │ │
│ └─────────────────┘ │                 │ └─────────────────┘ │
└─────────────────────┘                 └─────────────────────┘
```

### 2. USB Connection Establishment

#### Step 1: Prerequisites Check
```
Android Device Requirements:
- USB Debugging enabled in Developer Options
- Device authorized for debugging
- NFC Reader app installed with debug permissions

PC Requirements:
- ADB (Android Debug Bridge) installed
- USB drivers for the Android device
- NFC Server application running
```

#### Step 2: Connection Sequence
```
1. Physical USB connection detected
2. ADB daemon startup (both PC and Android)
3. Device authorization handshake
4. Port forwarding establishment
5. Application-level connection test
6. Security key exchange
7. Ready for data transmission
```

#### Step 3: Port Forwarding Setup
```bash
# PC Server establishes local listener
adb forward tcp:8080 tcp:8080

# Android app connects to forwarded port
http://localhost:8080/api/v1/
```

### 3. USB Data Transmission Protocol

#### Message Format
```
USB Message Structure:
┌──────────────────────────────────────────────────────────┐
│ Header (32 bytes)                                        │
├──────────────────────────────────────────────────────────┤
│ Message ID (16 bytes)   │ Message Type (4 bytes)         │
├──────────────────────────────────────────────────────────┤
│ Payload Length (4 bytes)│ CRC32 (4 bytes)               │
├──────────────────────────────────────────────────────────┤
│ Timestamp (8 bytes)                                      │
├──────────────────────────────────────────────────────────┤
│ Payload (Variable Length)                                │
│                                                          │
│ [JSON Data or Binary Data]                               │
└──────────────────────────────────────────────────────────┘
```

#### Message Types
```json
{
  "message_types": {
    "0x01": "HANDSHAKE",
    "0x02": "HEARTBEAT", 
    "0x03": "NFC_DATA",
    "0x04": "CONFIG_REQUEST",
    "0x05": "CONFIG_RESPONSE",
    "0x06": "ERROR",
    "0x07": "ACK",
    "0x08": "STATUS_REQUEST",
    "0x09": "STATUS_RESPONSE",
    "0x0A": "DISCONNECT"
  }
}
```

#### Handshake Protocol
```
Android → PC: HANDSHAKE
{
  "message_type": "HANDSHAKE",
  "device_info": {
    "device_id": "android_device_12345",
    "app_version": "1.0.0",
    "android_version": "12",
    "supported_nfc_types": ["NDEF", "ISO14443A", "MIFARE_CLASSIC"]
  },
  "auth_token": "temp_auth_token_12345"
}

PC → Android: HANDSHAKE_RESPONSE
{
  "message_type": "HANDSHAKE_RESPONSE",
  "status": "accepted",
  "server_info": {
    "version": "1.0.0",
    "api_version": "v1",
    "max_payload_size": 1048576
  },
  "auth_token": "session_auth_token_67890",
  "session_id": "session_uuid_abcdef"
}
```

### 4. USB Error Handling

#### Connection Errors
```json
{
  "usb_errors": {
    "USB_DEVICE_NOT_FOUND": {
      "code": "USB001",
      "message": "Android device not detected",
      "recovery": "Check USB cable and device connection"
    },
    "ADB_NOT_AUTHORIZED": {
      "code": "USB002", 
      "message": "Device not authorized for debugging",
      "recovery": "Accept ADB debugging prompt on device"
    },
    "PORT_FORWARD_FAILED": {
      "code": "USB003",
      "message": "Failed to establish port forwarding",
      "recovery": "Restart ADB server and retry"
    },
    "CONNECTION_TIMEOUT": {
      "code": "USB004",
      "message": "Connection establishment timeout",
      "recovery": "Check device connectivity and retry"
    }
  }
}
```

#### Recovery Mechanisms
```
1. Automatic Retry: 3 attempts with exponential backoff
2. Port Reset: Clear existing port forwarding and re-establish
3. ADB Restart: Kill and restart ADB daemon
4. Fallback: Switch to WiFi connection if available
5. Cache Mode: Store data locally until connection restored
```

## WiFi Communication Protocol

### 1. WiFi Connection Architecture

```
┌─────────────────────┐    WiFi Network    ┌─────────────────────┐
│   Android Device    │◄──────────────────►│      PC Server      │
│                     │    (192.168.x.x)   │                     │
│ ┌─────────────────┐ │                    │ ┌─────────────────┐ │
│ │ NFC Reader App  │ │                    │ │   HTTP Server   │ │
│ └─────────────────┘ │                    │ └─────────────────┘ │
│          │          │                    │          │          │
│ ┌─────────────────┐ │                    │ ┌─────────────────┐ │
│ │ HTTP Client     │ │                    │ │   API Router    │ │
│ │ (OkHttp/Retrofit)│ │                    │ │   (Flask/FastAPI)│ │
│ └─────────────────┘ │                    │ └─────────────────┘ │
│          │          │                    │          │          │
│ ┌─────────────────┐ │                    │ ┌─────────────────┐ │
│ │ WiFi Stack      │ │                    │ │ Network Stack   │ │
│ └─────────────────┘ │                    │ └─────────────────┘ │
└─────────────────────┘                    └─────────────────────┘
```

### 2. Server Discovery Protocol

#### mDNS Service Discovery
```
Service Type: _nfc-reader._tcp.local.
Service Name: nfc-server-{hostname}
Port: 8080 (HTTP) / 8443 (HTTPS)
TXT Records:
  version=1.0.0
  api=v1
  auth=api-key
  secure=true/false
  max_clients=10
```

#### Discovery Process
```
1. Android app broadcasts mDNS query
   Query: _nfc-reader._tcp.local.

2. PC server responds with service information
   Response: nfc-server-pc123._nfc-reader._tcp.local.
             Port: 8080
             TXT: version=1.0.0,api=v1,auth=api-key

3. Android app attempts connection to discovered server
   GET http://192.168.1.100:8080/api/v1/health

4. Server responds with capabilities
   Response: {"status": "healthy", "version": "1.0.0"}

5. Authentication and registration process
   POST http://192.168.1.100:8080/api/v1/devices/register
```

#### Manual Server Configuration
```json
{
  "manual_config": {
    "server_ip": "192.168.1.100",
    "server_port": 8080,
    "use_https": false,
    "api_key": "user_provided_key",
    "verify_ssl": true,
    "connection_timeout": 30
  }
}
```

### 3. WiFi Authentication and Security

#### API Key Authentication
```
Request Headers:
Authorization: ApiKey {device_api_key}
X-Device-ID: {android_device_id}
X-App-Version: {app_version}
Content-Type: application/json
```

#### TLS/SSL Configuration
```json
{
  "tls_config": {
    "min_version": "TLSv1.2",
    "cipher_suites": [
      "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
      "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
      "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384"
    ],
    "certificate_verification": true,
    "certificate_pinning": false
  }
}
```

#### Request Signing (Optional)
```
HMAC-SHA256 signature using shared secret:
X-Signature: sha256={signature}
X-Timestamp: {unix_timestamp}

Signature calculation:
message = method + url + timestamp + body
signature = HMAC-SHA256(shared_secret, message)
```

### 4. WiFi Data Transmission

#### Standard HTTP Request Format
```http
POST /api/v1/nfc/data HTTP/1.1
Host: 192.168.1.100:8080
Authorization: ApiKey device_specific_key_xyz789
X-Device-ID: android_device_12345
X-Request-ID: req_uuid_67890
Content-Type: application/json
Content-Length: 1024
Connection: keep-alive

{
  "nfc_data": {
    "id": "nfc_scan_uuid_12345",
    "timestamp": "2025-06-23T20:13:31.123Z",
    "device_id": "android_device_12345",
    // ... NFC data payload
  }
}
```

#### Batch Request Format
```http
POST /api/v1/nfc/batch HTTP/1.1
Host: 192.168.1.100:8080
Authorization: ApiKey device_specific_key_xyz789
X-Device-ID: android_device_12345
Content-Type: application/json

{
  "batch": {
    "id": "batch_uuid_12345",
    "count": 5,
    "nfc_data": [
      // Array of NFC data objects
    ]
  }
}
```

### 5. Connection Quality Monitoring

#### Network Quality Metrics
```json
{
  "network_metrics": {
    "latency_ms": 25,
    "jitter_ms": 5,
    "packet_loss_percent": 0.1,
    "bandwidth_kbps": 1024,
    "signal_strength_dbm": -45,
    "connection_quality": "excellent|good|fair|poor"
  }
}
```

#### Quality Assessment Algorithm
```
Quality Scoring:
- Latency: < 50ms = 30 points, < 100ms = 20 points, < 200ms = 10 points
- Packet Loss: < 1% = 25 points, < 5% = 15 points, < 10% = 5 points  
- Jitter: < 10ms = 20 points, < 25ms = 10 points, < 50ms = 5 points
- Signal: > -50dBm = 25 points, > -70dBm = 15 points, > -80dBm = 5 points

Total Score:
- 80-100: Excellent
- 60-79: Good  
- 40-59: Fair
- 0-39: Poor
```

## Connection Management

### 1. Connection State Machine

```
States:
- DISCONNECTED: No active connection
- CONNECTING: Attempting to establish connection
- CONNECTED: Active and healthy connection
- DEGRADED: Connected but poor quality
- RECONNECTING: Attempting to restore connection
- FAILED: Connection failed, using cache mode

Transitions:
DISCONNECTED → CONNECTING: User initiate or auto-connect
CONNECTING → CONNECTED: Successful connection establishment
CONNECTING → FAILED: Connection timeout or error
CONNECTED → DEGRADED: Quality metrics below threshold
CONNECTED → RECONNECTING: Connection lost
DEGRADED → CONNECTED: Quality improved
DEGRADED → RECONNECTING: Connection lost
RECONNECTING → CONNECTED: Connection restored
RECONNECTING → FAILED: Reconnection failed
FAILED → CONNECTING: Manual retry or timer-based retry
```

### 2. Automatic Failover Protocol

#### Connection Priority
```
1. USB Connection (if available and stable)
2. WiFi Connection (if available and good quality)
3. Offline Mode (cache locally)
```

#### Failover Sequence
```
1. Monitor primary connection quality
2. If quality degrades below threshold:
   a. Attempt to improve connection
   b. If unsuccessful, initiate failover
3. Test secondary connection availability
4. Switch to secondary connection
5. Notify user of connection change
6. Continue monitoring for primary restoration
```

### 3. Heartbeat and Keep-Alive

#### Heartbeat Protocol
```json
{
  "heartbeat_request": {
    "timestamp": "2025-06-23T20:13:31Z",
    "device_id": "android_device_12345",
    "connection_type": "WIFI",
    "device_status": {
      "battery_level": 85,
      "nfc_enabled": true,
      "pending_scans": 0
    }
  }
}

{
  "heartbeat_response": {
    "timestamp": "2025-06-23T20:13:31.456Z",
    "status": "healthy",
    "next_heartbeat": 30,
    "server_commands": []
  }
}
```

#### Keep-Alive Configuration
```json
{
  "keep_alive_settings": {
    "heartbeat_interval": 30,
    "missed_heartbeat_threshold": 3,
    "connection_timeout": 90,
    "retry_interval": 10,
    "max_retry_attempts": 5
  }
}
```

## Data Integrity and Reliability

### 1. Message Acknowledgment

#### Request-Response Pattern
```
1. Client sends request with unique ID
2. Server processes request
3. Server sends response with same ID
4. Client matches response to request
5. If no response within timeout, retry
```

#### Acknowledgment Types
```json
{
  "ack_types": {
    "RECEIVED": "Message received by server",
    "PROCESSED": "Message processed successfully", 
    "STORED": "Data stored in database",
    "ERROR": "Processing error occurred"
  }
}
```

### 2. Data Validation and Checksums

#### Checksum Verification
```
1. Client calculates MD5 hash of payload
2. Include checksum in message header
3. Server recalculates checksum upon receipt
4. Compare checksums for integrity verification
5. Reject message if checksums don't match
```

#### Data Validation Layers
```
1. Transport Layer: TCP/HTTP checksums
2. Message Layer: Custom MD5 checksums  
3. Application Layer: JSON schema validation
4. Business Layer: NFC data format validation
```

### 3. Retry and Recovery Mechanisms

#### Exponential Backoff
```
Retry Intervals:
Attempt 1: Immediate
Attempt 2: 1 second
Attempt 3: 2 seconds  
Attempt 4: 4 seconds
Attempt 5: 8 seconds
Max Interval: 60 seconds
```

#### Circuit Breaker Pattern
```
States:
- CLOSED: Normal operation
- OPEN: Failures exceeded threshold, reject requests
- HALF_OPEN: Test if service recovered

Thresholds:
- Failure Rate: 50% in 60 seconds
- Response Time: > 5 seconds
- Recovery Test: After 30 seconds in OPEN state
```

## Performance Optimization

### 1. Connection Pooling

#### HTTP Connection Pool
```json
{
  "connection_pool": {
    "max_idle_connections": 5,
    "keep_alive_duration": 300,
    "connection_timeout": 30,
    "read_timeout": 60,
    "write_timeout": 60
  }
}
```

### 2. Data Compression

#### Payload Compression
```
1. JSON payload compression using GZIP
2. Automatic compression for payloads > 1KB
3. Client indicates compression support in headers
4. Server responds with compressed data if supported
```

### 3. Bandwidth Optimization

#### Adaptive Quality
```
High Bandwidth (>1Mbps):
- Full NFC data transmission
- High-resolution metadata
- Real-time transmission

Medium Bandwidth (100Kbps-1Mbps):
- Compressed NFC data
- Essential metadata only
- Batch transmission

Low Bandwidth (<100Kbps):
- Minimal NFC data
- Text-only records
- Delayed transmission
```

This comprehensive communication protocol specification ensures reliable, efficient, and secure data transmission between the Android NFC Reader/Writer application and the PC server across both USB and WiFi connections.
