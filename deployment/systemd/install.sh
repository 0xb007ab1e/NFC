#!/bin/bash
set -e

# NFC Reader/Writer System - Systemd Service Installer
# This script installs the NFC server as a systemd service

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NFC_USER="nfc"
NFC_GROUP="nfc"
INSTALL_DIR="/opt/nfc-server"
CONFIG_DIR="/etc/nfc-server"
LOG_DIR="/var/log/nfc-server"
SERVICE_NAME="nfc-server"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVER_DIR="$PROJECT_ROOT/server"

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

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if server directory exists
    if [ ! -d "$SERVER_DIR" ]; then
        log_error "Server directory not found: $SERVER_DIR"
        exit 1
    fi
    
    # Check if Python 3.9+ is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.9+"
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ "$(echo "$PYTHON_VERSION 3.9" | awk '{print ($1 >= $2)}')" != "1" ]; then
        log_error "Python 3.9+ required, found $PYTHON_VERSION"
        exit 1
    fi
    
    # Check if systemd is available
    if ! command -v systemctl &> /dev/null; then
        log_error "systemctl not found. This system doesn't support systemd"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create NFC user and group
create_user() {
    log_info "Creating NFC user and group..."
    
    # Create group if it doesn't exist
    if ! getent group "$NFC_GROUP" > /dev/null 2>&1; then
        groupadd --system "$NFC_GROUP"
        log_info "Created group: $NFC_GROUP"
    else
        log_info "Group already exists: $NFC_GROUP"
    fi
    
    # Create user if it doesn't exist
    if ! getent passwd "$NFC_USER" > /dev/null 2>&1; then
        useradd --system --gid "$NFC_GROUP" --home-dir "$INSTALL_DIR" \
                --shell /bin/false --comment "NFC Server" "$NFC_USER"
        log_info "Created user: $NFC_USER"
    else
        log_info "User already exists: $NFC_USER"
    fi
    
    log_success "User and group setup completed"
}

# Create directories
create_directories() {
    log_info "Creating directories..."
    
    # Create installation directory
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$LOG_DIR"
    
    # Set ownership
    chown -R "$NFC_USER:$NFC_GROUP" "$INSTALL_DIR"
    chown -R "$NFC_USER:$NFC_GROUP" "$LOG_DIR"
    chown -R root:root "$CONFIG_DIR"
    chmod 750 "$CONFIG_DIR"
    
    log_success "Directories created"
}

# Install application
install_application() {
    log_info "Installing NFC server application..."
    
    # Copy server files
    cp -r "$SERVER_DIR"/* "$INSTALL_DIR/"
    
    # Create virtual environment
    log_info "Creating Python virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
    
    # Install dependencies
    log_info "Installing Python dependencies..."
    "$INSTALL_DIR/venv/bin/pip" install --upgrade pip setuptools wheel
    "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    
    # Set proper ownership
    chown -R "$NFC_USER:$NFC_GROUP" "$INSTALL_DIR"
    
    # Make scripts executable
    find "$INSTALL_DIR" -name "*.py" -exec chmod 644 {} \;
    chmod 755 "$INSTALL_DIR/main.py"
    
    log_success "Application installed"
}

# Install systemd service
install_service() {
    log_info "Installing systemd service..."
    
    # Copy service file
    cp "$SCRIPT_DIR/nfc-server.service" "/etc/systemd/system/"
    
    # Create environment file
    cat > "$CONFIG_DIR/environment" << EOF
# NFC Server Environment Configuration
# Edit this file to customize server settings

# Database Configuration
DATABASE_URL=postgresql://nfc_user:nfc_password@localhost:5432/nfc_system

# Server Configuration
NFC_SERVER_HOST=127.0.0.1
NFC_SERVER_PORT=8000
NFC_SERVER_LOG_LEVEL=info

# Security Configuration (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=change-this-secret-key-in-production
JWT_SECRET_KEY=change-this-jwt-secret-key-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Environment
ENVIRONMENT=production
DEBUG=false
EOF
    
    # Set proper permissions
    chown root:root "/etc/systemd/system/nfc-server.service"
    chmod 644 "/etc/systemd/system/nfc-server.service"
    chown root:root "$CONFIG_DIR/environment"
    chmod 640 "$CONFIG_DIR/environment"
    
    # Reload systemd
    systemctl daemon-reload
    
    log_success "Systemd service installed"
}

# Setup log rotation
setup_logrotate() {
    log_info "Setting up log rotation..."
    
    cat > "/etc/logrotate.d/nfc-server" << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $NFC_USER $NFC_GROUP
    postrotate
        systemctl reload-or-restart nfc-server > /dev/null 2>&1 || true
    endscript
}
EOF
    
    log_success "Log rotation configured"
}

# Create database migration script
create_migration_script() {
    log_info "Creating database migration script..."
    
    cat > "$INSTALL_DIR/migrate-database.sh" << 'EOF'
#!/bin/bash
# Database migration script for NFC Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running database migrations..."
source venv/bin/activate
python -m alembic -c db/migrations/alembic.ini upgrade head
echo "Database migrations completed successfully!"
EOF
    
    chmod 755 "$INSTALL_DIR/migrate-database.sh"
    chown "$NFC_USER:$NFC_GROUP" "$INSTALL_DIR/migrate-database.sh"
    
    log_success "Migration script created"
}

# Show post-installation instructions
show_instructions() {
    log_info "Installation completed successfully!"
    echo ""
    echo -e "${GREEN}===== POST-INSTALLATION INSTRUCTIONS =====${NC}"
    echo ""
    echo "1. Configure the service by editing:"
    echo "   $CONFIG_DIR/environment"
    echo ""
    echo "2. Set up your database (PostgreSQL) and update DATABASE_URL"
    echo ""
    echo "3. Run database migrations:"
    echo "   sudo -u $NFC_USER $INSTALL_DIR/migrate-database.sh"
    echo ""
    echo "4. Start and enable the service:"
    echo "   systemctl start $SERVICE_NAME"
    echo "   systemctl enable $SERVICE_NAME"
    echo ""
    echo "5. Check service status:"
    echo "   systemctl status $SERVICE_NAME"
    echo ""
    echo "6. View logs:"
    echo "   journalctl -u $SERVICE_NAME -f"
    echo ""
    echo "7. The server will be available at:"
    echo "   http://127.0.0.1:8000 (default)"
    echo ""
    echo -e "${YELLOW}WARNING:${NC} Remember to change the default secret keys in production!"
    echo "Edit $CONFIG_DIR/environment and update:"
    echo "- SECRET_KEY"
    echo "- JWT_SECRET_KEY"
    echo "- DATABASE_URL"
    echo ""
}

# Main installation function
main() {
    log_info "Starting NFC Server systemd installation..."
    
    check_root
    check_prerequisites
    create_user
    create_directories
    install_application
    install_service
    setup_logrotate
    create_migration_script
    show_instructions
}

# Execute main function
main "$@"
