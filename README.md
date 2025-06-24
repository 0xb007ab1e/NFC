# NFC Reader/Writer System

[![Python CI](https://github.com/0xb007ab1e/NFC/actions/workflows/python-ci.yml/badge.svg)](https://github.com/0xb007ab1e/NFC/actions/workflows/python-ci.yml)
[![Android CI](https://github.com/0xb007ab1e/NFC/actions/workflows/android-ci.yml/badge.svg)](https://github.com/0xb007ab1e/NFC/actions/workflows/android-ci.yml)

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Project Overview

The NFC Reader/Writer System is a comprehensive solution that connects an Android application to a PC server, allowing NFC data to be scanned by the mobile device and transmitted to the server for logging and processing. The system supports both USB and WiFi connectivity, with automatic failover between connection types.

### Key Features

- **NFC Reading**: Scan and parse multiple NFC tag types
- **Dual Connectivity**: USB and WiFi communication options
- **Secure Data Transmission**: Encrypted data transfer between app and server
- **Offline Mode**: Local caching with synchronization when connection is restored
- **Real-time Logging**: Comprehensive data logging on the PC server
- **User-friendly Interface**: Intuitive mobile app with real-time status updates

## Project Documentation

### Planning and Design Documents

1. [**Project Overview**](PROJECT_OVERVIEW.md): High-level description of system goals and components
2. [**Progress Tracker**](PROGRESS_TRACKER.md): Task management and project status tracking
3. [**System Architecture**](SYSTEM_ARCHITECTURE.md): Detailed technical architecture and component design
4. [**API Specifications**](API_SPECIFICATIONS.md): Complete REST API design for app-server communication
5. [**Database Schema**](DATABASE_SCHEMA.md): Database structure for data storage
6. [**NFC Data Formats**](NFC_DATA_FORMATS.md): Specifications for NFC data parsing and handling
7. [**Android UI Mockups**](ANDROID_UI_MOCKUPS.md): Mobile app UI/UX design and component specifications
8. [**Communication Protocols**](COMMUNICATION_PROTOCOLS.md): USB and WiFi communication protocols
9. [**Testing Strategy**](TESTING_STRATEGY.md): Comprehensive testing approach for all components
10. [**Security Requirements**](SECURITY_REQUIREMENTS.md): Security specifications and threat mitigations
11. [**Implementation Timeline**](IMPLEMENTATION_TIMELINE.md): Project schedule and resource allocation

### Project Structure

```
NFC/
├── README.md                     # This file
├── PROJECT_OVERVIEW.md           # High-level system description
├── PROGRESS_TRACKER.md           # Task management and status
├── SYSTEM_ARCHITECTURE.md        # Technical architecture design
├── API_SPECIFICATIONS.md         # REST API documentation
├── DATABASE_SCHEMA.md            # Database structure
├── NFC_DATA_FORMATS.md           # NFC data specifications
├── ANDROID_UI_MOCKUPS.md         # Mobile app UI design
├── COMMUNICATION_PROTOCOLS.md    # USB and WiFi protocols
├── TESTING_STRATEGY.md           # Testing methodology
├── SECURITY_REQUIREMENTS.md      # Security specifications
└── IMPLEMENTATION_TIMELINE.md    # Project schedule
```

## Project Status

**Current Phase**: Transitioning from Phase 0 (Design and Planning) to Phase 1 (PC Server Development)

The project has completed the design and planning phase. All design documents have been finalized and approved. The repository structure is being set up, and the project is preparing to begin implementation of the PC Server component.

## ⚠️ Important Security Notice

**DO NOT COMMIT `.p1d` FILES TO THIS REPOSITORY**

These files contain proprietary authentication information and are extremely sensitive. We have implemented multiple safeguards to prevent these files from being committed:

1. Added patterns to `.gitignore` files
2. Installed Git pre-commit hooks to block sensitive files

New contributors MUST run the Git hooks installation script before contributing:
```bash
bash tools/install_git_hooks.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

See the [Progress Tracker](PROGRESS_TRACKER.md) for detailed status information.

## Getting Started

### Prerequisites

**This project is currently in the design phase. Development has not yet begun.**

The following will be required once development starts:

#### For PC Server Development:
- Python 3.8+
- Flask/FastAPI
- SQLite/PostgreSQL
- ADB (Android Debug Bridge)

#### For Android Development:
- Android Studio
- Android SDK (API Level 21+)
- NFC-enabled Android device

### Future Setup Instructions

Development setup instructions will be provided once the implementation phase begins. These will include:

1. Server environment setup
2. Android development environment configuration 
3. Database initialization
4. Testing environment setup

## Timeline

- **Phase 0: Design and Planning** - Weeks 1-2 (**Current**)
- **Phase 1: PC Server Development** - Weeks 3-5
- **Phase 2: Android Application Development** - Weeks 6-9
- **Phase 3: Integration and Testing** - Weeks 10-11
- **Phase 4: Documentation and Deployment** - Week 12

## Contact and Contributors

Project maintained according to the implementation timeline and project specifications.
