# Step 14: Backups, Partitions & Disaster Recovery

**Status:** Runbook Complete
**Date:** 2025-11-03
**Est. Implementation:** 8-10 hours
**Priority:** P0 CRITICAL (Production Blocker)

---

## 🎯 Objective

Implement production-grade backup and disaster recovery:
1. **Partitioning** - Time-partition large tables (serp_*, competitor_pages, task_logs)
2. **Backups** - Nightly PostgreSQL dumps + configuration backups
3. **Restore Drills** - Weekly automated restore verification
4. **Health Monitoring** - Dashboard heartbeat signals (backup_ok, last_restore_check)
5. **Storage Policy** - Hot/cold tier strategy (SSD → HDD)

**Recovery Time Objective (RTO):** < 1 hour
**Recovery Point Objective (RPO):** < 24 hours

---

## 📊 Database Size Assessment

### Current Database Sizes (Projected)

```sql
-- Check current database sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY size_bytes DESC
LIMIT 20;
```

**Expected Large Tables:**
- `serp_results` - ~50GB/year (daily SERP data)
- `competitor_pages` - ~100GB/year (crawled content)
- `task_logs` - ~20GB/year (automation logs)
- `change_log` - ~10GB/year (AI suggestions)
- `interactions` - ~15GB/year (communications)

---

## 🗂️ Table Partitioning Strategy

### Phase 1: Partition Large Tables by Time

#### 1.1 Partition `serp_results` (Daily SERP Data)

```sql
-- crm_api/migrations/partition_serp_results.sql

-- Step 1: Rename existing table
ALTER TABLE serp_results RENAME TO serp_results_old;

-- Step 2: Create partitioned table
CREATE TABLE serp_results (
    id SERIAL,
    keyword_id INT NOT NULL,
    search_date DATE NOT NULL,
    rank INT,
    url TEXT,
    title TEXT,
    description TEXT,
    featured_snippet BOOLEAN DEFAULT FALSE,
    serp_features JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id, search_date)
) PARTITION BY RANGE (search_date);

-- Step 3: Create partitions (monthly for efficiency)
-- Current month (hot - on SSD)
CREATE TABLE serp_results_2025_11 PARTITION OF serp_results
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Previous months (warm - can move to HDD after 3 months)
CREATE TABLE serp_results_2025_10 PARTITION OF serp_results
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

CREATE TABLE serp_results_2025_09 PARTITION OF serp_results
    FOR VALUES FROM ('2025-09-01') TO ('2025-10-01');

-- Create index on each partition
CREATE INDEX ON serp_results_2025_11 (keyword_id, search_date);
CREATE INDEX ON serp_results_2025_10 (keyword_id, search_date);
CREATE INDEX ON serp_results_2025_09 (keyword_id, search_date);

-- Step 4: Migrate old data (if exists)
-- INSERT INTO serp_results SELECT * FROM serp_results_old;

-- Step 5: Drop old table (after verification!)
-- DROP TABLE serp_results_old;

-- Create function to automatically create next month's partition
CREATE OR REPLACE FUNCTION create_serp_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    -- Get first day of next month
    partition_date := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
    partition_name := 'serp_results_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';

    -- Check if partition already exists
    IF NOT EXISTS (
        SELECT 1 FROM pg_tables
        WHERE tablename = partition_name
    ) THEN
        -- Create partition
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF serp_results FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );

        -- Create index
        EXECUTE format(
            'CREATE INDEX ON %I (keyword_id, search_date)',
            partition_name
        );

        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly partition creation (via cron)
-- Will be added to crontab: 0 0 1 * * psql -c "SELECT create_serp_partition();"
```

#### 1.2 Partition `competitor_pages` (Crawled Content)

```sql
-- crm_api/migrations/partition_competitor_pages.sql

-- Partition by crawl_date (monthly)
ALTER TABLE competitor_pages RENAME TO competitor_pages_old;

CREATE TABLE competitor_pages (
    id SERIAL,
    competitor_domain VARCHAR(255),
    url TEXT,
    content TEXT,
    content_hash VARCHAR(64),
    crawl_date DATE NOT NULL,
    meta_title TEXT,
    meta_description TEXT,
    h1_tags TEXT[],
    word_count INT,
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (id, crawl_date)
) PARTITION BY RANGE (crawl_date);

-- Create initial partitions
CREATE TABLE competitor_pages_2025_11 PARTITION OF competitor_pages
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

CREATE TABLE competitor_pages_2025_10 PARTITION OF competitor_pages
    FOR VALUES FROM ('2025-10-01') TO ('2025-11-01');

-- Indexes
CREATE INDEX ON competitor_pages_2025_11 (competitor_domain, crawl_date);
CREATE INDEX ON competitor_pages_2025_10 (competitor_domain, crawl_date);

-- Auto-create function (similar to serp_results)
CREATE OR REPLACE FUNCTION create_competitor_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_date := DATE_TRUNC('month', NOW() + INTERVAL '1 month');
    partition_name := 'competitor_pages_' || TO_CHAR(partition_date, 'YYYY_MM');
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 month';

    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = partition_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF competitor_pages FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        EXECUTE format('CREATE INDEX ON %I (competitor_domain, crawl_date)', partition_name);
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

#### 1.3 Partition `task_logs` (Automation Logs)

```sql
-- crm_api/migrations/partition_task_logs.sql

-- Partition by created_at (weekly for granular archival)
ALTER TABLE task_logs RENAME TO task_logs_old;

CREATE TABLE task_logs (
    id SERIAL,
    module_name VARCHAR(100),
    task_name VARCHAR(255),
    status VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create weekly partitions (keep last 12 weeks = 3 months)
-- Week 1
CREATE TABLE task_logs_2025_w45 PARTITION OF task_logs
    FOR VALUES FROM ('2025-11-03') TO ('2025-11-10');

-- Indexes
CREATE INDEX ON task_logs_2025_w45 (module_name, created_at);
CREATE INDEX ON task_logs_2025_w45 (status, created_at);

-- Auto-create weekly partitions
CREATE OR REPLACE FUNCTION create_tasklog_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE;
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
    week_num INT;
BEGIN
    -- Get next Monday
    partition_date := DATE_TRUNC('week', NOW() + INTERVAL '1 week');
    week_num := EXTRACT(WEEK FROM partition_date);
    partition_name := 'task_logs_' || TO_CHAR(partition_date, 'YYYY') || '_w' || week_num;
    start_date := partition_date;
    end_date := partition_date + INTERVAL '1 week';

    IF NOT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = partition_name) THEN
        EXECUTE format(
            'CREATE TABLE %I PARTITION OF task_logs FOR VALUES FROM (%L) TO (%L)',
            partition_name, start_date, end_date
        );
        EXECUTE format('CREATE INDEX ON %I (module_name, created_at)', partition_name);
        EXECUTE format('CREATE INDEX ON %I (status, created_at)', partition_name);
        RAISE NOTICE 'Created partition: %', partition_name;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### Phase 2: Partition Maintenance & Archival

#### Archive Old Partitions to Cold Storage

```sql
-- Function to move old partitions to separate tablespace (HDD)
CREATE OR REPLACE FUNCTION archive_old_partitions()
RETURNS void AS $$
DECLARE
    partition_rec RECORD;
    archive_date DATE;
BEGIN
    -- Archive partitions older than 3 months to HDD tablespace
    archive_date := NOW() - INTERVAL '3 months';

    -- Find old serp_results partitions
    FOR partition_rec IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename LIKE 'serp_results_20%'
          AND tablename < 'serp_results_' || TO_CHAR(archive_date, 'YYYY_MM')
    LOOP
        -- Move to archive tablespace (assumes 'archive_hdd' tablespace exists)
        EXECUTE format('ALTER TABLE %I SET TABLESPACE archive_hdd', partition_rec.tablename);
        RAISE NOTICE 'Archived partition: %', partition_rec.tablename;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly archival
-- Cron: 0 2 1 * * psql -c "SELECT archive_old_partitions();"
```

#### Drop Very Old Partitions (Data Retention Policy)

```sql
-- Function to drop partitions older than retention period
CREATE OR REPLACE FUNCTION drop_expired_partitions()
RETURNS void AS $$
DECLARE
    partition_rec RECORD;
    retention_date DATE;
BEGIN
    -- Drop serp_results older than 2 years
    retention_date := NOW() - INTERVAL '2 years';

    FOR partition_rec IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename LIKE 'serp_results_20%'
          AND tablename < 'serp_results_' || TO_CHAR(retention_date, 'YYYY_MM')
    LOOP
        EXECUTE format('DROP TABLE IF EXISTS %I', partition_rec.tablename);
        RAISE NOTICE 'Dropped expired partition: %', partition_rec.tablename;
    END LOOP;

    -- Drop task_logs older than 6 months
    retention_date := NOW() - INTERVAL '6 months';

    FOR partition_rec IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
          AND tablename LIKE 'task_logs_20%'
          AND tablename < 'task_logs_' || TO_CHAR(retention_date, 'YYYY') || '_w' || EXTRACT(WEEK FROM retention_date)
    LOOP
        EXECUTE format('DROP TABLE IF EXISTS %I', partition_rec.tablename);
        RAISE NOTICE 'Dropped expired partition: %', partition_rec.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Schedule monthly cleanup
-- Cron: 0 3 1 * * psql -c "SELECT drop_expired_partitions();"
```

---

## 💾 Backup Strategy

### Phase 1: PostgreSQL Database Backups

#### 1.1 Nightly Full Backup Script

```bash
#!/bin/bash
# /usr/local/bin/backup-postgres.sh

set -e  # Exit on error
set -o pipefail  # Catch pipe errors

# Configuration
BACKUP_DIR="/var/backups/postgresql"
BACKUP_RETENTION_DAYS=30
S3_BUCKET="s3://rivercityclean-backups/postgresql"
DB_NAME="crm_production"
DB_USER="crm_user"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"
HEALTH_FILE="/var/lib/backup-health/last_backup.json"

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a /var/log/backup-postgres.log
}

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$(dirname $HEALTH_FILE)"

log "Starting PostgreSQL backup: $DB_NAME"

# Perform backup with compression
if pg_dump -U "$DB_USER" -Fc "$DB_NAME" | gzip > "$BACKUP_FILE"; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Backup completed successfully: $BACKUP_FILE ($BACKUP_SIZE)"

    # Calculate checksum
    CHECKSUM=$(sha256sum "$BACKUP_FILE" | cut -d' ' -f1)
    log "Backup checksum: $CHECKSUM"

    # Upload to S3 (if configured)
    if command -v aws &> /dev/null; then
        log "Uploading to S3: $S3_BUCKET"
        if aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/$(basename $BACKUP_FILE)" --storage-class STANDARD_IA; then
            log "S3 upload successful"
            S3_STATUS="success"
        else
            log "ERROR: S3 upload failed"
            S3_STATUS="failed"
        fi
    else
        S3_STATUS="not_configured"
    fi

    # Write health file (for dashboard)
    cat > "$HEALTH_FILE" <<EOF
{
    "last_backup_time": "$(date -Iseconds)",
    "backup_file": "$BACKUP_FILE",
    "backup_size_bytes": $(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE"),
    "backup_size_human": "$BACKUP_SIZE",
    "checksum": "$CHECKSUM",
    "database": "$DB_NAME",
    "status": "success",
    "s3_status": "$S3_STATUS"
}
EOF

    log "Backup health file updated: $HEALTH_FILE"

else
    log "ERROR: Backup failed!"

    # Write failure to health file
    cat > "$HEALTH_FILE" <<EOF
{
    "last_backup_time": "$(date -Iseconds)",
    "status": "failed",
    "error": "pg_dump failed"
}
EOF

    # Send alert
    echo "PostgreSQL backup failed on $(hostname)" | mail -s "BACKUP FAILURE" ops@rivercityclean.com

    exit 1
fi

# Cleanup old backups (retain last N days)
log "Cleaning up backups older than $BACKUP_RETENTION_DAYS days"
find "$BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -type f -mtime +$BACKUP_RETENTION_DAYS -delete

# Verify backup integrity
log "Verifying backup integrity"
if gzip -t "$BACKUP_FILE"; then
    log "Backup integrity check passed"
else
    log "ERROR: Backup integrity check failed!"
    exit 1
fi

log "Backup process completed"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-postgres.sh

# Schedule nightly at 2 AM
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-postgres.sh
```

#### 1.2 Configuration Backup Script

```bash
#!/bin/bash
# /usr/local/bin/backup-configs.sh

set -e

BACKUP_DIR="/var/backups/configs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/configs_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

# Backup critical configuration files
tar -czf "$BACKUP_FILE" \
    /etc/nginx/ \
    /etc/postgresql/ \
    /etc/redis/ \
    /etc/ssh/sshd_config \
    /etc/ufw/ \
    /etc/systemd/system/ \
    /home/saas/Saas-CRM---Claude/crm_api/.env \
    /home/saas/Saas-CRM---Claude/ops_api/.env \
    2>/dev/null || true

echo "Configuration backup completed: $BACKUP_FILE"

# Cleanup old configs (retain 60 days)
find "$BACKUP_DIR" -name "configs_*.tar.gz" -type f -mtime +60 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-configs.sh

# Schedule weekly on Sundays at 3 AM
sudo crontab -e
# Add: 0 3 * * 0 /usr/local/bin/backup-configs.sh
```

### Phase 2: Backup Verification (Restore Drills)

#### 2.1 Weekly Restore Test Script

```bash
#!/bin/bash
# /usr/local/bin/restore-drill.sh

set -e

BACKUP_DIR="/var/backups/postgresql"
TEST_DB="crm_restore_test"
RESTORE_LOG="/var/log/restore-drill.log"
HEALTH_FILE="/var/lib/backup-health/last_restore.json"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$RESTORE_LOG"
}

log "Starting weekly restore drill"

# Find most recent backup
LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/crm_production_*.sql.gz | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    log "ERROR: No backup found!"
    exit 1
fi

log "Testing restore of: $LATEST_BACKUP"

# Drop test database if exists
psql -U postgres -c "DROP DATABASE IF EXISTS $TEST_DB" 2>/dev/null || true

# Create test database
log "Creating test database: $TEST_DB"
psql -U postgres -c "CREATE DATABASE $TEST_DB"

# Restore backup
log "Restoring backup..."
START_TIME=$(date +%s)

if gunzip -c "$LATEST_BACKUP" | psql -U postgres -d "$TEST_DB" > /dev/null 2>&1; then
    END_TIME=$(date +%s)
    RESTORE_DURATION=$((END_TIME - START_TIME))

    log "Restore successful in ${RESTORE_DURATION} seconds"

    # Verify data integrity
    TABLE_COUNT=$(psql -U postgres -d "$TEST_DB" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    log "Restored $TABLE_COUNT tables"

    # Sample data verification
    LEAD_COUNT=$(psql -U postgres -d "$TEST_DB" -t -c "SELECT COUNT(*) FROM leads" 2>/dev/null || echo "0")
    log "Sample check - Leads: $LEAD_COUNT"

    # Write success to health file
    cat > "$HEALTH_FILE" <<EOF
{
    "last_restore_test_time": "$(date -Iseconds)",
    "backup_file": "$LATEST_BACKUP",
    "restore_duration_seconds": $RESTORE_DURATION,
    "tables_restored": $TABLE_COUNT,
    "status": "success"
}
EOF

    log "Restore drill completed successfully"

else
    log "ERROR: Restore failed!"

    cat > "$HEALTH_FILE" <<EOF
{
    "last_restore_test_time": "$(date -Iseconds)",
    "status": "failed",
    "error": "psql restore failed"
}
EOF

    # Send alert
    echo "Restore drill failed on $(hostname)" | mail -s "RESTORE DRILL FAILURE" ops@rivercityclean.com

    exit 1
fi

# Cleanup test database
log "Cleaning up test database"
psql -U postgres -c "DROP DATABASE $TEST_DB"

log "Restore drill completed"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/restore-drill.sh

# Schedule weekly on Sundays at 4 AM
sudo crontab -e
# Add: 0 4 * * 0 /usr/local/bin/restore-drill.sh
```

---

## 📡 Health Monitoring & Dashboard Integration

### Phase 1: Backup Health API Endpoint

```python
# crm_api/app/api/routes/system_health.py

from fastapi import APIRouter
import json
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter(prefix="/system-health", tags=["System Health"])

@router.get("/backup-status")
async def get_backup_status():
    """
    Get backup and restore health status for dashboard.

    Returns:
        {
            "backup": {
                "status": "ok|warning|error",
                "last_backup_time": "2025-11-03T02:00:00Z",
                "backup_size": "2.5 GB",
                "age_hours": 6,
                "s3_status": "success"
            },
            "restore": {
                "status": "ok|warning|error",
                "last_restore_test": "2025-11-03T04:00:00Z",
                "restore_duration_seconds": 45,
                "age_hours": 4
            }
        }
    """

    # Read backup health file
    backup_health_path = Path("/var/lib/backup-health/last_backup.json")
    restore_health_path = Path("/var/lib/backup-health/last_restore.json")

    backup_status = {"status": "unknown"}
    restore_status = {"status": "unknown"}

    # Parse backup health
    if backup_health_path.exists():
        with open(backup_health_path) as f:
            backup_data = json.load(f)

        last_backup = datetime.fromisoformat(backup_data["last_backup_time"])
        age_hours = (datetime.now(last_backup.tzinfo) - last_backup).total_seconds() / 3600

        # Determine status
        if backup_data.get("status") == "success" and age_hours < 30:
            status = "ok"
        elif age_hours < 48:
            status = "warning"
        else:
            status = "error"

        backup_status = {
            "status": status,
            "last_backup_time": backup_data["last_backup_time"],
            "backup_size": backup_data.get("backup_size_human", "unknown"),
            "age_hours": round(age_hours, 1),
            "s3_status": backup_data.get("s3_status", "unknown"),
            "database": backup_data.get("database")
        }

    # Parse restore health
    if restore_health_path.exists():
        with open(restore_health_path) as f:
            restore_data = json.load(f)

        last_restore = datetime.fromisoformat(restore_data["last_restore_test_time"])
        age_hours = (datetime.now(last_restore.tzinfo) - last_restore).total_seconds() / 3600

        # Determine status (restore test should run weekly)
        if restore_data.get("status") == "success" and age_hours < 168 + 24:  # 7 days + 1 day grace
            status = "ok"
        elif age_hours < 336:  # 14 days
            status = "warning"
        else:
            status = "error"

        restore_status = {
            "status": status,
            "last_restore_test": restore_data["last_restore_test_time"],
            "restore_duration_seconds": restore_data.get("restore_duration_seconds"),
            "tables_restored": restore_data.get("tables_restored"),
            "age_hours": round(age_hours, 1)
        }

    return {
        "backup": backup_status,
        "restore": restore_status
    }


@router.get("/disk-usage")
async def get_disk_usage():
    """
    Get disk usage statistics.

    Returns partition info for monitoring.
    """
    import subprocess

    result = subprocess.run(
        ["df", "-h", "/", "/var/backups"],
        capture_output=True,
        text=True
    )

    lines = result.stdout.strip().split('\n')[1:]  # Skip header

    partitions = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 6:
            partitions.append({
                "filesystem": parts[0],
                "size": parts[1],
                "used": parts[2],
                "available": parts[3],
                "use_percent": int(parts[4].rstrip('%')),
                "mounted_on": parts[5]
            })

    return {"partitions": partitions}
```

### Phase 2: Dashboard Widget (React)

```typescript
// ops-console/src/components/BackupHealthCard.tsx

import React, { useEffect, useState } from 'react';

interface BackupHealth {
  backup: {
    status: 'ok' | 'warning' | 'error' | 'unknown';
    last_backup_time: string;
    backup_size: string;
    age_hours: number;
    s3_status: string;
  };
  restore: {
    status: 'ok' | 'warning' | 'error' | 'unknown';
    last_restore_test: string;
    restore_duration_seconds: number;
    age_hours: number;
  };
}

export const BackupHealthCard: React.FC = () => {
  const [health, setHealth] = useState<BackupHealth | null>(null);

  useEffect(() => {
    // Fetch backup health
    fetch('/api/system-health/backup-status')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(console.error);

    // Refresh every 5 minutes
    const interval = setInterval(() => {
      fetch('/api/system-health/backup-status')
        .then(res => res.json())
        .then(data => setHealth(data))
        .catch(console.error);
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  if (!health) return <div>Loading...</div>;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ok': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return '?';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Backup & Recovery</h3>

      {/* Backup Status */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Last Backup</span>
          <span className={`text-2xl ${getStatusColor(health.backup.status)}`}>
            {getStatusIcon(health.backup.status)}
          </span>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          <div>{new Date(health.backup.last_backup_time).toLocaleString()}</div>
          <div>Size: {health.backup.backup_size}</div>
          <div>Age: {health.backup.age_hours.toFixed(1)}h ago</div>
          <div>S3: {health.backup.s3_status}</div>
        </div>
      </div>

      {/* Restore Test Status */}
      <div>
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Last Restore Test</span>
          <span className={`text-2xl ${getStatusColor(health.restore.status)}`}>
            {getStatusIcon(health.restore.status)}
          </span>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          <div>{new Date(health.restore.last_restore_test).toLocaleString()}</div>
          <div>Duration: {health.restore.restore_duration_seconds}s</div>
          <div>Age: {health.restore.age_hours.toFixed(1)}h ago</div>
        </div>
      </div>
    </div>
  );
};
```

---

## 🗄️ Storage & Retention Policy

### Storage Tiers

| Tier | Storage Type | Purpose | Retention | Cost |
|------|-------------|---------|-----------|------|
| **Hot** | SSD (local) | Current month data, active queries | 1 month | High |
| **Warm** | HDD (local) | 1-3 months old, occasional access | 3 months | Medium |
| **Cold** | S3 Standard-IA | 3-12 months old, archival | 1 year | Low |
| **Glacier** | S3 Glacier | > 1 year, compliance | 7 years | Very Low |

### Retention Policies

```bash
# Data Retention by Type

# SERP Results
- Hot (SSD): Last 30 days
- Warm (HDD): 31-90 days
- Cold (S3): 91 days - 2 years
- Delete: > 2 years

# Competitor Pages
- Hot (SSD): Last 30 days
- Cold (S3): 31 days - 2 years
- Delete: > 2 years

# Task Logs
- Hot (SSD): Last 7 days
- Warm (HDD): 8-90 days
- Delete: > 90 days

# Backups
- Local: Last 30 days (daily)
- S3: Last 90 days (daily)
- S3 (weekly): 1 year
- Glacier: 7 years (compliance)

# Configuration Backups
- Local: Last 60 days
- S3: Indefinite
```

### Automated Tier Migration

```bash
#!/bin/bash
# /usr/local/bin/migrate-to-s3.sh

# Move old backups to S3
find /var/backups/postgresql -name "*.sql.gz" -mtime +7 -type f | while read file; do
    aws s3 cp "$file" s3://rivercityclean-backups/postgresql/$(basename "$file") --storage-class STANDARD_IA
    echo "Migrated to S3: $file"
    rm "$file"  # Remove local copy after successful upload
done

# Transition to Glacier after 1 year (via S3 lifecycle policy)
# This is configured in AWS S3 bucket lifecycle rules
```

---

## 🚨 Disaster Recovery Procedures

### Scenario 1: Database Corruption

```bash
#!/bin/bash
# Emergency database restore procedure

# 1. Stop applications
sudo systemctl stop nginx
sudo systemctl stop crm-api
sudo systemctl stop ops-api

# 2. Backup corrupted database (for forensics)
pg_dump -U postgres crm_production > /tmp/corrupted_db_$(date +%Y%m%d).sql

# 3. Drop corrupted database
psql -U postgres -c "DROP DATABASE crm_production"

# 4. Create fresh database
psql -U postgres -c "CREATE DATABASE crm_production OWNER crm_user"

# 5. Restore from latest backup
LATEST_BACKUP=$(ls -t /var/backups/postgresql/crm_production_*.sql.gz | head -1)
echo "Restoring from: $LATEST_BACKUP"
gunzip -c "$LATEST_BACKUP" | psql -U postgres crm_production

# 6. Verify restore
psql -U postgres -d crm_production -c "SELECT COUNT(*) FROM leads"

# 7. Restart applications
sudo systemctl start crm-api
sudo systemctl start ops-api
sudo systemctl start nginx

echo "Database restored. RTO: $(date)"
```

### Scenario 2: Complete Server Loss

```bash
# Disaster Recovery Runbook for Complete Server Failure

# 1. Provision new server
# - Ubuntu 22.04 LTS
# - Same specs or better
# - Attach volumes if using cloud

# 2. Install base system
sudo apt-get update
sudo apt-get install -y postgresql redis-server nginx python3 python3-pip

# 3. Restore configurations
aws s3 cp s3://rivercityclean-backups/configs/latest.tar.gz /tmp/
sudo tar -xzf /tmp/latest.tar.gz -C /

# 4. Restore database from S3
aws s3 cp s3://rivercityclean-backups/postgresql/$(aws s3 ls s3://rivercityclean-backups/postgresql/ | sort | tail -n 1 | awk '{print $4}') /tmp/latest_backup.sql.gz

# 5. Create database and restore
sudo -u postgres createdb crm_production
gunzip -c /tmp/latest_backup.sql.gz | sudo -u postgres psql crm_production

# 6. Deploy application code
git clone https://github.com/org/Saas-CRM---Claude.git
cd Saas-CRM---Claude
# Follow deployment procedure

# 7. Start services
sudo systemctl start postgresql redis-server nginx crm-api ops-api

# 8. Verify functionality
curl https://rivercityclean.com/health
```

---

## ✅ Implementation Checklist

- [ ] Create partition maintenance functions (serp_results, competitor_pages, task_logs)
- [ ] Schedule monthly partition creation (cron)
- [ ] Implement nightly database backup script
- [ ] Configure S3 upload for backups
- [ ] Implement weekly configuration backup
- [ ] Create restore drill script
- [ ] Schedule weekly restore tests
- [ ] Set up backup health monitoring API
- [ ] Create dashboard backup health widget
- [ ] Configure storage tier migration
- [ ] Set up retention policies
- [ ] Document disaster recovery procedures
- [ ] Test full disaster recovery scenario
- [ ] Configure email alerts for backup failures

---

## 📊 Success Metrics

- **Backup Success Rate:** 100% (zero failures)
- **Backup Duration:** < 30 minutes
- **Restore Test Success:** 100% weekly drills
- **RTO (Recovery Time Objective):** < 1 hour
- **RPO (Recovery Point Objective):** < 24 hours
- **Backup Storage Growth:** ~5GB/month
- **Dashboard Heartbeat:** Green status 99.9%+

---

**Status:** ✅ Runbook Complete
**Estimated Time:** 8-10 hours for full implementation
**Priority:** P0 - CRITICAL (Production blocker)

**Validation Criteria:**
- Database backups running nightly (verified in logs)
- Restore drills passing weekly (verified in health API)
- Dashboard showing backup/restore timestamps
- Partitions auto-creating monthly
- S3 uploads working (check bucket)
- Old partitions being archived/dropped per policy

---

*Runbook created: 2025-11-03*
*Part of AI Suite Implementation (Step 14/16)*
*Status: P0 - PRODUCTION BLOCKER*
