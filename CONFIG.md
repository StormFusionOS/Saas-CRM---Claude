# Configuration Contract

This document defines all required and optional environment variables, their formats, validation rules, and security requirements.

## 📋 Configuration Overview

All configuration is managed via environment variables loaded from `.env` files. The monorepo provides:

- **`.env.example`** - Template with safe defaults for local development
- **`tools/config/sanity.py`** - Configuration validator
- **`scripts/config/check.sh`** - Unified security check (config + secrets scan)

## 🔒 Security Requirements

### Development vs Production

| Environment | Requirements |
|-------------|--------------|
| **Development** | Placeholders allowed, warnings for weak secrets |
| **Production** | All secrets must be strong, no placeholders, strict validation |

### Validation Rules

Configuration is validated for:
- ✅ **Existence**: Required variables must be set
- ✅ **Format**: URLs, ports, and secrets must match expected patterns
- ✅ **Length**: Secrets must meet minimum length requirements
- ✅ **Placeholders**: Production mode rejects placeholder values
- ✅ **Pattern Matching**: Specific formats (URLs, database strings, etc.)

## 📝 Required Variables

### JWT Secrets

| Variable | Required | Min Length | Description | Example |
|----------|----------|------------|-------------|---------|
| `CRM_SECRET_KEY` | ✅ | 32 chars | JWT signing secret for CRM API | `<random-32+-char-string>` |
| `OPS_SECRET_KEY` | ✅ | 32 chars | JWT signing secret for Ops API | `<random-32+-char-string>` |
| `CRM_ACCESS_TOKEN_EXPIRE` | ✅ | - | Access token TTL in seconds | `900` (15 minutes) |
| `CRM_REFRESH_TOKEN_EXPIRE` | ✅ | - | Refresh token TTL in seconds | `604800` (7 days) |
| `OPS_ACCESS_TOKEN_EXPIRE` | ✅ | - | Access token TTL in seconds | `900` |
| `OPS_REFRESH_TOKEN_EXPIRE` | ✅ | - | Refresh token TTL in seconds | `604800` |

**Security Notes:**
- Must be cryptographically random in production
- Never commit actual secrets to git
- Rotate regularly (every 90 days recommended)
- Use different secrets for CRM and Ops APIs

**Generate secure secrets:**
```bash
# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# OpenSSL
openssl rand -base64 32
```

### Database Configuration

#### CRM Database

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `CRM_DB_HOST` | ✅ | hostname/IP | Database host | `localhost` or `crm-db.example.com` |
| `CRM_DB_PORT` | ✅ | 1-65535 | Database port | `5433` |
| `CRM_DB_NAME` | ✅ | string | Database name | `crm` |
| `CRM_DB_USER` | ✅ | string | Database user | `crm_user` |
| `CRM_DB_PASSWORD` | ✅ | 8+ chars | Database password | `<secure-password>` |

#### Ops Database

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `OPS_DB_HOST` | ✅ | hostname/IP | Database host | `localhost` or `ops-db.example.com` |
| `OPS_DB_PORT` | ✅ | 1-65535 | Database port | `5434` |
| `OPS_DB_NAME` | ✅ | string | Database name | `ops` |
| `OPS_DB_USER` | ✅ | string | Database user | `ops_user` |
| `OPS_DB_PASSWORD` | ✅ | 8+ chars | Database password | `<secure-password>` |

#### Connection Pool Settings

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_POOL_SIZE` | ❌ | `5` | Connection pool size |
| `DB_MAX_OVERFLOW` | ❌ | `10` | Max overflow connections |

**Database URL Format:**
```
postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}
```

### Redis Configuration

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `REDIS_HOST` | ✅ | hostname/IP | Redis host | `localhost` |
| `REDIS_PORT` | ✅ | 1-65535 | Redis port | `6379` |
| `REDIS_DB` | ✅ | integer | Redis database number | `0` |
| `REDIS_PASSWORD` | ❌ | string | Redis password (if auth enabled) | `<redis-password>` |

**Redis URL Format:**
```
redis://:{PASSWORD}@{HOST}:{PORT}/{DB}  # With password
redis://{HOST}:{PORT}/{DB}              # Without password
```

### API Configuration

#### CRM API

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `CRM_API_HOST` | ✅ | IP/hostname | API bind address | `0.0.0.0` |
| `CRM_API_PORT` | ✅ | 1-65535 | API port | `8000` |
| `CRM_API_PREFIX` | ✅ | string | API URL prefix | `/api/v1` |
| `CRM_API_DEBUG` | ❌ | `true`/`false` | Debug mode | `false` in production |
| `CRM_CORS_ORIGINS` | ✅ | comma-separated URLs | Allowed CORS origins | `https://crm.example.com` |

#### Ops API

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `OPS_API_HOST` | ✅ | IP/hostname | API bind address | `0.0.0.0` |
| `OPS_API_PORT` | ✅ | 1-65535 | API port | `8001` |
| `OPS_API_PREFIX` | ✅ | string | API URL prefix | `/api/v1` |
| `OPS_API_DEBUG` | ❌ | `true`/`false` | Debug mode | `false` in production |
| `OPS_CORS_ORIGINS` | ✅ | comma-separated URLs | Allowed CORS origins | `https://ops.example.com` |

### Frontend Configuration

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `VITE_CRM_API_URL` | ✅ | http(s):// URL | CRM API base URL | `http://localhost:8000/api/v1` |
| `VITE_OPS_API_URL` | ✅ | http(s):// URL | Ops API base URL | `http://localhost:8001/api/v1` |

**Note:** Vite variables are embedded at build time, not runtime.

### Celery Configuration

| Variable | Required | Format | Description | Example |
|----------|----------|--------|-------------|---------|
| `CELERY_BROKER_URL` | ✅ | redis:// or amqp:// | Broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | ✅ | redis:// URL | Result backend | `redis://localhost:6379/0` |
| `CELERY_TASK_SERIALIZER` | ❌ | string | Task serializer | `json` |
| `CELERY_RESULT_SERIALIZER` | ❌ | string | Result serializer | `json` |
| `CELERY_ACCEPT_CONTENT` | ❌ | string | Accepted content types | `json` |
| `CELERY_TIMEZONE` | ❌ | timezone | Celery timezone | `UTC` |
| `CELERY_ENABLE_UTC` | ❌ | `true`/`false` | Use UTC | `true` |

## 🔌 Webhook Secrets (Optional)

These are required only if you're using the respective integrations:

| Variable | Required | Description | How to Obtain |
|----------|----------|-------------|---------------|
| `TWILIO_AUTH_TOKEN` | ❌ | Twilio webhook auth token | Twilio Console → Account → Auth Token |
| `TWILIO_ACCOUNT_SID` | ❌ | Twilio account SID | Twilio Console → Account → SID |
| `FB_APP_SECRET` | ❌ | Facebook app secret | Facebook Developer → App → Settings → Basic |
| `FB_VERIFY_TOKEN` | ❌ | Facebook verify token | Custom string you define |
| `GOOGLE_WEBHOOK_SECRET` | ❌ | Google webhook secret | Google Ads → Conversions → Webhook |

**Security Notes:**
- Never log or display these secrets
- Validate webhook signatures on every request
- Rotate periodically or if compromised

## 📧 Email Configuration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SMTP_HOST` | ❌ | `localhost` | SMTP server host |
| `SMTP_PORT` | ❌ | `1025` | SMTP server port |
| `SMTP_USER` | ❌ | `""` | SMTP username |
| `SMTP_PASSWORD` | ❌ | `""` | SMTP password |
| `SMTP_FROM` | ❌ | `noreply@example.com` | From address |
| `SMTP_TLS` | ❌ | `false` | Use TLS |

## 🔍 Logging & Monitoring

| Variable | Required | Default | Description | Options |
|----------|----------|---------|-------------|---------|
| `LOG_LEVEL` | ❌ | `INFO` | Logging level | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOG_FORMAT` | ❌ | `json` | Log format | `json`, `text` |
| `SENTRY_DSN` | ❌ | `""` | Sentry DSN for error tracking | `https://...@sentry.io/...` |

## 🛡️ Security & Rate Limiting

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `RATE_LIMIT_ENABLED` | ❌ | `true` | Enable rate limiting |
| `RATE_LIMIT_PER_MINUTE` | ❌ | `60` | Requests per minute |
| `FILE_INTEGRITY_PATHS` | ❌ | `/etc/nginx,/var/www` | Paths to monitor (comma-separated) |

## 💾 Backup Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKUP_ENABLED` | ❌ | `true` | Enable automated backups |
| `BACKUP_RETENTION_DAYS` | ❌ | `30` | Days to retain backups |
| `BACKUP_SCHEDULE` | ❌ | `0 2 * * *` | Cron schedule |

## 🤖 AI/ML Configuration (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_PROVIDER` | ❌ | `openai` | AI provider |
| `AI_API_KEY` | ❌ | `""` | API key for AI provider |
| `AI_MODEL` | ❌ | `gpt-4` | Model name |
| `AI_TEMPERATURE` | ❌ | `0.7` | Temperature (0.0-1.0) |
| `AI_MAX_TOKENS` | ❌ | `1000` | Max tokens per request |
| `AI_SUGGESTIONS_ENABLED` | ❌ | `false` | Enable AI suggestions |
| `AUTO_REPLY_ENABLED` | ❌ | `false` | Enable auto-replies |

## 🚀 Usage

### Validate Configuration

Run the configuration validator before deploying:

```bash
# Validate .env file (dev mode)
python3 tools/config/sanity.py

# Validate for production
MODE=prod python3 tools/config/sanity.py

# Run full security check (config + secrets scan)
./scripts/config/check.sh

# Check specific env file
./scripts/config/check.sh /path/to/.env
```

### Expected Output

**Success:**
```
====================================================================================================
Configuration Validation Report - Mode: DEV
====================================================================================================
Environment File: .env.example

Variable                            Status          Message
----------------------------------------------------------------------------------------------------
CRM_SECRET_KEY                      ⚠ Placeholder   Appears to be a placeholder value
OPS_SECRET_KEY                      ⚠ Placeholder   Appears to be a placeholder value
CRM_DB_HOST                         ✓ Found         CRM database host
...

Summary: 35/38 variables OK | 0 errors | 3 warnings

⚠ VALIDATION PASSED WITH WARNINGS - Review before deploying
```

**Failure (Production):**
```
====================================================================================================
Configuration Validation Report - Mode: PROD
====================================================================================================
Environment File: .env

Variable                            Status          Message
----------------------------------------------------------------------------------------------------
CRM_SECRET_KEY                      ✗ Placeholder   Placeholder value not allowed in production
...

Summary: 20/38 variables OK | 5 errors | 0 warnings

✗ VALIDATION FAILED - Fix errors before deploying to production
```

### Pre-commit Hooks

The `.pre-commit-config.yaml` includes secret detection:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

**Blocked Patterns:**
- AWS credentials (`AKIA...`, `aws_access_key_id`, etc.)
- Private keys (`-----BEGIN PRIVATE KEY-----`)
- API keys and tokens (32+ char secrets)
- GitHub tokens (`ghp_...`, `gho_...`, etc.)
- Slack tokens (`xox...`)
- Stripe keys (`sk_live_...`, `pk_live_...`)
- JWT tokens (full encoded tokens)
- Database connection strings with passwords

## ❌ Common Pitfalls

### 1. Using Placeholders in Production

**❌ Wrong:**
```bash
CRM_SECRET_KEY=crm-dev-secret-key-change-in-production-min-32-chars
```

**✅ Correct:**
```bash
CRM_SECRET_KEY=8mF2jK9pL3nQ7rS1tV4wX6yZ0aB2cD4eF5gH7iJ8kL9mN0oP1qR2sT3uV4wX5yZ6
```

### 2. Weak Secrets

**❌ Wrong:**
```bash
CRM_DB_PASSWORD=password123
```

**✅ Correct:**
```bash
CRM_DB_PASSWORD=xK9$mP2#vL8@nQ4!rS7*wT5&yU3
```

### 3. Hardcoding URLs

**❌ Wrong:**
```python
API_URL = "http://localhost:8000"
```

**✅ Correct:**
```python
API_URL = os.getenv("VITE_CRM_API_URL")
```

### 4. Committing .env Files

**❌ Wrong:**
```bash
git add .env
git commit -m "Add config"
```

**✅ Correct:**
```bash
# .env is in .gitignore
# Only commit .env.example
git add .env.example
```

### 5. Localhost in Production

**❌ Wrong:**
```bash
CRM_DB_HOST=localhost
VITE_CRM_API_URL=http://localhost:8000/api/v1
```

**✅ Correct:**
```bash
CRM_DB_HOST=crm-db-prod.internal
VITE_CRM_API_URL=https://api.crm.example.com/api/v1
```

## 🔄 Secret Rotation

Rotate secrets regularly to minimize security risk:

### JWT Secrets (Every 90 Days)

```bash
# Generate new secret
NEW_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Update .env
sed -i "s/^CRM_SECRET_KEY=.*/CRM_SECRET_KEY=$NEW_SECRET/" .env

# Restart services
docker-compose restart crm-api
```

### Database Passwords (Every 90 Days)

```sql
-- Connect to database
psql -U postgres -h localhost

-- Change password
ALTER USER crm_user WITH PASSWORD 'new-secure-password';

-- Update .env
-- Restart services
```

### Webhook Secrets (On Compromise)

1. Generate new secret in provider console
2. Update `.env` file
3. Restart API services
4. Update webhook configuration in provider

## 📚 References

- [Twelve-Factor App: Config](https://12factor.net/config)
- [OWASP: Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [NIST: Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)

## 🆘 Troubleshooting

### Validation Fails with "Missing Required Variable"

**Solution:** Add the variable to your `.env` file:
```bash
echo "MISSING_VARIABLE=value" >> .env
```

### Pre-commit Hook Blocks Commit

**Solution:** Review the blocked pattern. If it's a false positive, update the exclusion list in `.pre-commit-config.yaml`.

### Variables Not Loading

**Solution:** Ensure `.env` is in the project root and sourced:
```bash
# Check file exists
ls -la .env

# Manually source (for testing)
set -a && source .env && set +a
```

---

**Last Updated:** 2025-11-02
**Validator Version:** 1.0.0
