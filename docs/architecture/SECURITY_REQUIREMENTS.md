# NFC Reader/Writer System - Security Requirements

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Security Overview

### Security Objectives
1. **Confidentiality**: Protect sensitive data from unauthorized access
2. **Integrity**: Ensure data accuracy and prevent unauthorized modification
3. **Availability**: Maintain system accessibility for authorized users
4. **Authentication**: Verify the identity of devices and users
5. **Authorization**: Control access to system resources and functions
6. **Non-repudiation**: Provide proof of data origin and delivery

### Threat Model
```
Potential Threats:
1. Man-in-the-Middle (MITM) attacks on WiFi communication
2. Eavesdropping on NFC data transmission
3. Unauthorized access to PC server
4. Malicious NFC tags with harmful payloads
5. Device impersonation and spoofing
6. Data injection and manipulation
7. Denial of Service (DoS) attacks
8. Local data extraction from compromised devices
9. Network sniffing and traffic analysis
10. Privilege escalation attempts
```

### Security Compliance Standards
- **OWASP Mobile Top 10**: Mobile application security guidelines
- **OWASP API Security Top 10**: API-specific security requirements
- **NIST Cybersecurity Framework**: Industry security standards
- **ISO 27001**: Information security management
- **GDPR Compliance**: Data protection regulations (where applicable)

## Authentication and Authorization

### 1. Device Authentication

#### API Key-Based Authentication
```json
{
  "api_key_requirements": {
    "length": 64,
    "character_set": "alphanumeric + special characters",
    "entropy": ">=128 bits",
    "generation": "cryptographically secure random",
    "format": "base64url encoding",
    "expiration": "configurable (default: 1 year)",
    "rotation": "manual and automatic rotation support"
  }
}
```

#### Device Registration Process
```
1. Initial Registration:
   - Device generates unique device ID
   - Device sends registration request with device information
   - Server validates device information
   - Server generates unique API key for device
   - API key transmitted securely to device
   - Device stores API key in encrypted storage

2. Authentication Flow:
   - Device includes API key in Authorization header
   - Server validates API key against database
   - Server checks API key expiration and status
   - Server logs authentication attempt
   - Access granted or denied based on validation
```

#### Device Identification
```json
{
  "device_id_format": {
    "method": "UUID v4 + device fingerprint",
    "components": [
      "Android device ID",
      "device model hash",
      "app installation ID",
      "hardware fingerprint hash"
    ],
    "example": "550e8400-e29b-41d4-a716-446655440000",
    "persistence": "device factory reset resistant",
    "uniqueness": "globally unique per device installation"
  }
}
```

### 2. Session Management

#### Session Security
```json
{
  "session_requirements": {
    "session_id": "UUID v4 format",
    "lifetime": "8 hours maximum",
    "idle_timeout": "30 minutes",
    "renewal": "automatic before expiration",
    "termination": "explicit logout or timeout",
    "concurrent_sessions": "1 per device maximum",
    "secure_storage": "encrypted in transit and at rest"
  }
}
```

#### Session Token Format
```
Session Token Structure:
{
  "session_id": "uuid",
  "device_id": "device_identifier", 
  "issued_at": "ISO8601_timestamp",
  "expires_at": "ISO8601_timestamp",
  "permissions": ["read", "write", "admin"],
  "ip_address": "client_ip_hash",
  "signature": "HMAC_SHA256_signature"
}
```

### 3. Authorization Model

#### Role-Based Access Control (RBAC)
```json
{
  "roles": {
    "device": {
      "permissions": [
        "nfc:submit",
        "nfc:read_own", 
        "device:update_own",
        "connection:heartbeat"
      ],
      "restrictions": [
        "cannot access other device data",
        "cannot modify server configuration",
        "cannot access admin endpoints"
      ]
    },
    "admin": {
      "permissions": [
        "device:manage_all",
        "nfc:read_all",
        "logs:read_all",
        "config:modify",
        "system:status"
      ],
      "restrictions": [
        "cannot impersonate devices",
        "actions are fully logged"
      ]
    }
  }
}
```

#### Permission Validation
```python
def validate_permission(session, required_permission, resource_id=None):
    """
    Validate if session has required permission for resource
    """
    # 1. Verify session is valid and not expired
    if not is_session_valid(session):
        raise AuthenticationError("Invalid or expired session")
    
    # 2. Check if user has required permission
    if not has_permission(session.user_id, required_permission):
        raise AuthorizationError("Insufficient permissions")
    
    # 3. For resource-specific permissions, verify ownership
    if resource_id and not can_access_resource(session.user_id, resource_id):
        raise AuthorizationError("Cannot access resource")
    
    return True
```

## Data Protection

### 1. Encryption Requirements

#### Data in Transit
```json
{
  "transport_encryption": {
    "wifi_communication": {
      "protocol": "TLS 1.3 (minimum TLS 1.2)",
      "cipher_suites": [
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_128_GCM_SHA256"
      ],
      "certificate_validation": "strict",
      "hsts_enabled": true,
      "perfect_forward_secrecy": true
    },
    "usb_communication": {
      "protocol": "Application-level encryption",
      "algorithm": "AES-256-GCM",
      "key_exchange": "ECDH-P256",
      "authentication": "HMAC-SHA256"
    }
  }
}
```

#### Data at Rest
```json
{
  "storage_encryption": {
    "android_device": {
      "api_keys": "Android Keystore (hardware-backed)",
      "cached_data": "AES-256-GCM with device key",
      "configuration": "AES-256-GCM with app key",
      "logs": "AES-256-GCM with app key"
    },
    "pc_server": {
      "database": "SQLCipher with AES-256",
      "configuration_files": "AES-256-GCM with system key",
      "log_files": "AES-256-GCM with system key",
      "api_keys": "bcrypt hashing + salt"
    }
  }
}
```

#### Key Management
```json
{
  "key_management": {
    "generation": "Hardware Security Module (HSM) when available",
    "storage": "Android Keystore / OS-specific secure storage",
    "rotation": "Annual rotation with graceful transition",
    "derivation": "PBKDF2 with 100,000 iterations minimum",
    "backup": "Encrypted backup with separate key escrow",
    "destruction": "Secure deletion with cryptographic erasure"
  }
}
```

### 2. Data Sanitization

#### Input Validation
```python
class InputValidator:
    """Comprehensive input validation for security"""
    
    @staticmethod
    def validate_nfc_data(nfc_data):
        """Validate NFC data structure and content"""
        # 1. Schema validation
        if not validate_json_schema(nfc_data, NFC_DATA_SCHEMA):
            raise ValidationError("Invalid NFC data schema")
        
        # 2. Size limits
        if len(nfc_data.get('raw_data', '')) > MAX_NFC_PAYLOAD_SIZE:
            raise ValidationError("NFC payload exceeds size limit")
        
        # 3. Character encoding validation
        if not is_valid_utf8(nfc_data.get('parsed_data', {})):
            raise ValidationError("Invalid character encoding")
        
        # 4. Malicious content detection
        if contains_suspicious_patterns(nfc_data):
            raise SecurityError("Potentially malicious content detected")
        
        return True
    
    @staticmethod
    def sanitize_string(input_string, max_length=1000):
        """Sanitize string input to prevent injection attacks"""
        if not input_string:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_string)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        # HTML encode special characters
        sanitized = html.escape(sanitized)
        
        return sanitized
```

#### SQL Injection Prevention
```python
# Always use parameterized queries
def get_device_by_id(device_id):
    """Secure database query using parameterized statements"""
    query = "SELECT * FROM devices WHERE id = ?"
    return db.execute(query, (device_id,)).fetchone()

# Input validation for all database operations
def validate_device_id(device_id):
    """Validate device ID format"""
    if not re.match(r'^[a-f0-9\-]{36}$', device_id):
        raise ValidationError("Invalid device ID format")
    return device_id
```

### 3. Privacy Protection

#### Data Minimization
```json
{
  "data_collection": {
    "principle": "collect only necessary data",
    "location_data": "optional, user-configurable",
    "device_info": "essential for functionality only",
    "user_identification": "device-based, not personal",
    "retention_policy": "configurable with default limits"
  }
}
```

#### Anonymization Techniques
```python
def anonymize_device_data(device_data):
    """Anonymize sensitive device information"""
    return {
        "device_id_hash": hash_device_id(device_data["device_id"]),
        "model_category": categorize_device_model(device_data["model"]),
        "android_version_major": extract_major_version(device_data["android_version"]),
        "location_region": get_approximate_region(device_data.get("location")),
        "timestamp_rounded": round_timestamp(device_data["timestamp"], minutes=10)
    }
```

## Network Security

### 1. WiFi Communication Security

#### TLS Configuration
```python
# Secure TLS configuration for WiFi communication
TLS_CONFIG = {
    'min_version': ssl.TLSVersion.TLSv1_2,
    'max_version': ssl.TLSVersion.TLSv1_3,
    'ciphers': [
        'ECDHE-RSA-AES256-GCM-SHA384',
        'ECDHE-RSA-AES128-GCM-SHA256',
        'ECDHE-RSA-CHACHA20-POLY1305'
    ],
    'verify_mode': ssl.CERT_REQUIRED,
    'check_hostname': True,
    'options': ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
}
```

#### Certificate Management
```json
{
  "certificate_requirements": {
    "ca_validation": "strict certificate chain validation",
    "hostname_verification": "mandatory",
    "certificate_pinning": "optional for enhanced security",
    "self_signed_certs": "rejected by default",
    "expired_certs": "automatic rejection",
    "revocation_checking": "OCSP where available"
  }
}
```

#### Request Signing
```python
def sign_request(method, url, timestamp, body, secret_key):
    """Sign API requests to prevent tampering"""
    message = f"{method}\n{url}\n{timestamp}\n{body}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

def verify_request_signature(request, secret_key):
    """Verify request signature to ensure integrity"""
    timestamp = request.headers.get('X-Timestamp')
    signature = request.headers.get('X-Signature')
    
    # Check timestamp freshness (within 5 minutes)
    if abs(time.time() - int(timestamp)) > 300:
        raise SecurityError("Request timestamp too old")
    
    # Recalculate signature
    expected_signature = sign_request(
        request.method,
        request.url,
        timestamp,
        request.body,
        secret_key
    )
    
    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(signature, expected_signature):
        raise SecurityError("Invalid request signature")
```

### 2. USB Communication Security

#### ADB Security
```json
{
  "adb_security": {
    "authentication": "RSA key-based device authorization",
    "encryption": "AES-256 session encryption",
    "device_verification": "device fingerprint validation",
    "connection_monitoring": "detect unauthorized connections",
    "session_timeout": "automatic timeout after inactivity"
  }
}
```

#### USB Protocol Security
```python
class SecureUSBProtocol:
    """Secure USB communication protocol implementation"""
    
    def __init__(self):
        self.session_key = None
        self.sequence_number = 0
    
    def establish_secure_session(self, device_public_key):
        """Establish encrypted session over USB"""
        # 1. Generate ephemeral key pair
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_key = private_key.public_key()
        
        # 2. Perform ECDH key exchange
        shared_key = private_key.exchange(ec.ECDH(), device_public_key)
        
        # 3. Derive session key using HKDF
        self.session_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'usb_session_key'
        ).derive(shared_key)
        
        return public_key
    
    def encrypt_message(self, plaintext):
        """Encrypt message with session key"""
        if not self.session_key:
            raise SecurityError("Session not established")
        
        # Use AES-GCM for authenticated encryption
        cipher = Cipher(
            algorithms.AES(self.session_key),
            modes.GCM(os.urandom(12))
        )
        encryptor = cipher.encryptor()
        
        # Include sequence number to prevent replay attacks
        data = struct.pack('<Q', self.sequence_number) + plaintext.encode()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        self.sequence_number += 1
        
        return {
            'ciphertext': ciphertext,
            'nonce': cipher.mode.nonce,
            'tag': encryptor.tag
        }
```

## Application Security

### 1. Android Application Security

#### Code Protection
```json
{
  "code_security": {
    "obfuscation": "ProGuard/R8 code obfuscation enabled",
    "anti_debugging": "detection of debugging attempts",
    "root_detection": "detection of rooted devices",
    "tamper_detection": "app signature verification",
    "runtime_protection": "detect hooking and injection",
    "ssl_pinning": "prevent MITM attacks"
  }
}
```

#### Secure Storage Implementation
```kotlin
class SecureStorage(private val context: Context) {
    private val keyAlias = "nfc_reader_key"
    
    init {
        generateOrRetrieveKey()
    }
    
    private fun generateOrRetrieveKey() {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        
        val keyGenParameterSpec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
        .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
        .setUserAuthenticationRequired(false)
        .setRandomizedEncryptionRequired(true)
        .build()
        
        keyGenerator.init(keyGenParameterSpec)
        keyGenerator.generateKey()
    }
    
    fun encryptData(data: String): String {
        val keyStore = KeyStore.getInstance("AndroidKeyStore")
        keyStore.load(null)
        
        val secretKey = keyStore.getKey(keyAlias, null) as SecretKey
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)
        
        val encryptedData = cipher.doFinal(data.toByteArray())
        val iv = cipher.iv
        
        // Combine IV and encrypted data
        val combined = iv + encryptedData
        return Base64.encodeToString(combined, Base64.DEFAULT)
    }
}
```

#### Permission Management
```xml
<!-- Minimum required permissions -->
<uses-permission android:name="android.permission.NFC" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<!-- Optional permissions (user-configurable) -->
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" 
                 android:required="false" />

<!-- Prevent installation on devices without NFC -->
<uses-feature android:name="android.hardware.nfc" 
              android:required="true" />
```

### 2. PC Server Security

#### Server Hardening
```json
{
  "server_security": {
    "process_isolation": "run with minimal privileges",
    "file_permissions": "restrictive file system permissions", 
    "network_binding": "bind to specific interfaces only",
    "resource_limits": "CPU and memory usage limits",
    "logging": "comprehensive security event logging",
    "monitoring": "real-time security monitoring"
  }
}
```

#### Input Validation Framework
```python
from marshmallow import Schema, fields, validate, ValidationError

class NFCDataSchema(Schema):
    """Schema for validating NFC data input"""
    id = fields.UUID(required=True)
    timestamp = fields.DateTime(required=True)
    device_id = fields.Str(required=True, validate=validate.Length(max=100))
    tag_type = fields.Str(required=True, validate=validate.OneOf([
        'NDEF', 'ISO14443A', 'ISO14443B', 'ISO15693', 
        'MIFARE_CLASSIC', 'MIFARE_ULTRALIGHT'
    ]))
    raw_data = fields.Str(required=True, validate=validate.Length(max=1048576))
    
    @validates('raw_data')
    def validate_base64(self, value):
        try:
            base64.b64decode(value, validate=True)
        except Exception:
            raise ValidationError('Invalid base64 encoding')

def validate_nfc_request(request_data):
    """Validate incoming NFC data request"""
    schema = NFCDataSchema()
    try:
        validated_data = schema.load(request_data)
        return validated_data
    except ValidationError as err:
        raise SecurityError(f"Validation failed: {err.messages}")
```

## Security Monitoring and Logging

### 1. Security Event Logging

#### Log Categories
```json
{
  "security_logs": {
    "authentication": {
      "events": ["login_success", "login_failure", "api_key_usage"],
      "data": ["device_id", "ip_address", "timestamp", "result"],
      "retention": "1 year"
    },
    "authorization": {
      "events": ["permission_denied", "privilege_escalation_attempt"],
      "data": ["device_id", "requested_resource", "permission_required"],
      "retention": "1 year"
    },
    "data_access": {
      "events": ["nfc_data_submitted", "data_retrieved", "data_modified"],
      "data": ["device_id", "data_id", "operation", "timestamp"],
      "retention": "90 days"
    },
    "security_incidents": {
      "events": ["malicious_input", "injection_attempt", "unusual_activity"],
      "data": ["full_request", "source_ip", "detection_method"],
      "retention": "2 years"
    }
  }
}
```

#### Security Logging Implementation
```python
import logging
from datetime import datetime
import json

class SecurityLogger:
    """Dedicated security event logger"""
    
    def __init__(self):
        self.logger = logging.getLogger('security')
        handler = logging.FileHandler('/var/log/nfc-reader/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_authentication_event(self, device_id, event_type, result, ip_address=None):
        """Log authentication-related events"""
        event = {
            'event_type': 'authentication',
            'sub_type': event_type,
            'device_id': device_id,
            'result': result,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.info(json.dumps(event))
    
    def log_security_incident(self, incident_type, details, severity='medium'):
        """Log security incidents and threats"""
        event = {
            'event_type': 'security_incident',
            'incident_type': incident_type,
            'severity': severity,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.logger.warning(json.dumps(event))
```

### 2. Intrusion Detection

#### Anomaly Detection
```python
class AnomalyDetector:
    """Detect unusual patterns in system usage"""
    
    def __init__(self):
        self.device_baselines = {}
        self.global_thresholds = {
            'requests_per_minute': 100,
            'failed_auth_per_hour': 10,
            'large_payload_threshold': 100000
        }
    
    def check_request_rate(self, device_id, current_rate):
        """Check if request rate is anomalous"""
        baseline = self.device_baselines.get(device_id, {})
        normal_rate = baseline.get('avg_requests_per_minute', 10)
        
        if current_rate > normal_rate * 5:  # 5x normal rate
            return {
                'anomaly': True,
                'type': 'unusual_request_rate',
                'severity': 'high',
                'current_rate': current_rate,
                'baseline_rate': normal_rate
            }
        
        return {'anomaly': False}
    
    def detect_suspicious_patterns(self, request_data):
        """Detect patterns that might indicate attacks"""
        suspicious_indicators = []
        
        # Check for SQL injection patterns
        sql_patterns = [
            r"union\s+select", r"drop\s+table", r"insert\s+into",
            r"delete\s+from", r"update\s+.*set", r"exec\s*\("
        ]
        
        request_str = json.dumps(request_data).lower()
        for pattern in sql_patterns:
            if re.search(pattern, request_str, re.IGNORECASE):
                suspicious_indicators.append(f"SQL injection pattern: {pattern}")
        
        # Check for XSS patterns
        xss_patterns = [r"<script", r"javascript:", r"onload=", r"onerror="]
        for pattern in xss_patterns:
            if re.search(pattern, request_str, re.IGNORECASE):
                suspicious_indicators.append(f"XSS pattern: {pattern}")
        
        return suspicious_indicators
```

### 3. Rate Limiting and DDoS Protection

#### Rate Limiting Implementation
```python
from collections import defaultdict
from time import time
import threading

class RateLimiter:
    """Token bucket rate limiter for API protection"""
    
    def __init__(self):
        self.buckets = defaultdict(dict)
        self.lock = threading.Lock()
        
        # Rate limiting rules
        self.limits = {
            'global': {'requests': 1000, 'window': 3600},     # 1000/hour globally
            'device': {'requests': 100, 'window': 3600},      # 100/hour per device
            'endpoint': {
                '/api/v1/nfc/data': {'requests': 60, 'window': 60},  # 60/minute for data submission
                '/api/v1/devices/register': {'requests': 5, 'window': 3600}  # 5/hour for registration
            }
        }
    
    def is_allowed(self, identifier, limit_type, endpoint=None):
        """Check if request is allowed under rate limits"""
        with self.lock:
            now = time()
            
            # Get appropriate limit
            if limit_type == 'endpoint' and endpoint:
                limit_config = self.limits['endpoint'].get(endpoint, 
                                                         self.limits['device'])
            else:
                limit_config = self.limits[limit_type]
            
            bucket = self.buckets[identifier]
            window_start = now - limit_config['window']
            
            # Remove old requests outside the window
            bucket['requests'] = [req_time for req_time in bucket.get('requests', []) 
                                if req_time > window_start]
            
            # Check if under limit
            if len(bucket['requests']) < limit_config['requests']:
                bucket['requests'].append(now)
                return True
            
            return False
    
    def get_retry_after(self, identifier, limit_type):
        """Get seconds until rate limit resets"""
        bucket = self.buckets.get(identifier, {})
        if not bucket.get('requests'):
            return 0
        
        limit_config = self.limits[limit_type]
        oldest_request = min(bucket['requests'])
        return max(0, limit_config['window'] - (time() - oldest_request))
```

## Incident Response

### 1. Security Incident Classification

#### Severity Levels
```json
{
  "incident_severity": {
    "critical": {
      "description": "Immediate threat to system integrity or data",
      "examples": ["successful data breach", "system compromise", "malware detection"],
      "response_time": "immediate (< 15 minutes)",
      "notification": "automatic alerts + manual escalation"
    },
    "high": {
      "description": "Significant security threat requiring urgent attention",
      "examples": ["failed authentication attacks", "privilege escalation attempts"],
      "response_time": "< 1 hour",
      "notification": "automatic alerts"
    },
    "medium": {
      "description": "Security concern requiring investigation",
      "examples": ["unusual usage patterns", "minor policy violations"],
      "response_time": "< 4 hours",
      "notification": "logged for review"
    },
    "low": {
      "description": "Minor security event for tracking purposes",
      "examples": ["configuration changes", "normal failed authentications"],
      "response_time": "< 24 hours",
      "notification": "logged only"
    }
  }
}
```

### 2. Automated Response Actions

#### Automatic Mitigation
```python
class SecurityResponseSystem:
    """Automated security incident response"""
    
    def __init__(self, logger, rate_limiter):
        self.logger = logger
        self.rate_limiter = rate_limiter
        self.blocked_devices = set()
        self.temp_blocks = {}
    
    def handle_security_incident(self, incident):
        """Process security incident and take appropriate action"""
        severity = incident.get('severity', 'low')
        incident_type = incident.get('type')
        device_id = incident.get('device_id')
        
        if severity == 'critical':
            self._handle_critical_incident(incident)
        elif severity == 'high':
            self._handle_high_incident(incident)
        elif incident_type in ['brute_force', 'rate_limit_exceeded']:
            self._handle_abuse_incident(device_id, incident)
    
    def _handle_critical_incident(self, incident):
        """Handle critical security incidents"""
        # Block device immediately
        device_id = incident.get('device_id')
        if device_id:
            self.block_device(device_id, permanent=True)
        
        # Log with high priority
        self.logger.log_security_incident(
            'critical_incident_auto_block',
            incident,
            severity='critical'
        )
        
        # Send immediate notification (implementation depends on notification system)
        self._send_emergency_notification(incident)
    
    def _handle_abuse_incident(self, device_id, incident):
        """Handle suspected abuse or attacks"""
        if device_id:
            # Temporary block for 1 hour
            self.temp_block_device(device_id, duration=3600)
            
            self.logger.log_security_incident(
                'device_temporarily_blocked',
                {
                    'device_id': device_id,
                    'reason': incident.get('type'),
                    'duration': 3600
                },
                severity='medium'
            )
    
    def block_device(self, device_id, permanent=False):
        """Block device from accessing the system"""
        if permanent:
            self.blocked_devices.add(device_id)
            # Update database to mark device as blocked
            self._update_device_status(device_id, 'blocked')
        else:
            self.temp_blocks[device_id] = time.time() + 3600  # 1 hour
    
    def is_device_blocked(self, device_id):
        """Check if device is currently blocked"""
        # Check permanent blocks
        if device_id in self.blocked_devices:
            return True
        
        # Check temporary blocks
        if device_id in self.temp_blocks:
            if time.time() < self.temp_blocks[device_id]:
                return True
            else:
                # Remove expired temporary block
                del self.temp_blocks[device_id]
        
        return False
```

This comprehensive security requirements document establishes a robust security framework for the NFC Reader/Writer system, addressing all major security concerns from authentication and data protection to incident response and monitoring.
