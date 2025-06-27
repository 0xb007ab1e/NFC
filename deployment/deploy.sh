#!/bin/bash
set -e

# NFC Reader/Writer System - Deployment Manager
# This script provides a unified interface for deploying the NFC system

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${CYAN}$1${NC}"
}

# Show banner
show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
╔═══════════════════════════════════════════════════════════╗
║                NFC Reader/Writer System                   ║
║                  Deployment Manager                       ║
║                      v0.1.0-alpha                         ║
╚═══════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Show usage
show_usage() {
    show_banner
    echo "Usage: $0 <deployment-type> [options]"
    echo ""
    echo "Deployment Types:"
    echo "  docker              Deploy using Docker Compose"
    echo "  kubernetes          Deploy to Kubernetes cluster"
    echo "  systemd             Install as systemd service"
    echo "  android-debug       Build Android debug APK"
    echo "  android-release     Build Android release APK"
    echo ""
    echo "Docker Options:"
    echo "  --dev               Use development configuration"
    echo "  --prod              Use production configuration"
    echo "  --build             Force rebuild of containers"
    echo "  --logs              Show container logs after deployment"
    echo ""
    echo "Kubernetes Options:"
    echo "  --namespace NAME    Kubernetes namespace (default: nfc-system)"
    echo "  --context NAME      Kubernetes context to use"
    echo "  --dry-run           Show what would be deployed without applying"
    echo ""
    echo "Systemd Options:"
    echo "  --user USER         Service user (default: nfc)"
    echo "  --install-dir DIR   Installation directory (default: /opt/nfc-server)"
    echo ""
    echo "Android Options:"
    echo "  --clean             Clean build before compiling"
    echo "  --tests             Run tests before building"
    echo ""
    echo "Global Options:"
    echo "  --help              Show this help message"
    echo "  --version           Show version information"
    echo ""
    echo "Examples:"
    echo "  $0 docker --dev --logs"
    echo "  $0 kubernetes --namespace production --context prod-cluster"
    echo "  $0 systemd"
    echo "  $0 android-release --clean"
}

# Show version
show_version() {
    log_info "NFC Reader/Writer System Deployment Manager"
    log_info "Version: 0.1.0-alpha"
    log_info "Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "Unknown")"
    log_info "Build Date: $(date)"
}

# Docker deployment
deploy_docker() {
    local env_type="dev"
    local build_flag=""
    local show_logs=false
    
    # Parse Docker-specific options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                env_type="dev"
                shift
                ;;
            --prod)
                env_type="prod"
                shift
                ;;
            --build)
                build_flag="--build"
                shift
                ;;
            --logs)
                show_logs=true
                shift
                ;;
            *)
                log_error "Unknown Docker option: $1"
                exit 1
                ;;
        esac
    done
    
    log_header "Deploying with Docker Compose ($env_type environment)"
    
    cd "$SCRIPT_DIR/docker"
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_warning ".env file not found, copying from .env.example"
        cp .env.example .env
        log_warning "Please edit .env file with your configuration"
    fi
    
    # Deploy
    if [ "$env_type" = "prod" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d $build_flag
    else
        docker-compose up -d $build_flag
    fi
    
    log_success "Docker deployment completed"
    
    # Show logs if requested
    if [ "$show_logs" = true ]; then
        log_info "Showing container logs (Ctrl+C to exit)..."
        docker-compose logs -f
    fi
    
    # Show status
    echo ""
    log_info "Container status:"
    docker-compose ps
    echo ""
    log_info "Access the API at: http://localhost:8000"
    log_info "Access Grafana at: http://localhost:3000 (admin/admin)"
}

# Kubernetes deployment
deploy_kubernetes() {
    local namespace="nfc-system"
    local context=""
    local dry_run=false
    
    # Parse Kubernetes-specific options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --namespace)
                namespace="$2"
                shift 2
                ;;
            --context)
                context="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            *)
                log_error "Unknown Kubernetes option: $1"
                exit 1
                ;;
        esac
    done
    
    log_header "Deploying to Kubernetes (namespace: $namespace)"
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl not found. Please install kubectl"
        exit 1
    fi
    
    # Set context if provided
    if [ -n "$context" ]; then
        kubectl config use-context "$context"
        log_info "Using Kubernetes context: $context"
    fi
    
    cd "$SCRIPT_DIR/kubernetes"
    
    # Apply manifests
    local kubectl_args=""
    if [ "$dry_run" = true ]; then
        kubectl_args="--dry-run=client"
        log_info "Dry run mode - showing what would be deployed:"
    fi
    
    for manifest in manifests/*.yaml; do
        log_info "Applying: $(basename "$manifest")"
        kubectl apply -f "$manifest" $kubectl_args
    done
    
    if [ "$dry_run" = false ]; then
        log_success "Kubernetes deployment completed"
        
        # Wait for deployment
        log_info "Waiting for deployment to be ready..."
        kubectl wait --for=condition=available --timeout=300s deployment/nfc-server -n "$namespace"
        
        # Show status
        echo ""
        log_info "Pod status:"
        kubectl get pods -n "$namespace"
        echo ""
        log_info "Service status:"
        kubectl get services -n "$namespace"
    fi
}

# Systemd deployment
deploy_systemd() {
    local user="nfc"
    local install_dir="/opt/nfc-server"
    
    # Parse systemd-specific options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --user)
                user="$2"
                shift 2
                ;;
            --install-dir)
                install_dir="$2"
                shift 2
                ;;
            *)
                log_error "Unknown systemd option: $1"
                exit 1
                ;;
        esac
    done
    
    log_header "Installing as systemd service"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        log_error "Systemd installation requires root privileges"
        log_info "Please run: sudo $0 systemd"
        exit 1
    fi
    
    # Run installation script
    "$SCRIPT_DIR/systemd/install.sh"
    
    log_success "Systemd service installation completed"
}

# Android build
build_android() {
    local build_type="$1"
    local clean_build=false
    local run_tests=true
    
    # Parse Android-specific options
    shift  # Remove build_type from arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --clean)
                clean_build=true
                shift
                ;;
            --tests)
                run_tests=true
                shift
                ;;
            --no-tests)
                run_tests=false
                shift
                ;;
            *)
                log_error "Unknown Android option: $1"
                exit 1
                ;;
        esac
    done
    
    log_header "Building Android APK ($build_type)"
    
    # Prepare build arguments
    local build_args=""
    if [ "$build_type" = "debug" ]; then
        build_args="--debug-only"
    elif [ "$build_type" = "release" ]; then
        build_args="--release-only"
    fi
    
    if [ "$clean_build" = true ]; then
        build_args="$build_args --clean-only"
        log_info "Cleaning build environment..."
        "$SCRIPT_DIR/android/build-release.sh" --clean-only
    fi
    
    if [ "$run_tests" = false ]; then
        build_args="$build_args --skip-tests"
    fi
    
    # Run build
    "$SCRIPT_DIR/android/build-release.sh" $build_args
    
    log_success "Android build completed"
    
    # Show build artifacts
    echo ""
    log_info "Build artifacts:"
    ls -la "$SCRIPT_DIR/android/build/"*.apk 2>/dev/null || log_warning "No APK files found"
}

# Health check
health_check() {
    log_header "Running deployment health checks"
    
    # Check if any services are running
    local services_found=false
    
    # Check Docker
    if command -v docker &> /dev/null && docker ps --format "table {{.Names}}" | grep -q nfc; then
        log_info "Docker containers found:"
        docker ps --filter "name=nfc" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        services_found=true
    fi
    
    # Check systemd
    if command -v systemctl &> /dev/null && systemctl is-active --quiet nfc-server 2>/dev/null; then
        log_info "Systemd service status:"
        systemctl status nfc-server --no-pager -l
        services_found=true
    fi
    
    # Check Kubernetes
    if command -v kubectl &> /dev/null; then
        local pods=$(kubectl get pods -l app.kubernetes.io/name=nfc-server --no-headers 2>/dev/null | wc -l)
        if [ "$pods" -gt 0 ]; then
            log_info "Kubernetes pods found:"
            kubectl get pods -l app.kubernetes.io/name=nfc-server
            services_found=true
        fi
    fi
    
    if [ "$services_found" = false ]; then
        log_warning "No running NFC services found"
    else
        log_success "Health check completed"
    fi
}

# Main function
main() {
    # Parse global options first
    case "${1:-}" in
        --help|-h)
            show_usage
            exit 0
            ;;
        --version|-v)
            show_version
            exit 0
            ;;
        health|status)
            health_check
            exit 0
            ;;
    esac
    
    # Check if deployment type is provided
    if [ $# -eq 0 ]; then
        show_usage
        exit 1
    fi
    
    local deployment_type="$1"
    shift
    
    # Execute deployment based on type
    case "$deployment_type" in
        docker)
            deploy_docker "$@"
            ;;
        kubernetes|k8s)
            deploy_kubernetes "$@"
            ;;
        systemd)
            deploy_systemd "$@"
            ;;
        android-debug)
            build_android "debug" "$@"
            ;;
        android-release)
            build_android "release" "$@"
            ;;
        *)
            log_error "Unknown deployment type: $deployment_type"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
