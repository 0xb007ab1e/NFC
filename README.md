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

## Documentation

#### Architecture
1. [**System Architecture**](docs/architecture/SYSTEM_ARCHITECTURE.md): Detailed technical architecture and component design
2. [**API Specifications**](docs/architecture/API_SPECIFICATIONS.md): Complete REST API design for app-server communication
3. [**Database Schema**](docs/architecture/DATABASE_SCHEMA.md): Database structure for data storage
4. [**NFC Data Formats**](docs/architecture/NFC_DATA_FORMATS.md): Specifications for NFC data parsing and handling
5. [**Android UI Mockups**](docs/architecture/ANDROID_UI_MOCKUPS.md): Mobile app UI/UX design and component specifications
6. [**Communication Protocols**](docs/architecture/COMMUNICATION_PROTOCOLS.md): USB and WiFi communication protocols
7. [**Security Requirements**](docs/architecture/SECURITY_REQUIREMENTS.md): Security specifications and threat mitigations

#### Planning
1. [**Project Overview**](docs/planning/PROJECT_OVERVIEW.md): High-level description of system goals and components
2. [**Progress Tracker**](docs/planning/PROGRESS_TRACKER.md): Task management and project status tracking
3. [**Implementation Timeline**](docs/planning/IMPLEMENTATION_TIMELINE.md): Project schedule and resource allocation
4. [**Work Breakdown Structure**](docs/planning/WORK_BREAKDOWN_STRUCTURE.md): Detailed task breakdown
5. [**Implementation Checklist**](docs/planning/IMPLEMENTATION_CHECKLIST.md): Requirements verification
6. [**Phase Completion & Planning**](docs/planning/PHASE0_COMPLETION.md): Phase milestones and next steps

#### Standards & Guidelines
1. [**Python Coding Standards**](docs/standards/CODING_STANDARDS_PYTHON.md): Coding conventions for server code
2. [**Kotlin Coding Standards**](docs/standards/CODING_STANDARDS_KOTLIN.md): Coding conventions for Android app
3. [**Testing Strategy**](docs/standards/TESTING_STRATEGY.md): Comprehensive testing approach for all components
4. [**Version Control Setup**](docs/standards/VERSION_CONTROL_SETUP.md): Git workflow and practices

#### Development
1. [**Development Log**](docs/development/DEVELOPMENT_LOG.md): Progress and decision records
2. [**Dependency Management**](docs/development/DEPENDENCY_MANAGEMENT.md): External libraries and tools
3. [**CI/CD Status**](docs/CI_CD_STATUS.md): Continuous Integration/Deployment status
4. [**Server Development Setup**](docs/SERVER_DEVELOPMENT_SETUP.md): Environment setup for server development

### Project Structure

```
NFC/
├── README.md                     # This file
├── CONTRIBUTING.md               # Contribution guidelines
├── server/                       # Server component source code
├── android/                      # Android app source code
├── tools/                        # Development tools and scripts
├── docs/                         # Documentation
│   ├── architecture/             # System architecture documents
│   ├── planning/                 # Project planning documents
│   ├── standards/                # Coding standards and guidelines
│   ├── development/              # Development documents
│   ├── CI_CD_STATUS.md           # CI/CD pipeline status
│   ├── BRANCH_PROTECTION_SETUP.md # Branch protection configuration
│   ├── MANUAL_WORKFLOW_TRIGGER.md # CI/CD workflow manual trigger guide
│   └── SERVER_DEVELOPMENT_SETUP.md # Server setup instructions
└── .github/                      # GitHub configuration and workflows
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

See the [Progress Tracker](docs/planning/PROGRESS_TRACKER.md) for detailed status information.

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
