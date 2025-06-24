# NFC Reader/Writer System - NFC Data Formats and Protocols

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## NFC Technology Overview

### Supported NFC Technologies
The Android NFC Reader/Writer application will support the following NFC technologies:

1. **NDEF (NFC Data Exchange Format)**
   - Primary format for structured data exchange
   - Cross-platform compatibility
   - Multiple record types support

2. **ISO14443 Type A**
   - Most common NFC tag type
   - MIFARE Classic and Ultralight support
   - High-frequency (13.56 MHz) operation

3. **ISO14443 Type B**
   - Alternative to Type A
   - Different modulation scheme
   - Compatible with certain smart cards

4. **ISO15693**
   - Vicinity cards
   - Longer read range
   - Lower data transfer rates

5. **MIFARE Classic**
   - Proprietary NXP format
   - Sector-based memory structure
   - Authentication required for read/write

6. **MIFARE Ultralight**
   - Simplified MIFARE variant
   - No authentication required
   - Limited memory capacity

## NDEF Data Format Specification

### NDEF Message Structure
```
NDEF Message = NDEF Record + [NDEF Record + ...]
```

### NDEF Record Format
```
+--------+--------+--------+--------+--------+--------+--------+--------+
| MB ME  | TNF    | Type   | Payload| ID     | Type   | ID     | Payload|
| CF SR  |        | Length | Length | Length |        |        |        |
| IL     |        |        |        |        |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
|  Flag  |  TNF   |   TL   |   PL   |   IL   |  Type  |   ID   | Payload|
|  Byte  |        |        |        |        |        |        |        |
+--------+--------+--------+--------+--------+--------+--------+--------+
```

### NDEF Record Header Flags
- **MB (Message Begin)**: First record in message
- **ME (Message End)**: Last record in message  
- **CF (Chunk Flag)**: Record is chunked
- **SR (Short Record)**: Payload length < 256 bytes
- **IL (ID Length)**: ID field present

### TNF (Type Name Format) Values
```json
{
  "tnf_values": {
    "0x00": "Empty",
    "0x01": "Well-Known Type",
    "0x02": "MIME Media Type",
    "0x03": "Absolute URI",
    "0x04": "External Type",
    "0x05": "Unknown",
    "0x06": "Unchanged",
    "0x07": "Reserved"
  }
}
```

## Well-Known NDEF Record Types

### 1. Text Record (TNF=0x01, Type="T")
**Purpose**: Store human-readable text with language information

**Payload Structure**:
```
+--------+--------+--------+--------+--------+--------+
| Status |      Language Code      |       Text       |
|  Byte  |                         |                  |
+--------+--------+--------+--------+--------+--------+
|   S    |      Lang (n bytes)     |    Text Data     |
+--------+--------+--------+--------+--------+--------+
```

**Status Byte Format**:
- Bit 7: Text Encoding (0=UTF-8, 1=UTF-16)
- Bit 6: RFU (Reserved for Future Use)
- Bits 5-0: Language Code Length

**JSON Representation**:
```json
{
  "record_type": "text",
  "tnf": 1,
  "type": "T",
  "encoding": "UTF-8",
  "language": "en",
  "text": "Hello World",
  "payload_hex": "02656e48656c6c6f20576f726c64"
}
```

### 2. URI Record (TNF=0x01, Type="U")
**Purpose**: Store Uniform Resource Identifiers

**Payload Structure**:
```
+--------+--------+--------+--------+--------+
| URI    |           URI Content            |
| ID     |                                  |
+--------+--------+--------+--------+--------+
```

**URI Identifier Prefixes**:
```json
{
  "uri_prefixes": {
    "0x00": "",
    "0x01": "http://www.",
    "0x02": "https://www.",
    "0x03": "http://",
    "0x04": "https://",
    "0x05": "tel:",
    "0x06": "mailto:",
    "0x07": "ftp://anonymous:anonymous@",
    "0x08": "ftp://ftp.",
    "0x09": "ftps://",
    "0x0A": "sftp://",
    "0x0B": "smb://",
    "0x0C": "nfs://",
    "0x0D": "ftp://",
    "0x0E": "dav://",
    "0x0F": "news:",
    "0x10": "telnet://",
    "0x11": "imap:",
    "0x12": "rtsp://",
    "0x13": "urn:",
    "0x14": "pop:",
    "0x15": "sip:",
    "0x16": "sips:",
    "0x17": "tftp:",
    "0x18": "btspp://",
    "0x19": "btl2cap://",
    "0x1A": "btgoep://",
    "0x1B": "tcpobex://",
    "0x1C": "irdaobex://",
    "0x1D": "file://",
    "0x1E": "urn:epc:id:",
    "0x1F": "urn:epc:tag:",
    "0x20": "urn:epc:pat:",
    "0x21": "urn:epc:raw:",
    "0x22": "urn:epc:",
    "0x23": "urn:nfc:"
  }
}
```

**JSON Representation**:
```json
{
  "record_type": "uri",
  "tnf": 1,
  "type": "U",
  "uri_identifier": 1,
  "uri_prefix": "http://www.",
  "uri_suffix": "example.com",
  "full_uri": "http://www.example.com",
  "payload_hex": "016578616d706c652e636f6d"
}
```

### 3. Smart Poster Record (TNF=0x01, Type="Sp")
**Purpose**: Combine URI with metadata (title, action, etc.)

**Structure**: NDEF message containing:
- Mandatory URI record
- Optional Text record(s) for title
- Optional Action record
- Optional Size record
- Optional Type record

**JSON Representation**:
```json
{
  "record_type": "smart_poster",
  "tnf": 1,
  "type": "Sp",
  "uri": "http://www.example.com",
  "titles": [
    {
      "language": "en",
      "text": "Example Website"
    }
  ],
  "action": "open",
  "size": 1024,
  "mime_type": "text/html"
}
```

### 4. MIME Media Type Record (TNF=0x02)
**Purpose**: Store data with MIME type specification

**JSON Representation**:
```json
{
  "record_type": "mime",
  "tnf": 2,
  "type": "image/jpeg",
  "payload_size": 2048,
  "payload_b64": "base64_encoded_image_data"
}
```

### 5. External Type Record (TNF=0x04)
**Purpose**: Application-specific record types

**Type Format**: `domain:type`

**JSON Representation**:
```json
{
  "record_type": "external",
  "tnf": 4,
  "type": "example.com:mydata",
  "payload_json": {
    "custom_field1": "value1",
    "custom_field2": "value2"
  }
}
```

## Raw NFC Tag Data Formats

### ISO14443A Tag Structure
```
+--------+--------+--------+--------+--------+
| UID    | BCC    | SAK    | ATQA   | Data   |
| (4-10) | (1)    | (1)    | (2)    | (var)  |
+--------+--------+--------+--------+--------+
```

### MIFARE Classic Sector Structure
```
Sector N (64 bytes for sectors 0-31, 256 bytes for sectors 32+)
+--------+--------+--------+--------+
| Block  | Block  | Block  | Sector |
|   0    |   1    |   2    | Trailer|
+--------+--------+--------+--------+
| 16 B   | 16 B   | 16 B   | 16 B   |
+--------+--------+--------+--------+
```

### MIFARE Ultralight Page Structure
```
Page Structure (4 bytes per page)
+--------+--------+--------+--------+
| Byte 0 | Byte 1 | Byte 2 | Byte 3 |
+--------+--------+--------+--------+
```

## Data Transmission Format

### Standard NFC Data Package
```json
{
  "nfc_data": {
    "id": "uuid",
    "timestamp": "ISO8601",
    "device_id": "android_device_identifier",
    "tag_info": {
      "type": "NDEF|ISO14443A|ISO14443B|ISO15693|MIFARE_CLASSIC|MIFARE_ULTRALIGHT",
      "uid": "hex_string",
      "technology": "technology_name",
      "atqa": "hex_string",
      "sak": "hex_string",
      "max_transceive_length": "integer"
    },
    "raw_data": {
      "format": "base64",
      "data": "base64_encoded_raw_bytes",
      "size": "size_in_bytes",
      "checksum": "md5_hash"
    },
    "parsed_data": {
      "format": "ndef|mifare|iso15693",
      "records": [
        {
          "type": "text|uri|smart_poster|mime|external|unknown",
          "tnf": "integer",
          "type_name": "string",
          "payload": "varies_by_type",
          "id": "optional_id",
          "metadata": {}
        }
      ]
    },
    "read_metadata": {
      "read_time_ms": "integer",
      "signal_strength": "integer",
      "read_attempts": "integer",
      "error_count": "integer",
      "location": {
        "latitude": "decimal",
        "longitude": "decimal",
        "accuracy": "decimal"
      }
    }
  }
}
```

## NFC Command and Response Protocols

### Tag Detection Protocol
```
1. NFC Adapter Enable
2. Tag Discovery Intent Filter Registration
3. Tag Detection Event
4. Technology Detection
5. Tag Connection Establishment
6. Data Reading/Writing
7. Tag Disconnection
```

### NDEF Reading Protocol
```
1. Connect to NDEF technology
2. Check if NDEF formatted
3. Check if writable
4. Read NDEF message
5. Parse NDEF records
6. Disconnect
```

### MIFARE Classic Reading Protocol
```
1. Connect to MIFARE Classic
2. Authenticate sector (if required)
3. Read block data
4. Parse data structure
5. Disconnect
```

## Error Handling and Validation

### NFC Read Errors
```json
{
  "error_types": {
    "TAG_LOST": "Tag moved away during read",
    "IO_ERROR": "Communication error with tag",
    "FORMAT_ERROR": "Invalid data format",
    "AUTHENTICATION_ERROR": "Failed to authenticate with tag",
    "UNSUPPORTED_OPERATION": "Operation not supported by tag",
    "TIMEOUT": "Read operation timed out"
  }
}
```

### Data Validation Rules
1. **UID Validation**: Check for valid hex format and length
2. **NDEF Structure**: Validate TNF, type, and payload format
3. **Checksum Verification**: MD5 hash validation
4. **Size Limits**: Maximum payload sizes per record type
5. **Character Encoding**: UTF-8/UTF-16 validation for text records

## Security Considerations

### Data Sanitization
- Remove or mask sensitive information
- Validate all input data
- Prevent injection attacks
- Secure storage of authentication keys

### Privacy Protection
- Optional location data inclusion
- Device identifier anonymization
- Secure transmission protocols
- Data retention policies

## Performance Optimization

### Reading Optimization
- Parallel technology detection
- Optimized NDEF parsing
- Caching for frequently read tags
- Background processing for large payloads

### Data Compression
- GZIP compression for large payloads
- Base64 encoding optimization
- Incremental data transmission
- Batch processing for multiple tags

## Testing Data Formats

### Test NDEF Messages
```json
{
  "test_cases": [
    {
      "name": "Simple Text Record",
      "ndef_hex": "D1010C5402656E48656C6C6F20576F726C64",
      "description": "Text record with 'Hello World' in English"
    },
    {
      "name": "URI Record",
      "ndef_hex": "D1010E5501657861706C652E636F6D",
      "description": "URI record for http://www.example.com"
    },
    {
      "name": "Smart Poster",
      "ndef_hex": "D1021553700101085302656E48656C6C6F",
      "description": "Smart poster with URI and title"
    }
  ]
}
```

## Format Extensions

### Custom Application Records
```json
{
  "custom_record": {
    "tnf": 4,
    "type": "nfcreader.app:metadata",
    "payload": {
      "version": "1.0",
      "timestamp": "ISO8601",
      "device_info": {
        "model": "device_model",
        "app_version": "app_version"
      },
      "scan_context": {
        "location": "optional_location",
        "user_notes": "optional_notes"
      }
    }
  }
}
```

This comprehensive NFC data format specification ensures consistent data handling across the entire system, from Android NFC reading to PC server storage and processing.
