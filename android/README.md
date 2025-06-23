# NFC Reader/Writer System - Android Application

## Overview
The Android application component of the NFC Reader/Writer System provides NFC tag reading and writing capabilities with connectivity to a PC server via USB or WiFi.

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Features
- NFC tag reading and writing
- USB connectivity to PC server
- WiFi connectivity with automatic discovery
- Offline data caching
- Connection failover
- User-friendly UI for scanning and data viewing
- Settings management

## Directory Structure
```
android/
├── app/
│   └── src/
│       ├── main/
│       │   ├── java/com/nfc/readwriter/
│       │   │   ├── api/           # API client code
│       │   │   ├── comm/          # Communication modules
│       │   │   │   ├── usb/       # USB communication code
│       │   │   │   └── wifi/      # WiFi communication code
│       │   │   ├── data/          # Data models and processing
│       │   │   ├── nfc/           # NFC handling code
│       │   │   ├── ui/            # UI components
│       │   │   └── utils/         # Utility functions
│       │   └── res/               # Resources
│       └── test/                  # Unit tests
├── .gitignore                     # Git ignore file
├── build.gradle                   # Build configuration
└── README.md                      # This file
```

## Setup and Development

### Prerequisites
- Android Studio 4.2+
- JDK 11+
- Android SDK (min API level 21, target API level 33)
- Android device with NFC capability or emulator with NFC support

### Setup Instructions
1. Clone the repository
2. Open the android directory in Android Studio
3. Sync Gradle files
4. Configure your device for development
5. Build and run the application

### Building the App
1. From Android Studio:
   - Build > Build Bundle(s) / APK(s) > Build APK(s)

2. From command line:
   ```
   ./gradlew assembleDebug
   ```

## Testing
Run unit tests:
```
./gradlew test
```

Run instrumented tests:
```
./gradlew connectedAndroidTest
```

Generate coverage report:
```
./gradlew createDebugCoverageReport
```

## Architecture
The application follows MVVM architecture with Clean Architecture principles:
- **UI Layer**: Activities, Fragments, ViewModels
- **Domain Layer**: Use Cases, Domain Models
- **Data Layer**: Repositories, Data Sources

## Libraries and Dependencies
- AndroidX Components
- Kotlin Coroutines
- Hilt for dependency injection
- Room for local database
- Retrofit for network communication
- Google Material Components
- JUnit, Espresso, and Mockito for testing

## NFC Compatibility
The application supports the following NFC tag types:
- NDEF tags
- NFC-A (ISO 14443-3A)
- NFC-B (ISO 14443-3B)
- NFC-F (JIS 6319-4)
- NFC-V (ISO 15693)
- ISO-DEP (ISO 14443-4)

## Coding Standards
All code must adhere to the project's Kotlin coding standards as defined in [CODING_STANDARDS_KOTLIN.md](../CODING_STANDARDS_KOTLIN.md).

## License
This project is licensed under the MIT License - see the LICENSE file for details.
