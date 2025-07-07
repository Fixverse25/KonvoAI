# EVA-Dev Deployment Guide

This guide covers deploying EVA-Dev to production on Fixverse.se.

## Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or CentOS 8+
- **RAM**: Minimum 4GB, Recommended 8GB+
- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Storage**: Minimum 20GB SSD
- **Network**: Public IP with ports 80, 443, and 22 accessible

### Domain Setup
- Domain: `fixverse.se`
- API Subdomain: `api.fixverse.se`
- DNS A records pointing to your server IP

### Required Services
- **Azure Speech Services**: Subscription key and region
- **Anthropic Claude API**: API key
- **SSL Certificate**: Let's Encrypt or custom certificate

## Quick Deployment

### 1. Server Setup
```bash
# Run as root on fresh server
curl -fsSL https://raw.githubusercontent.com/your-repo/eva-dev/main/scripts/setup-server.sh | bash
```

### 2. Application Deployment
```bash
# Switch to application user
sudo su - eva-dev
cd /opt/eva-dev

# Clone repository
git clone https://github.com/your-repo/eva-dev.git .

# Configure environment
cp .env.example .env
nano .env  # Edit with your values

# Generate SSL certificates
sudo ./scripts/setup-ssl.sh letsencrypt

# Deploy application
./scripts/deploy.sh
```

## Detailed Setup

### Environment Configuration

Create `.env` file with the following variables:

```bash
# Azure Speech Services
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_region
AZURE_SPEECH_LANGUAGE=en-US
AZURE_SPEECH_VOICE=en-US-AriaNeural

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=4000

# Application URLs
FRONTEND_URL=https://fixverse.se
BACKEND_URL=https://api.fixverse.se

# Security
SECRET_KEY=your_super_secret_key_change_this
ALLOWED_ORIGINS=https://fixverse.se
ALLOWED_HOSTS=fixverse.se,api.fixverse.se

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=WARNING
MAX_AUDIO_DURATION_SECONDS=30
SILENCE_TIMEOUT_SECONDS=3
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Database & Cache
REDIS_URL=redis://redis:6379/0
```

### SSL Certificate Setup

#### Option 1: Let's Encrypt (Recommended)
```bash
sudo ./scripts/setup-ssl.sh letsencrypt
```

#### Option 2: Custom Certificate
```bash
# Copy your certificates to nginx/ssl/
cp your-certificate.crt nginx/ssl/fixverse.crt
cp your-private-key.key nginx/ssl/fixverse.key
chmod 644 nginx/ssl/fixverse.crt
chmod 600 nginx/ssl/fixverse.key
```

### Deployment Process

1. **Build and Deploy**:
   ```bash
   make prod-build
   ```

2. **Verify Deployment**:
   ```bash
   make health
   ```

3. **Monitor Logs**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f
   ```

## Production Monitoring

### Health Checks
- Frontend: `https://fixverse.se/health`
- Backend: `https://api.fixverse.se/health`
- Detailed: `https://api.fixverse.se/api/v1/health/detailed`

### Log Locations
- Application logs: `/opt/eva-dev/logs/`
- Nginx logs: `/opt/eva-dev/nginx/logs/`
- Docker logs: `docker-compose logs`

### Resource Monitoring
```bash
# Container stats
docker stats

# System resources
htop
iotop
df -h
```

## Backup and Recovery

### Automated Backups
Backups are automatically created before each deployment in `/opt/eva-dev/backups/`.

### Manual Backup
```bash
./scripts/deploy.sh backup
```

### Restore from Backup
```bash
./scripts/deploy.sh rollback
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer (nginx, HAProxy, or cloud LB)
- Scale backend containers: `docker-compose up -d --scale backend=3`
- Use external Redis cluster for session storage

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Adjust Docker resource limits in `docker-compose.prod.yml`
- Tune nginx worker processes

## Security Best Practices

### Server Security
- Keep system updated: `apt update && apt upgrade`
- Use fail2ban for intrusion prevention
- Configure firewall (UFW/firewalld)
- Regular security audits

### Application Security
- Rotate API keys regularly
- Use strong SECRET_KEY
- Enable HTTPS only
- Monitor for suspicious activity

### SSL/TLS Security
- Use TLS 1.2+ only
- Strong cipher suites
- HSTS headers enabled
- Certificate monitoring

## Troubleshooting

### Common Issues

#### 1. SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/fixverse.crt -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

#### 2. Service Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Check environment variables
docker-compose -f docker-compose.prod.yml config
```

#### 3. High Memory Usage
```bash
# Check container memory usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

#### 4. API Errors
```bash
# Check backend health
curl -f https://api.fixverse.se/health

# Check Azure Speech service
curl -f https://api.fixverse.se/api/v1/voice/test-services
```

### Performance Optimization

#### Backend Optimization
- Adjust Gunicorn workers: `--workers 4`
- Tune Redis memory settings
- Enable response compression
- Optimize Claude API calls

#### Frontend Optimization
- Enable nginx gzip compression
- Set proper cache headers
- Optimize bundle size
- Use CDN for static assets

## Maintenance

### Regular Tasks
- **Daily**: Check logs and health status
- **Weekly**: Review resource usage and performance
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Review and rotate secrets

### Update Process
1. Test updates in staging environment
2. Create backup before deployment
3. Deploy during low-traffic periods
4. Monitor for issues post-deployment
5. Rollback if necessary

### Monitoring Alerts
Set up alerts for:
- Service downtime
- High error rates
- Resource exhaustion
- SSL certificate expiration
- Failed backups

## Support

### Log Analysis
```bash
# Search for errors
grep -i error /opt/eva-dev/logs/*.log

# Monitor real-time logs
tail -f /opt/eva-dev/logs/app.log
```

### Performance Analysis
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://api.fixverse.se/health

# Database performance
docker-compose exec redis redis-cli info stats
```

For additional support, check the troubleshooting section in the main README or contact the development team.
