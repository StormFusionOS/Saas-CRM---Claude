# Database Management Scripts

Unified database migration, seeding, and rollback tools for CRM and Ops APIs.

## 📋 Table of Contents

- [Overview](#overview)
- [Scripts](#scripts)
- [Usage](#usage)
- [Seeded Data](#seeded-data)
- [Schema Drift Detection](#schema-drift-detection)
- [Troubleshooting](#troubleshooting)

## Overview

This directory contains Python scripts for managing database migrations, seeding demo data, and rolling back changes across the CRM and Ops APIs. All scripts work with both stub (test) and production (real SQLAlchemy + Alembic) environments.

## Scripts

### 1. `migrate.py` - Migration Management

Wrapper for Alembic migrations with unified interface for both services.

**Commands:**
- `upgrade` - Apply migrations
- `current` - Show current revision
- `history` - Show migration history
- `create` - Create new migration

**Examples:**
```bash
# Upgrade both services to latest
python3 scripts/db/migrate.py upgrade all

# Upgrade specific service
python3 scripts/db/migrate.py upgrade crm

# Show current revision
python3 scripts/db/migrate.py current all

# Show migration history
python3 scripts/db/migrate.py history crm --count 5

# Create new migration
python3 scripts/db/migrate.py create crm -m "add user preferences"

# Dry run (print without executing)
python3 scripts/db/migrate.py upgrade all --dry-run
```

### 2. `seed.py` - Demo Data Seeding

Seeds minimal demo datasets for testing and demos.

**CRM Data:**
- 10 Contacts (varied companies and titles)
- 8 Leads (NEW, CONTACTED, QUALIFIED, WON, LOST)
- 1-3 Interactions per lead (EMAIL, SMS, PHONE, MEETING, NOTE, WEBHOOK)

**Ops Data:**
- 5 Task runs (backup, health check, AI suggestions, file integrity, cleanup)
- 3 Backup runs (1 full, 2 incremental)
- 1 Anomaly alert → 1 AI suggestion workflow
- 5 Service health checks (all healthy)

**Examples:**
```bash
# Seed all services (NOTE: Run separately to avoid module conflicts)
python3 scripts/db/seed.py crm
python3 scripts/db/seed.py ops

# Seed with verbose output
python3 scripts/db/seed.py crm -v
python3 scripts/db/seed.py ops -v
```

**Important:** Seed CRM and Ops separately to avoid Python module caching conflicts.

### 3. `rollback.py` - Migration Rollback

Safely rolls back database migrations with confirmation prompts.

**Examples:**
```bash
# Rollback 1 revision (with confirmation)
python3 scripts/db/rollback.py crm

# Rollback multiple revisions
python3 scripts/db/rollback.py crm --steps 2

# Rollback to specific revision
python3 scripts/db/rollback.py crm --to 202401010001

# Rollback without confirmation
python3 scripts/db/rollback.py crm --yes

# Dry run (show what would happen)
python3 scripts/db/rollback.py crm --dry-run

# Rollback all services
python3 scripts/db/rollback.py all --yes
```

**Safety Features:**
- Interactive confirmation prompt (unless `--yes` provided)
- Shows migration history before rollback
- Displays current and target revisions
- Warns about potential data loss

## Usage

### Full Workflow Example

```bash
# 1. Check for schema drift
python3 tools/check_migrations.py

# 2. Create migration if needed
python3 scripts/db/migrate.py create crm -m "add new columns"

# 3. Review generated migration file
cat crm_api/alembic/versions/<new_migration>.py

# 4. Apply migrations
python3 scripts/db/migrate.py upgrade all

# 5. Seed demo data
python3 scripts/db/seed.py crm
python3 scripts/db/seed.py ops

# 6. Verify data
# (Run API and check endpoints)

# 7. If issues, rollback
python3 scripts/db/rollback.py crm --yes
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Check schema drift
  run: python3 tools/check_migrations.py

- name: Run migrations
  run: python3 scripts/db/migrate.py upgrade all

- name: Seed test data
  run: |
    python3 scripts/db/seed.py crm
    python3 scripts/db/seed.py ops

- name: Run tests
  run: pytest

- name: Rollback (cleanup)
  run: python3 scripts/db/rollback.py all --yes
  if: always()
```

## Seeded Data

### CRM API

**Contacts (10):**
| ID | Name | Company | Email | Phone |
|----|------|---------|-------|-------|
| 1 | Alice Johnson | TechStart Inc | alice.johnson@example.com | +1-555-0101 |
| 2 | Bob Smith | Acme Corp | bob.smith@acme.com | +1-555-0102 |
| 3 | Carol Davis | Innovate.io | carol.davis@innovate.io | +1-555-0103 |
| 4 | David Wilson | Enterprise LLC | david.wilson@enterprise.com | +1-555-0104 |
| 5 | Emma Martinez | Startup.co | emma.martinez@startup.co | +1-555-0105 |
| ... | ... | ... | ... | ... |

**Leads (8):**
| ID | Contact | Status | Source | Value | Probability |
|----|---------|--------|--------|-------|-------------|
| 1 | Alice | NEW | FACEBOOK | $15,234 | 10% |
| 2 | Bob | NEW | GOOGLE | $28,450 | 10% |
| 3 | Carol | CONTACTED | TWILIO | $42,100 | 25% |
| 4 | David | CONTACTED | MANUAL | $19,875 | 25% |
| 5 | Emma | CONTACTED | FACEBOOK | $31,620 | 25% |
| 6 | Frank | QUALIFIED | GOOGLE | $48,900 | 60% |
| 7 | Grace | WON | MANUAL | $55,200 | 100% |
| 8 | Henry | LOST | TWILIO | - | 0% |

**Interactions (16-19):**
- 1-3 interactions per lead
- Types: EMAIL, SMS, PHONE, MEETING, NOTE, WEBHOOK
- Directions: INBOUND, OUTBOUND
- Created over last 30 days

### Ops API

**Task Runs (5):**
| ID | Task Name | Status | Duration | Result |
|----|-----------|--------|----------|--------|
| 1 | backup_databases | completed | 120.5s | 3 files, 450 MB |
| 2 | check_service_health | completed | 5.2s | 8 services, all healthy |
| 3 | generate_ai_suggestions | completed | 45.8s | 3 suggestions, GPT-4 |
| 4 | scan_file_integrity | completed | 30.1s | 1250 files, 1 anomaly |
| 5 | cleanup_old_logs | running | 0s | - |

**Backup Runs (3):**
| ID | Type | Status | Size | Location |
|----|------|--------|------|----------|
| 1 | full | completed | 1250.5 MB | s3://backups/full/2025-11-01.tar.gz |
| 2 | incremental | completed | 85.2 MB | s3://backups/incremental/2025-11-02.tar.gz |
| 3 | incremental | completed | 92.8 MB | s3://backups/incremental/2025-11-02-2.tar.gz |

**Anomaly → Suggestion Workflow (1):**
- **Alert #1**: File integrity check detected modified configuration file
  - Severity: warning
  - Source: file_integrity_scanner
  - Created: 2 hours ago

- **Suggestion #1**: Review configuration file changes
  - Type: security
  - Priority: high
  - Description: AI detected unauthorized changes to /etc/nginx/nginx.conf
  - Status: pending
  - Linked to Alert #1

**Service Health (5):**
| ID | Service | Status | Response Time |
|----|---------|--------|---------------|
| 1 | crm-api | healthy | 45.2 ms |
| 2 | ops-api | healthy | 38.1 ms |
| 3 | redis | healthy | 2.5 ms |
| 4 | postgres-crm | healthy | 12.3 ms |
| 5 | postgres-ops | healthy | 11.8 ms |

## Schema Drift Detection

The `tools/check_migrations.py` script detects when models have been changed without creating migrations.

**What it checks:**
1. ✅ Migration files exist
2. ✅ Revision chain is valid (no duplicates, proper down_revision links)
3. ✅ All models have corresponding migrations
4. ⚠️  Orphaned migrations (tables in migrations but not models)

**Example output:**
```
================================================================================
Checking CRM API migrations
================================================================================
✓ Found 2 migration files

Checking revision chain...
✓ Found 2 unique revisions
✓ Found 1 migration head(s)

Checking for schema drift...
✓ Found 5 models: auto_reply_rules, contacts, interactions, leads, users
✓ Found 5 tables in migrations: auto_reply_rules, contacts, interactions, leads, users
✓ No schema drift detected

✅ CRM API migration checks passed
```

**If drift detected:**
```
❌ Models without migrations: contacts, interactions, leads
   Run: python3 scripts/db/migrate.py create crm -m 'Add missing tables'
```

## Troubleshooting

### Issue: "Module not found" errors during seeding

**Solution:** Seed services separately, not with `all`:
```bash
# ✗ Wrong (module conflicts)
python3 scripts/db/seed.py all

# ✓ Correct
python3 scripts/db/seed.py crm
python3 scripts/db/seed.py ops
```

### Issue: "Alembic not found"

**Solution:** This is expected in stub mode. Scripts work with or without Alembic:
```bash
# Install for production use
pip install alembic sqlalchemy psycopg2-binary

# Or use stub mode (no database required)
# Scripts will show ⚠️  warnings but still function
```

### Issue: Schema drift detected after model changes

**Solution:** Create a new migration:
```bash
# 1. Check what changed
python3 tools/check_migrations.py

# 2. Create migration
python3 scripts/db/migrate.py create crm -m "describe changes"

# 3. Review and edit migration file if needed
nano crm_api/alembic/versions/<new_file>.py

# 4. Apply migration
python3 scripts/db/migrate.py upgrade crm
```

### Issue: Need to undo a migration

**Solution:** Use rollback:
```bash
# Rollback 1 revision
python3 scripts/db/rollback.py crm

# Or rollback to specific point
python3 scripts/db/rollback.py crm --to <revision_id>
```

### Issue: Lost track of migration state

**Solution:** Check current revision:
```bash
# Show current
python3 scripts/db/migrate.py current all

# Show history
python3 scripts/db/migrate.py history all
```

## Best Practices

### Development Workflow

1. **Before making model changes:**
   ```bash
   python3 tools/check_migrations.py  # Verify clean state
   ```

2. **After changing models:**
   ```bash
   python3 scripts/db/migrate.py create <service> -m "description"
   ```

3. **Review generated migration:**
   - Check SQL operations (create_table, add_column, etc.)
   - Verify downgrade() is correct
   - Test rollback works

4. **Test locally:**
   ```bash
   python3 scripts/db/migrate.py upgrade <service>  # Apply
   python3 scripts/db/seed.py <service>             # Seed
   # Run tests
   python3 scripts/db/rollback.py <service> --yes  # Rollback
   ```

5. **Commit migration file:**
   ```bash
   git add <service>_api/alembic/versions/<new_migration>.py
   git commit -m "feat: add <description> migration"
   ```

### Production Deployment

1. **Backup database first:**
   ```bash
   pg_dump -Fc crm > backup_$(date +%Y%m%d).dump
   ```

2. **Run migrations in transaction:**
   - Alembic uses transactions by default
   - Monitor for errors
   - Have rollback plan ready

3. **Verify after migration:**
   ```bash
   python3 scripts/db/migrate.py current all
   python3 tools/check_migrations.py
   ```

4. **If issues, rollback immediately:**
   ```bash
   python3 scripts/db/rollback.py <service> --yes
   # Restore from backup if needed
   ```

## File Locations

```
scripts/db/
├── README.md              # This file
├── migrate.py            # Migration management (upgrade, current, history, create)
├── rollback.py           # Rollback management (downgrade)
└── seed.py               # Demo data seeding

tools/
└── check_migrations.py   # Schema drift detection

crm_api/
├── alembic/
│   ├── versions/         # Migration files
│   ├── env.py           # Alembic environment config
│   └── alembic.ini      # Alembic configuration
└── app/
    ├── db.py            # In-memory database (stub)
    ├── models.py        # Dataclass models
    └── db_models.py     # SQLAlchemy models (for migrations)

ops_api/
└── app/
    ├── db.py            # In-memory database (stub)
    └── models/          # Dataclass models
```

## Related Documentation

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Migration Best Practices](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

**Last Updated:** 2025-11-02
**Version:** 1.0.0
