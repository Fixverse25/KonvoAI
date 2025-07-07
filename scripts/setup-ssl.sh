#!/bin/bash

# =============================================================================
# SSL Certificate Setup Script for EVA-Dev
# Supports both Let's Encrypt and self-signed certificates
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="fixverse.se"
API_DOMAIN="api.fixverse.se"
EMAIL="admin@fixverse.se"
SSL_DIR="nginx/ssl"
CERTBOT_DIR="/etc/letsencrypt"

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
        error "This script must be run as root for Let's Encrypt certificates"
    fi
}

# Install certbot if not present
install_certbot() {
    log "Checking for certbot..."
    
    if ! command -v certbot &> /dev/null; then
        log "Installing certbot..."
        
        # Detect OS and install accordingly
        if [[ -f /etc/debian_version ]]; then
            apt-get update
            apt-get install -y certbot
        elif [[ -f /etc/redhat-release ]]; then
            yum install -y certbot
        else
            error "Unsupported OS. Please install certbot manually."
        fi
    fi
    
    success "Certbot is available"
}

# Generate Let's Encrypt certificates
generate_letsencrypt() {
    log "Generating Let's Encrypt certificates..."
    
    # Stop nginx if running
    if systemctl is-active --quiet nginx; then
        log "Stopping nginx..."
        systemctl stop nginx
    fi
    
    # Generate certificates
    certbot certonly \
        --standalone \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN" \
        -d "$API_DOMAIN"
    
    # Create SSL directory
    mkdir -p "$SSL_DIR"
    
    # Copy certificates to nginx directory
    cp "$CERTBOT_DIR/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fixverse.crt"
    cp "$CERTBOT_DIR/live/$DOMAIN/privkey.pem" "$SSL_DIR/fixverse.key"
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/fixverse.crt"
    chmod 600 "$SSL_DIR/fixverse.key"
    
    success "Let's Encrypt certificates generated and installed"
}

# Generate self-signed certificates for development
generate_selfsigned() {
    log "Generating self-signed certificates for development..."
    
    mkdir -p "$SSL_DIR"
    
    # Generate private key
    openssl genrsa -out "$SSL_DIR/fixverse.key" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$SSL_DIR/fixverse.key" -out "$SSL_DIR/fixverse.csr" -subj "/C=US/ST=State/L=City/O=EVA-Dev/CN=$DOMAIN/subjectAltName=DNS:$DOMAIN,DNS:www.$DOMAIN,DNS:$API_DOMAIN"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in "$SSL_DIR/fixverse.csr" -signkey "$SSL_DIR/fixverse.key" -out "$SSL_DIR/fixverse.crt" -extensions v3_req -extfile <(
        echo '[v3_req]'
        echo 'basicConstraints = CA:FALSE'
        echo 'keyUsage = nonRepudiation, digitalSignature, keyEncipherment'
        echo 'subjectAltName = @alt_names'
        echo '[alt_names]'
        echo "DNS.1 = $DOMAIN"
        echo "DNS.2 = www.$DOMAIN"
        echo "DNS.3 = $API_DOMAIN"
        echo "DNS.4 = localhost"
    )
    
    # Clean up CSR
    rm "$SSL_DIR/fixverse.csr"
    
    # Set proper permissions
    chmod 644 "$SSL_DIR/fixverse.crt"
    chmod 600 "$SSL_DIR/fixverse.key"
    
    success "Self-signed certificates generated"
    warning "Self-signed certificates are for development only!"
}

# Setup certificate renewal
setup_renewal() {
    log "Setting up certificate renewal..."
    
    # Create renewal script
    cat > /etc/cron.d/eva-dev-ssl-renewal << EOF
# EVA-Dev SSL Certificate Renewal
0 2 * * * root certbot renew --quiet --post-hook "docker-compose -f /opt/eva-dev/docker-compose.prod.yml restart nginx"
EOF
    
    # Create renewal hook script
    mkdir -p /etc/letsencrypt/renewal-hooks/post
    cat > /etc/letsencrypt/renewal-hooks/post/eva-dev-reload.sh << 'EOF'
#!/bin/bash
# Copy renewed certificates to nginx directory
SSL_DIR="/opt/eva-dev/nginx/ssl"
DOMAIN="fixverse.se"

if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" "$SSL_DIR/fixverse.crt"
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" "$SSL_DIR/fixverse.key"
    chmod 644 "$SSL_DIR/fixverse.crt"
    chmod 600 "$SSL_DIR/fixverse.key"
    
    # Reload nginx
    cd /opt/eva-dev
    docker-compose -f docker-compose.prod.yml restart nginx
fi
EOF
    
    chmod +x /etc/letsencrypt/renewal-hooks/post/eva-dev-reload.sh
    
    success "Certificate renewal configured"
}

# Test certificate
test_certificate() {
    log "Testing SSL certificate..."
    
    if [[ -f "$SSL_DIR/fixverse.crt" ]] && [[ -f "$SSL_DIR/fixverse.key" ]]; then
        # Check certificate validity
        if openssl x509 -in "$SSL_DIR/fixverse.crt" -text -noout > /dev/null 2>&1; then
            success "Certificate is valid"
            
            # Show certificate info
            log "Certificate information:"
            openssl x509 -in "$SSL_DIR/fixverse.crt" -text -noout | grep -E "(Subject:|Issuer:|Not Before:|Not After:|DNS:)"
        else
            error "Certificate is invalid"
        fi
    else
        error "Certificate files not found"
    fi
}

# Main function
main() {
    log "EVA-Dev SSL Certificate Setup"
    
    case "${1:-help}" in
        "letsencrypt")
            check_root
            install_certbot
            generate_letsencrypt
            setup_renewal
            test_certificate
            ;;
        "selfsigned")
            generate_selfsigned
            test_certificate
            ;;
        "renew")
            check_root
            certbot renew
            ;;
        "test")
            test_certificate
            ;;
        *)
            echo "Usage: $0 [letsencrypt|selfsigned|renew|test]"
            echo ""
            echo "Commands:"
            echo "  letsencrypt  - Generate Let's Encrypt certificates (production)"
            echo "  selfsigned   - Generate self-signed certificates (development)"
            echo "  renew        - Renew existing Let's Encrypt certificates"
            echo "  test         - Test existing certificates"
            echo ""
            echo "Examples:"
            echo "  sudo $0 letsencrypt    # For production with real SSL"
            echo "  $0 selfsigned          # For development/testing"
            exit 1
            ;;
    esac
    
    success "SSL setup completed!"
}

main "$@"
