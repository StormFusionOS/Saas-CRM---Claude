# Production Deployment Guide - RiverCityClean SaaS CRM

## Platform Recommendation: Oracle Cloud Always Free Tier

**WINNER: Oracle Cloud Always Free Tier**

### Why Oracle Cloud?

✅ **FREE FOREVER** (not just 12 months like AWS)
✅ **Generous specs**: 2 x AMD VMs (1GB RAM each = 2GB total)
✅ **200GB storage** included
✅ **No credit card required** for Always Free tier
✅ **Room to grow** - Can upgrade to paid tier later
✅ **Reliable** - Enterprise-grade infrastructure

### Alternative: Render.com Free Tier
- ✅ Easiest to deploy (one-click)
- ✅ Free tier available
- ⚠️ Spins down after 15min inactivity (slow first request)
- ⚠️ Limited to 512MB RAM

### Alternative: DigitalOcean ($12/month)
- ✅ Excellent documentation
- ✅ Simple droplet management
- ✅ Predictable pricing
- ❌ Not free

---

## OPTION 1: Deploy to Oracle Cloud Always Free (RECOMMENDED)

### Prerequisites
- Oracle account (no credit card needed for Always Free)
- Domain name (optional but recommended - $10-12/year from Namecheap)
- 30-60 minutes of time

### Step-by-Step Deployment

#### Phase 1: Oracle Cloud Setup (15 minutes)

**1.1 Create Oracle Cloud Account**
```bash
# Go to: https://signup.cloud.oracle.com/
# Click "Start for free"
# Fill in details (NO credit card required for Always Free)
# Verify email
# Sign in to console: https://cloud.oracle.com/
```

**1.2 Create Compute Instance (VM)**
```bash
# In Oracle Console:
1. Click "Create a VM instance"
2. Name: crm-production
3. Image: Ubuntu 22.04 (Always Free eligible)
4. Shape: VM.Standard.A1.Flex (ARM-based, Always Free)
   - OCPUs: 2
   - Memory: 12 GB
   (OR use VM.Standard.E2.1.Micro for x86, 1GB RAM)
5. Networking: Create new VCN (Virtual Cloud Network)
6. SSH Keys:
   - Choose "Generate SSH key pair"
   - Download both private and public keys
   - Save as: ~/oracle-ssh-key.pem
7. Boot volume: 50GB (default)
8. Click "Create"
```

**1.3 Configure Firewall Rules**
```bash
# In Oracle Console, while instance is creating:
1. Go to: Networking > Virtual Cloud Networks > Your VCN
2. Click: Security Lists > Default Security List
3. Add Ingress Rules:

   Rule 1 - HTTP:
   - Source CIDR: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port: 80

   Rule 2 - HTTPS:
   - Source CIDR: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port: 443

   Rule 3 - API (CRM):
   - Source CIDR: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port: 8000

   Rule 4 - API (Ops):
   - Source CIDR: 0.0.0.0/0
   - IP Protocol: TCP
   - Destination Port: 8001

4. Click "Add Ingress Rules"
```

**1.4 Get Public IP Address**
```bash
# Wait for instance to finish creating (2-3 minutes)
# In instance details, copy the "Public IP address"
# Example: 129.213.45.67

export ORACLE_IP="YOUR_PUBLIC_IP_HERE"
echo "Server IP: $ORACLE_IP"
```

---

#### Phase 2: SSH and Server Setup (10 minutes)

**2.1 Connect to Server**
```bash
# Fix SSH key permissions (on your local machine)
chmod 400 ~/oracle-ssh-key.pem

# Connect to server
ssh -i ~/oracle-ssh-key.pem ubuntu@$ORACLE_IP

# Once connected, you'll see: ubuntu@crm-production:~$
```

**2.2 Update System and Install Docker**
```bash
# On the server - run each command:

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Log out and back in for group changes
exit

# SSH back in
ssh -i ~/oracle-ssh-key.pem ubuntu@$ORACLE_IP

# Verify Docker works
docker --version
docker-compose --version
```

**2.3 Install Node.js and Git**
```bash
# Install Node.js 20.x (LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install Git
sudo apt install -y git

# Verify installations
node --version  # Should show v20.x
npm --version   # Should show 10.x
git --version
```

**2.4 Configure Ubuntu Firewall**
```bash
# Oracle instances have iptables blocking by default
# Open ports in Ubuntu firewall

sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8001 -j ACCEPT

# Save rules
sudo netfilter-persistent save

# Or install iptables-persistent
sudo apt install iptables-persistent -y
# Answer YES to save current rules
```

---

#### Phase 3: Deploy Application (20 minutes)

**3.1 Clone Repository**
```bash
# On the server

# Clone your repo (use your actual repo URL)
git clone https://github.com/YOUR_USERNAME/Saas-CRM---Claude.git
cd Saas-CRM---Claude

# Checkout the deployment branch
git checkout claude/setup-production-monorepo-011CUhodZTqfxTSwEx6QbENK
```

**3.2 Generate Production Secrets**
```bash
# Create .env file with production secrets
cat > .env << 'EOF'
# Production Environment Variables
# KEEP THIS FILE SECRET - NEVER COMMIT TO GIT

# Security
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=false

# API Endpoints
CRM_API_URL=http://YOUR_SERVER_IP:8000
OPS_API_URL=http://YOUR_SERVER_IP:8001

# CORS - Allow your domain and localhost for testing
CORS_ORIGINS=http://YOUR_SERVER_IP,http://YOUR_SERVER_IP:8080,http://YOUR_DOMAIN

# Token expiration (in seconds)
ACCESS_TOKEN_EXPIRE_SECONDS=1800  # 30 minutes
REFRESH_TOKEN_EXPIRE_SECONDS=604800  # 7 days

# Database (PostgreSQL) - CRM
CRM_DB_NAME=crm_prod
CRM_DB_USER=crm_user
CRM_DB_PASSWORD=$(openssl rand -base64 24)
CRM_DB_HOST=crm-db
CRM_DB_PORT=5432

# Database (PostgreSQL) - Ops
OPS_DB_NAME=ops_prod
OPS_DB_USER=ops_user
OPS_DB_PASSWORD=$(openssl rand -base64 24)
OPS_DB_HOST=ops-db
OPS_DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$(openssl rand -base64 24)

# Email (for notifications - optional, configure later)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your_email@gmail.com
# SMTP_PASSWORD=your_app_password
# EMAIL_FROM=noreply@yourdomain.com

# Feature Flags (enable/disable features)
ENABLE_NEW_DASHBOARD=true
STRICT_WEBHOOK_WINDOW=false
ENABLE_RATE_LIMITING=true
ENABLE_EMAIL_NOTIFICATIONS=false

# Monitoring (optional - configure later)
# SENTRY_DSN=https://...
# LOG_LEVEL=INFO
EOF

# Generate actual random secrets
SECRET_KEY=$(openssl rand -base64 32)
CRM_DB_PASSWORD=$(openssl rand -base64 24)
OPS_DB_PASSWORD=$(openssl rand -base64 24)
REDIS_PASSWORD=$(openssl rand -base64 24)

# Replace placeholders with actual values
sed -i "s/YOUR_SERVER_IP/$ORACLE_IP/g" .env
sed -i "s/\$(openssl rand -base64 32)/$SECRET_KEY/g" .env
sed -i "s/\$(openssl rand -base64 24)/$CRM_DB_PASSWORD/g" .env | head -1
# ... (would need to do this for each password)

# Better approach - manually edit the file:
nano .env

# Replace:
# - YOUR_SERVER_IP with actual IP (e.g., 129.213.45.67)
# - YOUR_DOMAIN with actual domain if you have one
# - Generate secrets by running: openssl rand -base64 32

# Save and exit (Ctrl+X, Y, Enter)
```

**3.3 Build and Start Services**
```bash
# Install SPA dependencies and build
cd crm
npm install
npm run build
cd ..

cd ops-console
npm install
npm run build
cd ..

# Start all services with Docker Compose
docker-compose up -d --build

# This will:
# - Build API Docker images
# - Start PostgreSQL databases
# - Start Redis
# - Start CRM API on port 8000
# - Start Ops API on port 8001

# Check status
docker-compose ps

# Should show all services as "Up" and healthy
```

**3.4 Verify Deployment**
```bash
# Test health endpoints
curl http://localhost:8000/health
# Should return: {"status":"ok","service":"crm-api","version":"1.0.0"}

curl http://localhost:8001/health
# Should return: {"status":"ok","service":"ops-api","version":"1.0.0"}

# Test metrics
curl http://localhost:8000/metrics
curl http://localhost:8001/metrics

# View logs
docker-compose logs -f crm-api
# Press Ctrl+C to stop viewing logs

# If there are errors, check logs:
docker-compose logs crm-api
docker-compose logs ops-api
```

---

#### Phase 4: Install and Configure Nginx (15 minutes)

**4.1 Install Nginx**
```bash
sudo apt install nginx -y

# Verify installation
nginx -v
```

**4.2 Configure Nginx for the Application**
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/crm << 'EOF'
# CRM and Ops Console - Production Nginx Config

server {
    listen 80;
    server_name YOUR_SERVER_IP;  # Replace with your domain if you have one

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=60r/m;
    limit_req_zone $binary_remote_addr zone=web_limit:10m rate=120r/m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # CRM SPA
    location / {
        limit_req zone=web_limit burst=20 nodelay;
        root /home/ubuntu/Saas-CRM---Claude/crm/dist;
        try_files $uri $uri/ /index.html;
        index index.html;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Ops Console SPA
    location /ops/ {
        limit_req zone=web_limit burst=20 nodelay;
        alias /home/ubuntu/Saas-CRM---Claude/ops-console/dist/;
        try_files $uri $uri/ /ops/index.html;
        index index.html;
    }

    # CRM API
    location /api/crm/ {
        limit_req zone=api_limit burst=10 nodelay;
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Ops API
    location /api/ops/ {
        limit_req zone=api_limit burst=10 nodelay;
        proxy_pass http://localhost:8001/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct API access (for testing)
    location /direct/crm/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
    }

    location /direct/ops/ {
        proxy_pass http://localhost:8001/;
        proxy_set_header Host $host;
    }
}
EOF

# Replace YOUR_SERVER_IP with actual IP
sudo sed -i "s/YOUR_SERVER_IP/$ORACLE_IP/g" /etc/nginx/sites-available/crm

# Enable the site
sudo ln -s /etc/nginx/sites-available/crm /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

**4.3 Test the Application**
```bash
# From your local machine (not the server):

# Open in browser:
# http://YOUR_SERVER_IP/           <- CRM SPA
# http://YOUR_SERVER_IP/ops/       <- Ops Console SPA
# http://YOUR_SERVER_IP/direct/crm/health  <- API health check
# http://YOUR_SERVER_IP/direct/ops/health  <- API health check

# Or test with curl:
curl http://YOUR_SERVER_IP/
curl http://YOUR_SERVER_IP/direct/crm/health
curl http://YOUR_SERVER_IP/direct/ops/health
```

---

#### Phase 5: SSL/HTTPS Setup (10 minutes) - OPTIONAL but RECOMMENDED

**5.1 Get a Domain Name (if you don't have one)**
```bash
# Recommended: Namecheap, Google Domains, or Cloudflare
# Cost: $10-12/year for .com domain

# Point A record to your Oracle IP:
# @ -> YOUR_SERVER_IP
# www -> YOUR_SERVER_IP
```

**5.2 Install Certbot and Get SSL Certificate**
```bash
# On the server:

# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate (replace with your actual domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose whether to redirect HTTP to HTTPS (recommended: Yes)

# Certbot will:
# 1. Get a free SSL certificate from Let's Encrypt
# 2. Automatically configure Nginx for HTTPS
# 3. Set up auto-renewal

# Test auto-renewal
sudo certbot renew --dry-run

# Certificate auto-renews every 90 days
```

**5.3 Update SPA Configuration for HTTPS**
```bash
# Update .env file to use HTTPS
cd ~/Saas-CRM---Claude

# Edit .env
nano .env

# Change:
# CRM_API_URL=https://yourdomain.com/api/crm
# OPS_API_URL=https://yourdomain.com/api/ops
# CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rebuild SPAs with new API URLs
cd crm && npm run build && cd ..
cd ops-console && npm run build && cd ..

# Reload Nginx
sudo systemctl reload nginx
```

---

#### Phase 6: Monitoring and Maintenance (5 minutes)

**6.1 Set Up Basic Monitoring**
```bash
# View Docker logs
docker-compose logs -f

# Check disk space
df -h

# Check memory usage
free -h

# Check running containers
docker-compose ps

# View system resources
htop  # (install with: sudo apt install htop)
```

**6.2 Set Up Automated Backups**
```bash
# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
# Backup script for CRM application

BACKUP_DIR="/home/ubuntu/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL databases
docker exec crm-db pg_dump -U crm_user crm_prod > $BACKUP_DIR/crm_$DATE.sql
docker exec ops-db pg_dump -U ops_user ops_prod > $BACKUP_DIR/ops_$DATE.sql

# Backup .env file
cp ~/Saas-CRM---Claude/.env $BACKUP_DIR/env_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "env_*" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup.sh

# Test backup
~/backup.sh

# Schedule daily backups at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/backup.sh") | crontab -
```

**6.3 Set Up Log Rotation**
```bash
# Docker logs are already rotated by default
# Check configuration:
cat /etc/docker/daemon.json

# Should contain:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# If not present, create it:
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
docker-compose up -d  # Restart containers
```

---

## Summary - Your Production URLs

After deployment, your application will be available at:

```
┌─────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT COMPLETE ✓                   │
└─────────────────────────────────────────────────────────────┘

Frontend Applications:
  • CRM SPA:         http://YOUR_SERVER_IP/
  • Ops Console:     http://YOUR_SERVER_IP/ops/

API Endpoints:
  • CRM API:         http://YOUR_SERVER_IP/direct/crm/
  • CRM API Docs:    http://YOUR_SERVER_IP/direct/crm/docs
  • CRM Health:      http://YOUR_SERVER_IP/direct/crm/health
  • CRM Metrics:     http://YOUR_SERVER_IP/direct/crm/metrics

  • Ops API:         http://YOUR_SERVER_IP/direct/ops/
  • Ops API Docs:    http://YOUR_SERVER_IP/direct/ops/docs
  • Ops Health:      http://YOUR_SERVER_IP/direct/ops/health
  • Ops Metrics:     http://YOUR_SERVER_IP/direct/ops/metrics

Default Login Credentials:
  • Email: Nathan@RiverCityClean.com
  • Password: password123

IMPORTANT: Change default password immediately!
```

---

## Troubleshooting

**Issue: Can't connect to server**
```bash
# Check if SSH port is open in Oracle security list
# Check if instance is running
# Verify you're using correct SSH key
ssh -i ~/oracle-ssh-key.pem -v ubuntu@$ORACLE_IP
```

**Issue: Nginx shows 502 Bad Gateway**
```bash
# Check if APIs are running
docker-compose ps

# Restart services
docker-compose restart

# Check API logs
docker-compose logs crm-api
docker-compose logs ops-api
```

**Issue: Out of memory**
```bash
# Check memory usage
free -h

# Add swap space (if using 1GB VM)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Issue: Docker container won't start**
```bash
# Check logs
docker-compose logs [service-name]

# Rebuild specific service
docker-compose up -d --build crm-api

# Remove all containers and start fresh
docker-compose down -v
docker-compose up -d --build
```

**Issue: SPAs not loading**
```bash
# Check if files are built
ls -la ~/Saas-CRM---Claude/crm/dist/
ls -la ~/Saas-CRM---Claude/ops-console/dist/

# Rebuild SPAs
cd ~/Saas-CRM---Claude/crm && npm run build
cd ~/Saas-CRM---Claude/ops-console && npm run build

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

---

## Maintenance Commands

```bash
# Restart all services
cd ~/Saas-CRM---Claude
docker-compose restart

# Update application (pull latest code)
git pull origin claude/setup-production-monorepo-011CUhodZTqfxTSwEx6QbENK
docker-compose up -d --build

# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose stop

# Start all services
docker-compose start

# Check disk usage
docker system df
docker system prune  # Clean up unused images/containers

# Backup database manually
~/backup.sh
```

---

## Next Steps After Deployment

1. **Change default credentials** - Create new users with strong passwords
2. **Set up monitoring** - Consider Sentry for error tracking (free tier)
3. **Configure email** - Add SMTP settings for notifications
4. **Set up backups to cloud** - Use Oracle Object Storage (free 20GB)
5. **Add custom domain** - Point DNS to your server
6. **Enable HTTPS** - Use Certbot with your domain
7. **Configure CI/CD** - Auto-deploy on git push (GitHub Actions)
8. **Add more users** - Invite team members

---

## Cost Breakdown

**Oracle Cloud Always Free:**
- VM: $0/month (Always Free)
- Storage: $0/month (Always Free, 200GB)
- Network: $0/month (Always Free, 10TB outbound)

**Domain (optional):**
- $10-12/year (Namecheap, Google Domains)

**Total: $0-1/month** 🎉

---

## Alternative: Quick Deploy to Render.com (5 minutes)

If you want the absolute fastest deployment (but with limitations):

1. Go to https://render.com
2. Sign in with GitHub
3. New > Web Service
4. Connect your GitHub repo
5. Select branch: claude/setup-production-monorepo-011CUhodZTqfxTSwEx6QbENK
6. Build Command: `cd crm && npm install && npm run build`
7. Start Command: `docker-compose up`
8. Plan: Free
9. Click "Create Web Service"

⚠️ Limitations:
- Spins down after 15min (slow first request)
- 512MB RAM limit
- No persistent storage on free tier
- Limited to 750 hours/month

---

Save this guide for reference! Let me know when you're ready to start, and I'll help you through each step.
