# NFC Reader/Writer System - Architecture Design

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## System Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────────┐
│                          NFC Reader/Writer System                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐              ┌─────────────────────────┐   │
│  │   Android Device    │              │      PC Server         │   │
│  │  (Readr/Writer)     │              │                         │   │
│  │                     │    USB       │                         │   │
│  │  ┌───────────────┐  │◄────────────►│  ┌───────────────────┐  │   │
│  │  │ NFC Scanner   │  │              │  │   Data Logger     │  │   │
│  │  └───────────────┘  │              │  └───────────────────┘  │   │
│  │  ┌───────────────┐  │              │  ┌───────────────────┐  │   │
│  │  │ UI Interface  │  │    WiFi      │  │   HTTP API        │  │   │
│  │  └───────────────┘  │◄────────────►│  └───────────────────┘  │   │
│  │  ┌───────────────┐  │              │  ┌───────────────────┐  │   │
│  │  │ Comm Manager  │  │              │  │   USB Handler     │  │   │
│  │  └───────────────┘  │              │  └───────────────────┘  │   │
│  └─────────────────────┘              └─────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Android Application Architecture

#### 1.1 Core Components
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Android Application Layer                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     UI Layer                                │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │  Main Activity  │ │ Settings        │ │ Status Display  │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Service Layer                              │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ NFC Service     │ │ Connection Mgr  │ │ Data Service    │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Data Layer                                 │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ Local Database  │ │ Cache Manager   │ │ Config Storage  │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                Communication Layer                          │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ USB Client      │ │ WiFi Client     │ │ API Client      │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 1.2 Key Android Components

**NFC Service**
- Handles NFC tag detection and reading
- Manages NFC adapter lifecycle
- Processes various NFC tag types (NDEF, ISO14443, etc.)
- Data validation and formatting

**Connection Manager**
- Manages USB and WiFi connections
- Connection state monitoring
- Automatic failover between connection types
- Connection health monitoring

**Data Service**
- Manages data flow between NFC service and communication layer
- Implements data queuing and retry logic
- Handles offline data caching
- Data integrity verification

**UI Interface**
- Main activity for user interaction
- Real-time status updates
- Connection status indicators
- Configuration interface

### 2. PC Server Architecture

#### 2.1 Core Components
```
┌─────────────────────────────────────────────────────────────────────┐
│                      PC Server Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   API Layer                                 │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ HTTP Server     │ │ WebSocket       │ │ API Router      │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Business Logic Layer                        │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ Data Processor  │ │ Validator       │ │ Logger Service  │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Data Layer                                 │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ File System     │ │ Database        │ │ Config Manager  │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                Communication Layer                          │   │
│  │  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │   │
│  │  │ USB Handler     │ │ Network Handler │ │ Protocol Mgr    │ │   │
│  │  └─────────────────┘ └─────────────────┘ └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

#### 2.2 Key PC Server Components

**HTTP Server**
- RESTful API endpoints for data reception
- Authentication and authorization
- Request/response handling
- CORS support for web clients

**Data Processor**
- Incoming data validation and parsing
- Data transformation and normalization
- Duplicate detection and filtering
- Format conversion utilities

**Logger Service**
- Structured logging of all NFC data
- Configurable log levels and formats
- Log rotation and archival
- Real-time log viewing capabilities

**USB Handler**
- USB device detection and connection
- ADB (Android Debug Bridge) communication
- Direct USB data transfer
- Device state monitoring

## Communication Protocols

### 1. USB Communication Protocol

#### 1.1 Connection Establishment
```
┌─────────────────┐              ┌─────────────────┐
│ Android Device  │              │   PC Server     │
└─────────────────┘              └─────────────────┘
         │                                │
         │ 1. USB Connection Detected     │
         │◄──────────────────────────────►│
         │                                │
         │ 2. ADB Bridge Initialization   │
         │◄──────────────────────────────►│
         │                                │
         │ 3. Port Forwarding Setup       │
         │◄──────────────────────────────►│
         │                                │
         │ 4. Handshake & Authentication  │
         │◄──────────────────────────────►│
         │                                │
         │ 5. Ready for Data Transfer     │
         │◄──────────────────────────────►│
```

#### 1.2 Data Transfer Protocol
- **Transport**: TCP over USB (via ADB port forwarding)
- **Port**: 8080 (configurable)
- **Format**: JSON over HTTP
- **Authentication**: API key based
- **Encryption**: TLS/SSL (optional)

### 2. WiFi Communication Protocol

#### 2.1 Network Discovery
```
┌─────────────────┐              ┌─────────────────┐
│ Android Device  │              │   PC Server     │
└─────────────────┘              └─────────────────┘
         │                                │
         │ 1. Network Scan                │
         │───────────────────────────────►│
         │                                │
         │ 2. Server Discovery (mDNS)     │
         │◄──────────────────────────────►│
         │                                │
         │ 3. Connection Establishment    │
         │◄──────────────────────────────►│
         │                                │
         │ 4. Authentication              │
         │◄──────────────────────────────►│
         │                                │
         │ 5. Ready for Data Transfer     │
         │◄──────────────────────────────►│
```

#### 2.2 Data Transfer Protocol
- **Transport**: HTTP/HTTPS
- **Port**: 8080 (HTTP) / 8443 (HTTPS)
- **Format**: JSON REST API
- **Authentication**: Bearer token / API key
- **Discovery**: mDNS service discovery

## Data Models

### 1. NFC Data Structure
```json
{
  "nfcData": {
    "id": "uuid",
    "timestamp": "ISO8601",
    "deviceId": "android_device_identifier",
    "tagType": "NDEF|ISO14443A|ISO14443B|ISO15693|MIFARE_CLASSIC|MIFARE_ULTRALIGHT",
    "uid": "hex_string",
    "data": {
      "raw": "base64_encoded_data",
      "parsed": {
        "records": [
          {
            "type": "TEXT|URI|MIME|EXTERNAL",
            "payload": "content",
            "language": "en",
            "encoding": "UTF-8"
          }
        ]
      }
    },
    "metadata": {
      "rssi": "signal_strength",
      "readTime": "milliseconds",
      "attempts": "retry_count"
    }
  }
}
```

### 2. Communication Message Structure
```json
{
  "message": {
    "id": "uuid",
    "type": "DATA|STATUS|COMMAND|RESPONSE",
    "timestamp": "ISO8601",
    "source": "android|server",
    "destination": "android|server",
    "payload": "varies_by_type",
    "checksum": "md5_hash",
    "sequence": "message_sequence_number"
  }
}
```

### 3. Server Log Structure
```json
{
  "logEntry": {
    "id": "uuid",
    "timestamp": "ISO8601",
    "level": "DEBUG|INFO|WARN|ERROR",
    "source": "component_name",
    "message": "log_message",
    "nfcData": "reference_to_nfc_data",
    "connectionType": "USB|WIFI",
    "deviceId": "android_device_identifier",
    "metadata": {
      "duration": "processing_time_ms",
      "errorCode": "error_code_if_applicable",
      "stackTrace": "error_stack_trace"
    }
  }
}
```

## Technology Stack

### 1. Android Application
- **Language**: Java/Kotlin
- **Framework**: Android SDK (API 21+)
- **NFC**: Android NFC API
- **HTTP Client**: OkHttp/Retrofit
- **USB Communication**: Android USB Host API / ADB
- **Database**: SQLite / Room
- **UI**: Material Design Components
- **Testing**: JUnit, Espresso

### 2. PC Server
- **Language**: Python 3.8+
- **Framework**: Flask/FastAPI
- **Database**: SQLite (initial) / PostgreSQL (future)
- **USB Communication**: PyUSB / ADB Python
- **Network**: requests, urllib3
- **Logging**: Python logging module
- **Configuration**: YAML/JSON config files
- **Testing**: pytest, unittest

## Security Considerations

### 1. Authentication
- API key based authentication
- Device registration and pairing
- Token expiration and renewal
- Rate limiting on API endpoints

### 2. Data Security
- TLS/SSL encryption for network communication
- Data validation on both client and server
- Input sanitization to prevent injection attacks
- Secure storage of authentication credentials

### 3. Network Security
- Firewall configuration guidelines
- Network segmentation recommendations
- VPN support for remote connections
- mDNS security considerations

## Performance Requirements

### 1. Android Application
- **NFC Read Time**: < 500ms per tag
- **Data Transmission**: < 1s per NFC data packet
- **Memory Usage**: < 50MB RAM
- **Battery Impact**: Minimal background processing
- **UI Response**: < 200ms for user interactions

### 2. PC Server
- **Request Processing**: < 100ms per API call
- **Data Logging**: < 50ms per log entry
- **Concurrent Connections**: Support up to 10 Android devices
- **Memory Usage**: < 200MB RAM
- **Storage**: Configurable log retention policies

## Scalability Considerations

### 1. Current Scope (Phase 1)
- Single PC server instance
- Basic file-based logging
- Simple SQLite database
- Up to 5 concurrent Android devices

### 2. Future Enhancements
- Multi-server support with load balancing
- Database clustering and replication
- Real-time data streaming
- Web-based management interface
- Mobile device management (MDM) integration

## Error Handling Strategy

### 1. Android Application
- Graceful NFC read failures
- Connection retry logic with exponential backoff
- Offline data caching and sync
- User-friendly error messages
- Automatic crash reporting

### 2. PC Server
- Comprehensive error logging
- Health check endpoints
- Graceful degradation under load
- Data integrity validation
- Recovery mechanisms for corrupted data

## Deployment Architecture

### 1. Development Environment
- Local development server
- Android emulator for testing
- Mock NFC data for development
- Version control with Git
- Continuous integration pipeline

### 2. Production Environment
- Standalone PC server application
- Android APK distribution
- Configuration management
- Monitoring and alerting
- Backup and recovery procedures

This architecture provides a solid foundation for the NFC Reader/Writer system while maintaining flexibility for future enhancements and ensuring robust, secure communication between Android devices and PC servers.
