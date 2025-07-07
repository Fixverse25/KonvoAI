#!/bin/bash

# =============================================================================
# EVA-Dev Server Setup Script
# Prepares a fresh server for EVA-Dev deployment
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root"
    fi
}

# Update system
update_system() {
    log "Updating system packages..."
    
    if [[ -f /etc/debian_version ]]; then
        apt-get update
        apt-get upgrade -y
        apt-get install -y curl wget git unzip software-properties-common
    elif [[ -f /etc/redhat-release ]]; then
        yum update -y
        yum install -y curl wget git unzip
    else
        error "Unsupported operating system"
    fi
    
    success "System updated"
}

# Install Docker
install_docker() {
    log "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log "Docker already installed"
        return
    fi
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    # Add current user to docker group if not root
    if [[ $SUDO_USER ]]; then
        usermod -aG docker $SUDO_USER
        log "Added $SUDO_USER to docker group"
    fi
    
    success "Docker installed"
}

# Install Docker Compose
install_docker_compose() {
    log "Installing Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        log "Docker Compose already installed"
        return
    fi
    
    # Get latest version
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    
    # Download and install
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    
    # Create symlink
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    success "Docker Compose installed"
}

# Configure firewall
configure_firewall() {
    log "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian firewall
        ufw --force enable
        ufw default deny incoming
        ufw default allow outgoing
        ufw allow ssh
        ufw allow 80/tcp
        ufw allow 443/tcp
        success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewall
        systemctl start firewalld
        systemctl enable firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --reload
        success "Firewalld configured"
    else
        warning "No supported firewall found. Please configure manually."
    fi
}

# Create application user
create_app_user() {
    log "Creating application user..."
    
    if id "eva-dev" &>/dev/null; then
        log "User eva-dev already exists"
        return
    fi
    
    # Create user
    useradd -m -s /bin/bash eva-dev
    usermod -aG docker eva-dev
    
    # Create application directory
    mkdir -p /opt/eva-dev
    chown eva-dev:eva-dev /opt/eva-dev
    
    success "Application user created"
}

# Setup application directory
setup_app_directory() {
    log "Setting up application directory..."
    
    APP_DIR="/opt/eva-dev"
    
    # Create necessary directories
    mkdir -p "$APP_DIR"/{logs,backups,data}
    mkdir -p "$APP_DIR/nginx"/{ssl,logs}
    
    # Set permissions
    chown -R eva-dev:eva-dev "$APP_DIR"
    chmod 755 "$APP_DIR"
    chmod 700 "$APP_DIR/nginx/ssl"
    
    success "Application directory setup complete"
}

# Install monitoring tools
install_monitoring() {
    log "Installing monitoring tools..."
    
    # Install htop, iotop, etc.
    if [[ -f /etc/debian_version ]]; then
        apt-get install -y htop iotop nethogs ncdu
    elif [[ -f /etc/redhat-release ]]; then
        yum install -y htop iotop nethogs ncdu
    fi
    
    success "Monitoring tools installed"
}

# Configure log rotation
configure_logrotate() {
    log "Configuring log rotation..."
    
    cat > /etc/logrotate.d/eva-dev << 'EOF'
/opt/eva-dev/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 eva-dev eva-dev
    postrotate
        docker-compose -f /opt/eva-dev/docker-compose.prod.yml restart nginx || true
    endscript
}

/var/log/eva-dev-deploy.log {
    weekly
    missingok
    rotate 12
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF
    
    success "Log rotation configured"
}

# Setup system limits
configure_limits() {
    log "Configuring system limits..."
    
    cat >> /etc/security/limits.conf << 'EOF'
# EVA-Dev limits
eva-dev soft nofile 65536
eva-dev hard nofile 65536
eva-dev soft nproc 4096
eva-dev hard nproc 4096
EOF
    
    # Configure systemd limits
    mkdir -p /etc/systemd/system.conf.d
    cat > /etc/systemd/system.conf.d/eva-dev.conf << 'EOF'
[Manager]
DefaultLimitNOFILE=65536
DefaultLimitNPROC=4096
EOF
    
    success "System limits configured"
}

# Install fail2ban for security
install_fail2ban() {
    log "Installing fail2ban..."
    
    if [[ -f /etc/debian_version ]]; then
        apt-get install -y fail2ban
    elif [[ -f /etc/redhat-release ]]; then
        yum install -y epel-release
        yum install -y fail2ban
    fi
    
    # Configure fail2ban
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF
    
    systemctl enable fail2ban
    systemctl start fail2ban
    
    success "Fail2ban installed and configured"
}

# Setup automatic updates
setup_auto_updates() {
    log "Setting up automatic security updates..."
    
    if [[ -f /etc/debian_version ]]; then
        apt-get install -y unattended-upgrades
        
        cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF
        
        cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
    fi
    
    success "Automatic updates configured"
}

# Main function
main() {
    log "Starting EVA-Dev server setup..."
    
    check_root
    update_system
    install_docker
    install_docker_compose
    configure_firewall
    create_app_user
    setup_app_directory
    install_monitoring
    configure_logrotate
    configure_limits
    install_fail2ban
    setup_auto_updates
    
    success "Server setup completed!"
    
    log "Next steps:"
    echo "1. Copy your EVA-Dev application files to /opt/eva-dev/"
    echo "2. Create .env file with your configuration"
    echo "3. Generate SSL certificates: ./scripts/setup-ssl.sh letsencrypt"
    echo "4. Deploy the application: ./scripts/deploy.sh"
    echo ""
    echo "Switch to eva-dev user: sudo su - eva-dev"
    echo "Application directory: /opt/eva-dev"
}

main "$@"
