# NFC Reader/Writer System - PC Server Component

## Overview
The PC Server component of the NFC Reader/Writer System provides a central data processing and storage hub for NFC data received from Android devices. It supports both USB and WiFi communication channels and provides a RESTful API for data transmission.

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Features
- HTTP API for receiving NFC data
- Database for storing and retrieving NFC records
- USB communication via ADB bridge
- WiFi communication with mDNS discovery
- Data validation and processing
- Logging and monitoring
- Security features including authentication and authorization

## Directory Structure
```
server/
├── api/              # API endpoint definitions
├── auth/             # Authentication logic
├── comm/             # Communication modules
│   ├── usb/          # USB communication code
│   └── wifi/         # WiFi communication code
├── config/           # Configuration management
├── data/             # Data processing logic
├── db/               # Database models and migrations
├── logging/          # Logging framework
├── tests/            # Test modules
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
├── utils/            # Utility functions
├── .gitignore        # Git ignore file
├── requirements.txt  # Python dependencies
├── setup.py          # Package setup script
└── README.md         # This file
```

## Setup and Installation

### Prerequisites
- Python 3.9+
- SQLite (development) / PostgreSQL (production)
- ADB (Android Debug Bridge) for USB communication

### Development Setup
1. Create virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run database migrations:
   ```
   python -m db.migrations run
   ```

5. Start development server:
   ```
   python server.py
   ```

## Testing
Run unit tests:
```
pytest tests/unit
```

Run integration tests:
```
pytest tests/integration
```

Run API tests:
```
pytest tests/api
```

You can run specific API test modules:
```
pytest tests/api/test_validators.py
pytest tests/api/test_user_routes.py
pytest tests/api/test_device_routes.py
pytest tests/api/test_connection_routes.py
```

Generate coverage report:
```
pytest --cov=./ --cov-report=html
```

## API Documentation
API documentation will be available at `/api/docs` when the server is running.

## Configuration
The server can be configured through environment variables or a `.env` file. See `.env.example` for available options.

## Coding Standards
All code must adhere to the project's Python coding standards as defined in [CODING_STANDARDS_PYTHON.md](../CODING_STANDARDS_PYTHON.md).

## License
This project is licensed under the MIT License - see the LICENSE file for details.
