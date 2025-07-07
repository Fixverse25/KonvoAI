#!/bin/bash

# =============================================================================
# EVA-Dev Production Deployment Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="fixverse.se"
API_DOMAIN="api.fixverse.se"
BACKUP_DIR="/opt/eva-dev/backups"
LOG_FILE="/var/log/eva-dev-deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. Consider using a dedicated user for deployment."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check environment file
    if [[ ! -f .env ]]; then
        error ".env file not found. Please create it from .env.example"
    fi
    
    # Check SSL certificates
    if [[ ! -f nginx/ssl/fixverse.crt ]] || [[ ! -f nginx/ssl/fixverse.key ]]; then
        error "SSL certificates not found in nginx/ssl/"
    fi
    
    # Check required environment variables
    source .env
    required_vars=(
        "AZURE_SPEECH_KEY"
        "AZURE_SPEECH_REGION"
        "ANTHROPIC_API_KEY"
        "SECRET_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    success "Prerequisites check passed"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    mkdir -p "$BACKUP_DIR"
    backup_name="eva-dev-backup-$(date +%Y%m%d-%H%M%S)"
    backup_path="$BACKUP_DIR/$backup_name"
    
    # Create backup directory
    mkdir -p "$backup_path"
    
    # Backup Redis data if running
    if docker-compose -f docker-compose.prod.yml ps redis | grep -q "Up"; then
        log "Backing up Redis data..."
        docker-compose -f docker-compose.prod.yml exec -T redis redis-cli BGSAVE
        sleep 5
        docker cp $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/dump.rdb "$backup_path/"
    fi
    
    # Backup configuration files
    cp -r nginx/ "$backup_path/"
    cp .env "$backup_path/"
    cp docker-compose.prod.yml "$backup_path/"
    
    success "Backup created at $backup_path"
}

# Deploy application
deploy() {
    log "Starting deployment..."
    
    # Pull latest images
    log "Pulling latest images..."
    docker-compose -f docker-compose.prod.yml pull
    
    # Build and start services
    log "Building and starting services..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    sleep 30
    
    # Health checks
    max_attempts=30
    attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        log "Health check attempt $attempt/$max_attempts..."
        
        # Check backend health
        if curl -f -s "http://localhost:8000/health" > /dev/null; then
            success "Backend is healthy"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "Backend health check failed after $max_attempts attempts"
        fi
        
        sleep 10
        ((attempt++))
    done
    
    success "Deployment completed successfully"
}

# Post-deployment tasks
post_deploy() {
    log "Running post-deployment tasks..."
    
    # Clean up old images
    log "Cleaning up old Docker images..."
    docker image prune -f
    
    # Show service status
    log "Service status:"
    docker-compose -f docker-compose.prod.yml ps
    
    # Show resource usage
    log "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    
    success "Post-deployment tasks completed"
}

# Rollback function
rollback() {
    log "Rolling back deployment..."
    
    # Find latest backup
    latest_backup=$(ls -t "$BACKUP_DIR" | head -n1)
    
    if [[ -z "$latest_backup" ]]; then
        error "No backup found for rollback"
    fi
    
    backup_path="$BACKUP_DIR/$latest_backup"
    
    # Stop current services
    docker-compose -f docker-compose.prod.yml down
    
    # Restore configuration
    cp -r "$backup_path/nginx/" ./
    cp "$backup_path/.env" ./
    cp "$backup_path/docker-compose.prod.yml" ./
    
    # Restore Redis data if backup exists
    if [[ -f "$backup_path/dump.rdb" ]]; then
        log "Restoring Redis data..."
        docker-compose -f docker-compose.prod.yml up -d redis
        sleep 10
        docker cp "$backup_path/dump.rdb" $(docker-compose -f docker-compose.prod.yml ps -q redis):/data/
        docker-compose -f docker-compose.prod.yml restart redis
    fi
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    success "Rollback completed"
}

# Main deployment flow
main() {
    log "Starting EVA-Dev deployment process..."
    
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            backup_current
            deploy
            post_deploy
            ;;
        "rollback")
            rollback
            ;;
        "check")
            check_prerequisites
            ;;
        *)
            echo "Usage: $0 [deploy|rollback|check]"
            echo "  deploy   - Full deployment (default)"
            echo "  rollback - Rollback to previous version"
            echo "  check    - Check prerequisites only"
            exit 1
            ;;
    esac
    
    success "EVA-Dev deployment process completed!"
}

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"
