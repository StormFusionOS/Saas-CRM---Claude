# Production Deployment Guide

Complete guide for deploying the SaaS CRM system to production using a two-server architecture.

## Architecture Overview

### Two-Server Design

**Server 1: Frontend + Reverse Proxy**
- Nginx (serves SPAs, reverse proxy to APIs)
- CRM SPA (static files)
- Ops Console SPA (static files)
- SSL/TLS termination
- Rate limiting & security headers

**Server 2: Backend + Data**
- CRM API (FastAPI)
- Ops API (FastAPI)
- PostgreSQL (CRM + Ops databases)
- Redis (cache & Celery broker)
- Qdrant (vector database)
- Celery (worker + beat scheduler)

### Network Flow

```
Internet → Frontend Server (Nginx) → Backend Server (APIs) → Databases
```

## Prerequisites

### Server Requirements

**Frontend Server:**
- Ubuntu 22.04 LTS
- 2 CPU cores, 4GB RAM
- 40GB SSD
- Public IP address
- Domain names pointing to server:
  - `crm.yourdomain.com`
  - `ops.yourdomain.com`

**Backend Server:**
- Ubuntu 22.04 LTS
- 4 CPU cores, 8GB RAM
- 100GB SSD (for databases)
- Private network access to Frontend Server
- Firewall allows only Frontend Server IP

### Software Requirements

- Docker & Docker Compose v2.0+
- Nginx
- Certbot (for SSL/TLS)
- Git

## Step-by-Step Deployment

### 1. Initial Server Setup

#### Frontend Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y nginx certbot python3-certbot-nginx git curl

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Clone repository
git clone https://github.com/your-org/saas-crm.git
cd saas-crm
```

#### Backend Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# Clone repository
git clone https://github.com/your-org/saas-crm.git
cd saas-crm
```

### 2. Configure Environment Variables

#### Backend Server

```bash
# Copy example and edit
cp .env.example .env
nano .env
```

**Critical variables to update:**
```bash
# JWT Secrets (generate strong random strings)
CRM_SECRET_KEY=$(openssl rand -hex 32)
OPS_SECRET_KEY=$(openssl rand -hex 32)

# Database credentials
CRM_DB_PASSWORD=$(openssl rand -hex 16)
OPS_DB_PASSWORD=$(openssl rand -hex 16)

# Domain configuration
BASE_DOMAIN=yourdomain.com

# CORS (allow frontend server)
CRM_CORS_ORIGINS=https://crm.yourdomain.com
OPS_CORS_ORIGINS=https://ops.yourdomain.com

# Disable debug in production
CRM_API_DEBUG=false
OPS_API_DEBUG=false
```

### 3. Deploy Backend Services

#### On Backend Server

```bash
# Start all backend services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Wait for all services to be healthy
docker-compose ps | grep healthy
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### 4. Build Frontend SPAs

#### On Frontend Server

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Build CRM SPA
cd crm
npm install
VITE_CRM_API_URL=https://crm.yourdomain.com/api/v1 npm run build

# Build Ops Console SPA
cd ../ops-console
npm install
VITE_OPS_API_URL=https://ops.yourdomain.com/api/v1 npm run build

# Copy build artifacts to web root
sudo mkdir -p /var/www/crm /var/www/ops
sudo cp -r ../crm/dist/* /var/www/crm/
sudo cp -r dist/* /var/www/ops/

# Set permissions
sudo chown -R www-data:www-data /var/www/crm /var/www/ops
```

### 5. Configure Nginx

#### On Frontend Server

```bash
# Copy production nginx config
sudo cp deploy/nginx/nginx.conf /etc/nginx/nginx.conf

# Update domain names in config
sudo sed -i 's/example.com/yourdomain.com/g' /etc/nginx/nginx.conf

# Update backend API URLs (point to Backend Server's private IP)
BACKEND_IP="10.0.0.10"  # Replace with actual private IP
sudo sed -i "s/localhost:8000/$BACKEND_IP:8000/g" /etc/nginx/nginx.conf
sudo sed -i "s/localhost:8001/$BACKEND_IP:8001/g" /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 6. Configure SSL/TLS

#### On Frontend Server

```bash
# Obtain SSL certificates
sudo certbot --nginx -d crm.yourdomain.com -d ops.yourdomain.com

# Certificates will auto-renew via cron
sudo systemctl status certbot.timer
```

### 7. Configure Firewall

#### Backend Server

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow connections from Frontend Server ONLY
FRONTEND_IP="203.0.113.5"  # Replace with actual public IP
sudo ufw allow from $FRONTEND_IP to any port 8000 proto tcp
sudo ufw allow from $FRONTEND_IP to any port 8001 proto tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable firewall
sudo ufw enable
```

#### Frontend Server

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 8. Database Initialization

#### On Backend Server

```bash
# Run migrations (if you have a migration system)
# docker-compose exec crm-api alembic upgrade head

# Create initial admin user (example)
docker-compose exec crm-api python3 -c "
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@yourdomain.com',
    hashed_password=get_password_hash('change-this-password'),
    roles=['OWNER']
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

### 9. Verification

#### Smoke Tests

```bash
# From Frontend Server
curl -k https://crm.yourdomain.com/api/health
curl -k https://ops.yourdomain.com/api/health

# From browser
https://crm.yourdomain.com
https://ops.yourdomain.com
```

#### Check Logs

```bash
# Backend logs
docker-compose logs -f crm-api
docker-compose logs -f ops-api
docker-compose logs -f celery-worker

# Frontend logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Maintenance

### Updates & Deployments

```bash
# On Backend Server
cd /path/to/saas-crm
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# On Frontend Server
cd /path/to/saas-crm
git pull origin main
cd crm && npm run build
cd ../ops-console && npm run build
sudo cp -r crm/dist/* /var/www/crm/
sudo cp -r ops-console/dist/* /var/www/ops/
sudo systemctl reload nginx
```

### Database Backups

```bash
# Add to crontab (daily at 2 AM)
0 2 * * * docker exec crm-db pg_dump -U crm_user crm_production > /backups/crm_$(date +\%Y\%m\%d).sql
0 2 * * * docker exec ops-db pg_dump -U ops_user ops_production > /backups/ops_$(date +\%Y\%m\%d).sql
```

### Monitoring

```bash
# Check service health
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8001/health

# Check disk space
df -h

# Check memory
free -h

# Check Docker logs
docker-compose logs --tail=100
```

## Troubleshooting

### API Not Responding

```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs crm-api
docker-compose logs ops-api

# Restart services
docker-compose restart crm-api ops-api
```

### Database Connection Issues

```bash
# Check database is running
docker-compose exec crm-db psql -U crm_user -d crm_production -c "SELECT 1;"

# Check connection from API
docker-compose logs crm-api | grep -i "database"
```

### Nginx Issues

```bash
# Test configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues

```bash
# Check certificate expiry
sudo certbot certificates

# Renew manually
sudo certbot renew --dry-run
```

## Security Checklist

- [ ] All secrets changed from defaults
- [ ] Firewall configured on both servers
- [ ] SSL/TLS enabled with valid certificates
- [ ] Database passwords are strong (32+ characters)
- [ ] JWT secrets are strong (64+ characters)
- [ ] CORS origins restricted to production domains
- [ ] Debug mode disabled (DEBUG=false)
- [ ] Database backups configured
- [ ] Monitoring and alerting set up
- [ ] SSH key-based authentication only
- [ ] Docker daemon socket not exposed
- [ ] Rate limiting enabled in Nginx
- [ ] Security headers configured
- [ ] Log rotation configured

## Next Steps

- Set up monitoring (Prometheus, Grafana)
- Configure log aggregation (ELK stack)
- Set up alerting (PagerDuty, OpsGenie)
- Configure automated backups
- Set up CI/CD pipeline
- Perform load testing
- Create disaster recovery plan

---

For questions or issues, contact the operations team.
