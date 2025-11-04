# Step 13: Security Hardening & Patch Policy

**Status:** Runbook Complete
**Date:** 2025-11-03
**Est. Implementation:** 4-6 hours
**Priority:** P0 CRITICAL (Production Blocker)

---

## 🎯 Objective

Harden production server for AI/CRM deployment:
1. **Firewall** - Restrict to essential ports only (22/80/443)
2. **Patching** - Enable automatic security updates with safe reboots
3. **Services** - Disable unnecessary services, minimize attack surface
4. **Logging** - Configure log rotation, retention, monitoring
5. **Monitoring** - Set up disk usage alerts and health checks

**Environment:** Ubuntu 22.04 LTS / Debian 12 production server

---

## 🔒 Security Hardening Checklist

### Phase 1: Firewall Configuration (UFW)

#### 1.1 Install and Configure UFW

```bash
# Install UFW (if not present)
sudo apt-get update
sudo apt-get install -y ufw

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Enable logging
sudo ufw logging on

# Verification
sudo ufw status verbose
```

#### 1.2 Allow Essential Services

```bash
# SSH (port 22) - CRITICAL: Set this first to avoid lockout!
sudo ufw allow 22/tcp comment 'SSH access'

# HTTP (port 80)
sudo ufw allow 80/tcp comment 'HTTP - will redirect to HTTPS'

# HTTPS (port 443)
sudo ufw allow 443/tcp comment 'HTTPS'

# Verification
sudo ufw show added
```

#### 1.3 Enable Firewall

```bash
# Enable firewall (will ask for confirmation)
sudo ufw enable

# Check status
sudo ufw status numbered

# Expected output:
# Status: active
#
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW IN    Anywhere                   # SSH access
# 80/tcp                     ALLOW IN    Anywhere                   # HTTP
# 443/tcp                    ALLOW IN    Anywhere                   # HTTPS
# 22/tcp (v6)                ALLOW IN    Anywhere (v6)              # SSH access
# 80/tcp (v6)                ALLOW IN    Anywhere (v6)              # HTTP
# 443/tcp (v6)               ALLOW IN    Anywhere (v6)              # HTTPS
```

#### 1.4 IPv6 Handling

```bash
# Verify IPv6 is enabled in UFW
sudo cat /etc/default/ufw | grep IPV6

# Should show: IPV6=yes

# If disabled, enable it:
sudo sed -i 's/IPV6=no/IPV6=yes/' /etc/default/ufw
sudo ufw reload
```

#### 1.5 Rate Limiting (Brute Force Protection)

```bash
# Enable rate limiting on SSH
sudo ufw delete allow 22/tcp
sudo ufw limit 22/tcp comment 'SSH with rate limiting'

# This limits connections to 6 per 30 seconds from same IP

# Verification
sudo ufw status
```

---

### Phase 2: Unattended Security Updates

#### 2.1 Install Unattended Upgrades

```bash
# Install package
sudo apt-get install -y unattended-upgrades apt-listchanges

# Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
# Select "Yes" when prompted
```

#### 2.2 Configure Unattended Upgrades

```bash
# Edit configuration
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades

# Recommended configuration:
```

```conf
// /etc/apt/apt.conf.d/50unattended-upgrades

Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

// Automatically upgrade packages from these (safe) origins
Unattended-Upgrade::Package-Blacklist {
    // List packages to never auto-update (e.g., custom kernels)
};

// Automatically reboot if required (for kernel updates)
Unattended-Upgrade::Automatic-Reboot "true";

// Reboot at specific time (3 AM)
Unattended-Upgrade::Automatic-Reboot-Time "03:00";

// Only reboot if no users logged in
Unattended-Upgrade::Automatic-Reboot-WithUsers "false";

// Email alerts on errors
Unattended-Upgrade::Mail "ops@rivercityclean.com";
Unattended-Upgrade::MailReport "only-on-error";

// Remove unused dependencies
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";

// Enable logging
Unattended-Upgrade::Verbose "true";
```

#### 2.3 Configure Update Frequency

```bash
# Edit auto-update configuration
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```

```conf
// /etc/apt/apt.conf.d/20auto-upgrades

APT::Periodic::Update-Package-Lists "1";        // Daily
APT::Periodic::Download-Upgradeable-Packages "1";  // Daily
APT::Periodic::AutocleanInterval "7";           // Weekly cleanup
APT::Periodic::Unattended-Upgrade "1";          // Daily auto-upgrade
```

#### 2.4 Test Unattended Upgrades

```bash
# Dry run to test configuration
sudo unattended-upgrades --dry-run --debug

# Check logs
sudo tail -f /var/log/unattended-upgrades/unattended-upgrades.log
```

#### 2.5 Safe Reboot Scheduling

```bash
# Create pre-reboot notification script
sudo nano /usr/local/bin/pre-reboot-check.sh
```

```bash
#!/bin/bash
# /usr/local/bin/pre-reboot-check.sh

# Check if critical services are healthy before reboot
SERVICES="nginx postgresql redis-server docker"

for service in $SERVICES; do
    if ! systemctl is-active --quiet $service; then
        echo "CRITICAL: $service is not running. Aborting reboot."
        logger -p user.crit "Automatic reboot aborted: $service not healthy"
        exit 1
    fi
done

# Check if there are active user sessions
if who | grep -v "^root"; then
    echo "Users logged in. Postponing reboot."
    exit 1
fi

# All checks passed
echo "Pre-reboot checks passed. Safe to reboot."
exit 0
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/pre-reboot-check.sh

# Test script
sudo /usr/local/bin/pre-reboot-check.sh
```

---

### Phase 3: Service Hardening

#### 3.1 List All Running Services

```bash
# List all active services
systemctl list-units --type=service --state=running

# List all listening ports
sudo ss -tulpn | grep LISTEN

# List all enabled services (will start on boot)
systemctl list-unit-files --type=service --state=enabled
```

#### 3.2 Disable Unnecessary Services

```bash
# Typical unnecessary services on a web server:

# Bluetooth (if server)
sudo systemctl disable bluetooth.service
sudo systemctl stop bluetooth.service

# CUPS (printing)
sudo systemctl disable cups.service
sudo systemctl stop cups.service

# Avahi (mDNS/Bonjour - not needed on server)
sudo systemctl disable avahi-daemon.service
sudo systemctl stop avahi-daemon.service

# ModemManager (if not using mobile broadband)
sudo systemctl disable ModemManager.service
sudo systemctl stop ModemManager.service

# Whoopsie (Ubuntu error reporting)
sudo systemctl disable whoopsie.service
sudo systemctl stop whoopsie.service

# Verification
systemctl list-units --type=service --state=running | grep -E "bluetooth|cups|avahi|modem|whoopsie"
# Should return nothing
```

#### 3.3 Required Services (Keep Enabled)

```bash
# Core services that MUST remain running:

# - sshd (SSH access)
# - nginx (web server)
# - postgresql (database)
# - redis-server (cache)
# - docker (containers)
# - systemd-resolved (DNS)
# - systemd-timesyncd (time sync)
# - ufw (firewall)
# - unattended-upgrades
# - rsyslog (logging)
# - cron (scheduled tasks)

# Verify critical services are enabled
for service in ssh nginx postgresql redis-server docker ufw rsyslog cron; do
    systemctl is-enabled $service && echo "✓ $service enabled" || echo "✗ $service disabled"
done
```

#### 3.4 SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

```conf
# /etc/ssh/sshd_config hardening

# Disable root login
PermitRootLogin no

# Use public key authentication only
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no

# Disable X11 forwarding
X11Forwarding no

# Limit users
AllowUsers saas

# Change default port (optional but recommended)
# Port 2222

# Use protocol 2 only
Protocol 2

# Limit authentication attempts
MaxAuthTries 3
MaxSessions 2

# Set idle timeout
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable unused authentication methods
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no
```

```bash
# Test configuration
sudo sshd -t

# Reload SSH daemon
sudo systemctl reload ssh

# Verification (from another terminal before closing current session!)
ssh saas@localhost
```

---

### Phase 4: Log Management

#### 4.1 Configure Logrotate

```bash
# Check current logrotate configuration
cat /etc/logrotate.conf

# Create custom logrotate config for application logs
sudo nano /etc/logrotate.d/crm-app
```

```conf
# /etc/logrotate.d/crm-app

/var/log/crm/*.log {
    daily
    rotate 30
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
    postrotate
        systemctl reload nginx > /dev/null 2>&1 || true
    endscript
}

/var/log/nginx/*.log {
    daily
    rotate 14
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}

/var/log/postgresql/*.log {
    daily
    rotate 7
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
}
```

```bash
# Test logrotate configuration
sudo logrotate -d /etc/logrotate.d/crm-app

# Force rotation (for testing)
sudo logrotate -f /etc/logrotate.d/crm-app

# Verification
ls -lh /var/log/nginx/
```

#### 4.2 Configure Journald Limits

```bash
# Edit journald configuration
sudo nano /etc/systemd/journald.conf
```

```conf
# /etc/systemd/journald.conf

[Journal]
# Limit journal size to 1GB
SystemMaxUse=1G

# Keep 1 month of logs
MaxRetentionSec=1month

# Compress logs
Compress=yes

# Forward to syslog
ForwardToSyslog=yes
```

```bash
# Restart journald
sudo systemctl restart systemd-journald

# Verification
sudo journalctl --disk-usage
```

#### 4.3 Set Up Disk Usage Monitoring

```bash
# Install monitoring tools
sudo apt-get install -y ncdu

# Create disk usage check script
sudo nano /usr/local/bin/check-disk-usage.sh
```

```bash
#!/bin/bash
# /usr/local/bin/check-disk-usage.sh

# Disk usage alert threshold (percentage)
THRESHOLD=85

# Email for alerts
ALERT_EMAIL="ops@rivercityclean.com"

# Check disk usage
USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    # Disk usage exceeded threshold
    SUBJECT="ALERT: Disk usage at ${USAGE}% on $(hostname)"
    MESSAGE="Disk usage has exceeded ${THRESHOLD}%\n\nCurrent usage:\n$(df -h)\n\nLargest directories:\n$(du -h / --max-depth=1 2>/dev/null | sort -hr | head -10)"

    echo -e "$MESSAGE" | mail -s "$SUBJECT" "$ALERT_EMAIL"

    # Log to syslog
    logger -p user.warning "Disk usage alert: ${USAGE}% used"

    # Also log to file
    echo "[$(date)] ALERT: Disk usage at ${USAGE}%" >> /var/log/disk-usage-alerts.log
fi

# Log check completed
logger -p user.info "Disk usage check completed: ${USAGE}% used"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/check-disk-usage.sh

# Test script
sudo /usr/local/bin/check-disk-usage.sh

# Schedule via cron (every hour)
sudo crontab -e

# Add line:
# 0 * * * * /usr/local/bin/check-disk-usage.sh
```

---

### Phase 5: System Monitoring

#### 5.1 Install Monitoring Tools

```bash
# Install essential monitoring tools
sudo apt-get install -y \
    htop \
    iotop \
    nethogs \
    sysstat \
    fail2ban \
    aide

# Enable sysstat
sudo systemctl enable sysstat
sudo systemctl start sysstat
```

#### 5.2 Configure Fail2Ban (Intrusion Prevention)

```bash
# Install fail2ban
sudo apt-get install -y fail2ban

# Create local configuration
sudo nano /etc/fail2ban/jail.local
```

```conf
# /etc/fail2ban/jail.local

[DEFAULT]
# Ban time: 1 hour
bantime = 3600

# Find time window: 10 minutes
findtime = 600

# Max retry attempts
maxretry = 5

# Email alerts
destemail = ops@rivercityclean.com
sender = fail2ban@rivercityclean.com
action = %(action_mwl)s

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
# Enable and start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Check status
sudo fail2ban-client status

# Check SSH jail
sudo fail2ban-client status sshd
```

#### 5.3 File Integrity Monitoring (AIDE)

```bash
# Initialize AIDE database (takes several minutes)
sudo aideinit

# Move database to production location
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run integrity check
sudo aide --check

# Schedule daily checks
sudo nano /etc/cron.daily/aide-check
```

```bash
#!/bin/bash
# /etc/cron.daily/aide-check

# Run AIDE check and email results if changes detected
OUTPUT=$(aide --check 2>&1)

if echo "$OUTPUT" | grep -q "changed:"; then
    echo "$OUTPUT" | mail -s "AIDE: File integrity changes detected on $(hostname)" ops@rivercityclean.com
    logger -p security.warning "AIDE detected file changes"
fi

# Update database weekly
if [ $(date +%u) -eq 7 ]; then
    aide --update
    mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db
fi
```

```bash
sudo chmod +x /etc/cron.daily/aide-check
```

---

## 📋 Security Verification Checklist

### Post-Implementation Validation

```bash
# 1. Verify only required ports are open
sudo ufw status numbered
sudo ss -tulpn | grep LISTEN

# Expected ports:
# - 22 (SSH)
# - 80 (HTTP)
# - 443 (HTTPS)
# - 5432 (PostgreSQL - localhost only)
# - 6379 (Redis - localhost only)

# 2. Verify unattended upgrades
sudo systemctl status unattended-upgrades
cat /var/log/unattended-upgrades/unattended-upgrades.log

# 3. Verify unnecessary services disabled
systemctl list-units --type=service --state=running | wc -l
# Should be minimal (< 30 services)

# 4. Verify log rotation
ls -lh /var/log/nginx/
ls -lh /var/log/postgresql/

# 5. Verify fail2ban
sudo fail2ban-client status

# 6. Test SSH hardening
ssh -o PasswordAuthentication=yes saas@localhost
# Should fail with "Permission denied"

# 7. Verify disk monitoring
sudo /usr/local/bin/check-disk-usage.sh
tail /var/log/disk-usage-alerts.log

# 8. Check for listening services
sudo netstat -tlnp
```

---

## 🔄 Rollback Procedures

### If Firewall Locks You Out

```bash
# Method 1: Physical/console access
# - Log in via console
# - Run: sudo ufw disable
# - Reconfigure: sudo ufw allow 22/tcp
# - Re-enable: sudo ufw enable

# Method 2: Cloud provider console/recovery
# - Access via cloud provider's web console
# - Disable UFW
# - Fix rules
# - Re-enable

# Prevention: Always test UFW with two SSH sessions open
```

### If Unattended Upgrades Break System

```bash
# Disable unattended upgrades temporarily
sudo systemctl stop unattended-upgrades
sudo systemctl disable unattended-upgrades

# Review recent upgrades
sudo less /var/log/apt/history.log

# Rollback specific package (if needed)
sudo apt-get install <package>=<old-version>

# Hold package from updates
sudo apt-mark hold <package>

# Re-enable once resolved
sudo systemctl enable unattended-upgrades
sudo systemctl start unattended-upgrades
```

### If Service Hardening Breaks Application

```bash
# Re-enable disabled service
sudo systemctl enable <service>
sudo systemctl start <service>

# Check service logs
sudo journalctl -u <service> -n 50

# Restore original SSH config
sudo cp /etc/ssh/sshd_config.bak /etc/ssh/sshd_config
sudo systemctl reload ssh
```

---

## 📊 Security Monitoring Dashboard

### Daily Security Checks

```bash
# Create daily security report script
sudo nano /usr/local/bin/daily-security-report.sh
```

```bash
#!/bin/bash
# /usr/local/bin/daily-security-report.sh

REPORT_FILE="/var/log/security-daily-report.log"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

{
    echo "========================================="
    echo "Daily Security Report - $DATE"
    echo "========================================="
    echo ""

    echo "1. FIREWALL STATUS"
    sudo ufw status numbered
    echo ""

    echo "2. FAILED LOGIN ATTEMPTS (Last 24h)"
    sudo journalctl --since "24 hours ago" | grep "Failed password" | wc -l
    echo ""

    echo "3. FAIL2BAN STATUS"
    sudo fail2ban-client status sshd
    echo ""

    echo "4. DISK USAGE"
    df -h / | awk 'NR==2 {print $5 " used on /"}'
    echo ""

    echo "5. SYSTEM LOAD"
    uptime
    echo ""

    echo "6. PENDING SECURITY UPDATES"
    sudo apt-get update > /dev/null 2>&1
    apt list --upgradable 2>/dev/null | grep -i security | wc -l
    echo ""

    echo "7. LISTENING PORTS"
    sudo ss -tulpn | grep LISTEN | awk '{print $5}' | sort -u
    echo ""

    echo "8. TOP 5 CPU PROCESSES"
    ps aux --sort=-%cpu | head -6
    echo ""

    echo "9. TOP 5 MEMORY PROCESSES"
    ps aux --sort=-%mem | head -6
    echo ""

} | tee -a "$REPORT_FILE"

# Email report if critical issues found
if sudo fail2ban-client status sshd | grep -q "Currently banned:"; then
    cat "$REPORT_FILE" | mail -s "Security Alert: IPs banned on $(hostname)" ops@rivercityclean.com
fi
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/daily-security-report.sh

# Schedule daily at 8 AM
sudo crontab -e
# Add: 0 8 * * * /usr/local/bin/daily-security-report.sh
```

---

## 🚨 Incident Response Procedures

### Suspected Breach Checklist

1. **Isolate System**
   ```bash
   # Block all incoming connections except from specific admin IP
   sudo ufw default deny incoming
   sudo ufw allow from YOUR_ADMIN_IP to any port 22
   sudo ufw reload
   ```

2. **Preserve Evidence**
   ```bash
   # Take snapshot of current state
   sudo tar -czf /tmp/incident-$(date +%Y%m%d-%H%M%S).tar.gz \
       /var/log \
       /etc/passwd \
       /etc/shadow \
       /etc/sudoers \
       /root/.bash_history \
       /home/*/.bash_history
   ```

3. **Review Logs**
   ```bash
   # Check auth logs
   sudo grep -i "failed\|accepted" /var/log/auth.log

   # Check sudo usage
   sudo grep "sudo" /var/log/auth.log

   # Check new user accounts
   awk -F: '$3 >= 1000 {print $1}' /etc/passwd

   # Check cron jobs
   sudo crontab -l
   ls -la /etc/cron.*
   ```

4. **Check for Backdoors**
   ```bash
   # Check for SUID files
   find / -perm -4000 -type f 2>/dev/null

   # Check active connections
   sudo netstat -antp

   # Check loaded kernel modules
   lsmod
   ```

---

## ✅ Final Security Hardening Checklist

- [ ] UFW firewall enabled with only ports 22, 80, 443 open
- [ ] SSH hardening applied (key-only auth, no root login)
- [ ] Unattended upgrades configured with automatic reboot at 3 AM
- [ ] Unnecessary services disabled (bluetooth, cups, avahi, etc.)
- [ ] Fail2ban installed and monitoring SSH/nginx
- [ ] Log rotation configured (30 days retention, compressed)
- [ ] Disk usage monitoring with 85% threshold alerts
- [ ] File integrity monitoring (AIDE) with daily checks
- [ ] Daily security report automated
- [ ] Rollback procedures documented and tested
- [ ] Incident response plan reviewed
- [ ] All verification tests passed

---

## 📊 Security Metrics to Monitor

### Key Performance Indicators

- **Failed Login Attempts:** < 10/day (spike = investigation)
- **Disk Usage:** < 85% (alert at 85%, critical at 95%)
- **Security Updates Pending:** 0 (auto-applied daily)
- **Fail2Ban Bans:** < 5/day (spike = attack investigation)
- **Open Ports:** Exactly 3 (22, 80, 443)
- **Running Services:** < 30 total
- **Log Rotation:** All logs < 30 days old
- **Uptime:** > 99.9% (downtime only for kernel patches)

---

## 🔐 Additional Hardening (Optional)

### Advanced Security Measures

```bash
# 1. AppArmor (already enabled on Ubuntu)
sudo systemctl status apparmor

# 2. Two-Factor Authentication for SSH
sudo apt-get install libpam-google-authenticator
# Configure per-user: google-authenticator

# 3. Rootkit Detection
sudo apt-get install rkhunter
sudo rkhunter --check

# 4. Kernel Hardening (sysctl)
sudo nano /etc/sysctl.d/99-security.conf
```

```conf
# /etc/sysctl.d/99-security.conf

# IP Forwarding (disable if not router)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore source routed packets
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Enable SYN cookies (DDoS protection)
net.ipv4.tcp_syncookies = 1

# Log suspicious packets
net.ipv4.conf.all.log_martians = 1
```

```bash
# Apply sysctl changes
sudo sysctl -p /etc/sysctl.d/99-security.conf
```

---

**Status:** ✅ Runbook Complete
**Estimated Time:** 4-6 hours for full implementation
**Priority:** P0 - CRITICAL (Must complete before production launch)

**Validation Criteria:**
- Only ports 22, 80, 443 accessible externally
- Unattended upgrades active and logs showing updates
- Unnecessary services disabled (< 30 services running)
- Logs rotating and compressed (< 30 days retention)
- Disk usage alerts functional (test at 85% threshold)
- Fail2ban active with SSH jail enabled
- Daily security reports generating

---

*Runbook created: 2025-11-03*
*Part of AI Suite Implementation (Step 13/16)*
*Status: P0 - PRODUCTION BLOCKER*
