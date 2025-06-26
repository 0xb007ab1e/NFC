#!/bin/bash
set -e

# NFC Reader/Writer Android App - Release Build Script
# This script builds and signs the Android APK for production deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ANDROID_DIR="$PROJECT_ROOT/android"
BUILD_DIR="$SCRIPT_DIR/build"
VERSION_FILE="$ANDROID_DIR/app/build.gradle"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Android project exists
    if [ ! -d "$ANDROID_DIR" ]; then
        log_error "Android project directory not found: $ANDROID_DIR"
        exit 1
    fi
    
    # Check if gradlew exists
    if [ ! -f "$ANDROID_DIR/gradlew" ]; then
        log_error "Gradle wrapper not found: $ANDROID_DIR/gradlew"
        exit 1
    fi
    
    # Make gradlew executable
    chmod +x "$ANDROID_DIR/gradlew"
    
    # Check Java/JDK
    if ! command -v java &> /dev/null; then
        log_error "Java not found. Please install JDK 17+"
        exit 1
    fi
    
    # Check Android SDK
    if [ -z "$ANDROID_HOME" ] && [ -z "$ANDROID_SDK_ROOT" ]; then
        log_warning "ANDROID_HOME or ANDROID_SDK_ROOT not set. Some features may not work."
    fi
    
    log_success "Prerequisites check passed"
}

# Extract version information
get_version_info() {
    log_info "Extracting version information..."
    
    # Extract version from build.gradle
    VERSION_NAME=$(grep "versionName" "$VERSION_FILE" | sed 's/.*versionName "\(.*\)".*/\1/')
    VERSION_CODE=$(grep "versionCode" "$VERSION_FILE" | sed 's/.*versionCode \(.*\)/\1/')
    
    if [ -z "$VERSION_NAME" ] || [ -z "$VERSION_CODE" ]; then
        log_error "Could not extract version information from build.gradle"
        exit 1
    fi
    
    log_info "Version Name: $VERSION_NAME"
    log_info "Version Code: $VERSION_CODE"
}

# Clean previous builds
clean_build() {
    log_info "Cleaning previous builds..."
    
    cd "$ANDROID_DIR"
    ./gradlew clean
    
    # Create build directory
    mkdir -p "$BUILD_DIR"
    
    log_success "Build environment cleaned"
}

# Build debug APK
build_debug() {
    log_info "Building debug APK..."
    
    cd "$ANDROID_DIR"
    ./gradlew assembleDebug
    
    # Copy debug APK to build directory
    DEBUG_APK="$ANDROID_DIR/app/build/outputs/apk/debug/app-debug.apk"
    if [ -f "$DEBUG_APK" ]; then
        cp "$DEBUG_APK" "$BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-debug.apk"
        log_success "Debug APK built: $BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-debug.apk"
    else
        log_error "Debug APK not found after build"
        exit 1
    fi
}

# Build release APK
build_release() {
    log_info "Building release APK..."
    
    # Check for signing configuration
    KEYSTORE_FILE="$ANDROID_DIR/app/release.keystore"
    if [ ! -f "$KEYSTORE_FILE" ]; then
        log_warning "Release keystore not found: $KEYSTORE_FILE"
        log_warning "Building unsigned release APK"
        
        cd "$ANDROID_DIR"
        ./gradlew assembleRelease
        
        RELEASE_APK="$ANDROID_DIR/app/build/outputs/apk/release/app-release-unsigned.apk"
        if [ -f "$RELEASE_APK" ]; then
            cp "$RELEASE_APK" "$BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-release-unsigned.apk"
            log_success "Unsigned release APK built: $BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-release-unsigned.apk"
        fi
    else
        log_info "Found release keystore, building signed APK..."
        
        cd "$ANDROID_DIR"
        ./gradlew assembleRelease
        
        RELEASE_APK="$ANDROID_DIR/app/build/outputs/apk/release/app-release.apk"
        if [ -f "$RELEASE_APK" ]; then
            cp "$RELEASE_APK" "$BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-release.apk"
            log_success "Signed release APK built: $BUILD_DIR/nfc-reader-writer-${VERSION_NAME}-release.apk"
        fi
    fi
}

# Run tests
run_tests() {
    log_info "Running unit tests..."
    
    cd "$ANDROID_DIR"
    ./gradlew testDebugUnitTest
    
    # Copy test results
    TEST_RESULTS="$ANDROID_DIR/app/build/reports/tests/testDebugUnitTest"
    if [ -d "$TEST_RESULTS" ]; then
        cp -r "$TEST_RESULTS" "$BUILD_DIR/test-results"
        log_success "Test results copied to: $BUILD_DIR/test-results"
    fi
}

# Generate APK info
generate_apk_info() {
    log_info "Generating APK information..."
    
    INFO_FILE="$BUILD_DIR/build-info.txt"
    cat > "$INFO_FILE" << EOF
NFC Reader/Writer Android App - Build Information
================================================

Build Date: $(date)
Version Name: $VERSION_NAME
Version Code: $VERSION_CODE
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Unknown")
Git Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "Unknown")

Built APKs:
EOF
    
    # List built APKs
    for apk in "$BUILD_DIR"/*.apk; do
        if [ -f "$apk" ]; then
            filename=$(basename "$apk")
            filesize=$(du -h "$apk" | cut -f1)
            echo "- $filename ($filesize)" >> "$INFO_FILE"
        fi
    done
    
    log_success "Build info generated: $INFO_FILE"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --debug-only    Build debug APK only"
    echo "  -r, --release-only  Build release APK only"
    echo "  -t, --skip-tests    Skip running tests"
    echo "  -c, --clean-only    Clean build environment and exit"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Build both debug and release APKs"
    echo "  $0 --debug-only     # Build debug APK only"
    echo "  $0 --release-only   # Build release APK only"
    echo "  $0 --skip-tests     # Build APKs without running tests"
}

# Parse command line arguments
BUILD_DEBUG=true
BUILD_RELEASE=true
RUN_TESTS=true
CLEAN_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--debug-only)
            BUILD_DEBUG=true
            BUILD_RELEASE=false
            shift
            ;;
        -r|--release-only)
            BUILD_DEBUG=false
            BUILD_RELEASE=true
            shift
            ;;
        -t|--skip-tests)
            RUN_TESTS=false
            shift
            ;;
        -c|--clean-only)
            CLEAN_ONLY=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Starting NFC Android App build process..."
    
    check_prerequisites
    get_version_info
    clean_build
    
    if [ "$CLEAN_ONLY" = true ]; then
        log_success "Clean completed"
        exit 0
    fi
    
    if [ "$RUN_TESTS" = true ]; then
        run_tests
    fi
    
    if [ "$BUILD_DEBUG" = true ]; then
        build_debug
    fi
    
    if [ "$BUILD_RELEASE" = true ]; then
        build_release
    fi
    
    generate_apk_info
    
    log_success "Build process completed successfully!"
    log_info "Build artifacts available in: $BUILD_DIR"
}

# Execute main function
main "$@"
