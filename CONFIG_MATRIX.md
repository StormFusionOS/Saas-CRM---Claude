# Configuration Matrix

## Overview

This document defines all environment variables required across development, staging, and production environments. Use this as a reference to ensure proper configuration and avoid "environment foot-guns."

## Environment Matrix

| Variable | Dev | Staging | Prod | Required | Default | Description |
|----------|-----|---------|------|----------|---------|-------------|
| **General** |
| `ENVIRONMENT` | `dev` | `staging` | `prod` | ✅ | `dev` | Runtime environment identifier |
| `DEBUG` | `true` | `false` | `false` | ✅ | `false` | Enable debug mode (verbose logs, stack traces) |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `WARNING` | ✅ | `INFO` | Logging verbosity |
| **CRM API** |
| `CRM_API_HOST` | `0.0.0.0` | `0.0.0.0` | `0.0.0.0` | ✅ | `0.0.0.0` | CRM API bind host |
| `CRM_API_PORT` | `8000` | `8000` | `8000` | ✅ | `8000` | CRM API port |
| `CRM_API_PREFIX` | `/api` | `/api` | `/api` | ✅ | `/api` | API route prefix |
| `CRM_CORS_ORIGINS` | `http://localhost:5173,http://localhost:5174` | `https://staging-crm.example.com` | `https://crm.example.com` | ✅ | `*` | Allowed CORS origins (comma-separated) |
| **Ops Console API** |
| `OPS_API_HOST` | `0.0.0.0` | `0.0.0.0` | `0.0.0.0` | ✅ | `0.0.0.0` | Ops API bind host |
| `OPS_API_PORT` | `8001` | `8001` | `8001` | ✅ | `8001` | Ops API port |
| `OPS_API_PREFIX` | `/api` | `/api` | `/api` | ✅ | `/api` | API route prefix |
| `OPS_CORS_ORIGINS` | `http://localhost:5173,http://localhost:5174` | `https://staging-ops.example.com` | `https://ops.example.com` | ✅ | `*` | Allowed CORS origins (comma-separated) |
| **Authentication** |
| `SECRET_KEY` | `dev-secret-key-change-in-prod` | `(from secrets manager)` | `(from secrets manager)` | ✅ | ❌ REQUIRED | JWT signing secret (must be cryptographically random in prod) |
| `ACCESS_TOKEN_EXPIRE_SECONDS` | `3600` | `1800` | `900` | ✅ | `3600` | JWT access token lifetime (seconds) |
| `REFRESH_TOKEN_EXPIRE_SECONDS` | `86400` | `86400` | `604800` | ✅ | `86400` | JWT refresh token lifetime (seconds) |
| `PASSWORD_MIN_LENGTH` | `6` | `8` | `12` | ✅ | `8` | Minimum password length |
| **Database** |
| `DATABASE_URL` | `sqlite:///./dev.db` | `postgresql://user:pass@staging-db:5432/crm` | `postgresql://user:pass@prod-db:5432/crm` | ✅ | `sqlite:///./app.db` | Database connection string |
| `DATABASE_POOL_SIZE` | `5` | `20` | `50` | ✅ | `10` | Database connection pool size |
| `DATABASE_MAX_OVERFLOW` | `5` | `10` | `20` | ✅ | `10` | Max overflow connections |
| `DATABASE_ECHO` | `true` | `false` | `false` | ✅ | `false` | Log SQL queries |
| **Redis/Cache** |
| `REDIS_URL` | `redis://localhost:6379/0` | `redis://staging-redis:6379/0` | `redis://prod-redis:6379/0` | ⚠️ | (none) | Redis connection URL (optional in dev, required in prod) |
| `CACHE_TTL` | `60` | `300` | `600` | ✅ | `300` | Cache time-to-live (seconds) |
| **Webhooks** |
| `FB_VERIFY_TOKEN` | `dev_fb_token_123` | `(from secrets manager)` | `(from secrets manager)` | ✅ | ❌ REQUIRED | Facebook webhook verification token |
| `FB_APP_SECRET` | `dev_fb_secret` | `(from secrets manager)` | `(from secrets manager)` | ✅ | ❌ REQUIRED | Facebook app secret for HMAC verification |
| `GOOGLE_WEBHOOK_SECRET` | `dev_google_secret` | `(from secrets manager)` | `(from secrets manager)` | ✅ | ❌ REQUIRED | Google webhook shared secret |
| `TWILIO_AUTH_TOKEN` | `dev_twilio_token` | `(from secrets manager)` | `(from secrets manager)` | ✅ | ❌ REQUIRED | Twilio auth token for signature verification |
| **Feature Flags** |
| `ENABLE_NEW_DASHBOARD` | `true` | `false` | `false` | ❌ | `false` | Enable new dashboard UI (gradual rollout) |
| `STRICT_WEBHOOK_WINDOW` | `false` | `true` | `true` | ❌ | `true` | Enforce strict webhook timestamp validation (5 min window) |
| `ENABLE_RATE_LIMITING` | `false` | `true` | `true` | ❌ | `false` | Enable API rate limiting |
| `ENABLE_EMAIL_NOTIFICATIONS` | `false` | `true` | `true` | ❌ | `false` | Send email notifications |
| **Monitoring** |
| `SENTRY_DSN` | ❌ Not set | `https://...@sentry.io/...` | `https://...@sentry.io/...` | ⚠️ | (none) | Sentry error tracking DSN (optional in dev) |
| `SENTRY_ENVIRONMENT` | `development` | `staging` | `production` | ✅ | `development` | Sentry environment tag |
| `SENTRY_TRACES_SAMPLE_RATE` | `1.0` | `0.1` | `0.01` | ✅ | `0.0` | Sentry performance tracing sample rate |
| **Email/SMTP** |
| `SMTP_HOST` | `localhost` | `smtp.example.com` | `smtp.example.com` | ⚠️ | (none) | SMTP server host |
| `SMTP_PORT` | `1025` | `587` | `587` | ⚠️ | `587` | SMTP server port |
| `SMTP_USER` | ❌ Not set | `noreply@example.com` | `noreply@example.com` | ⚠️ | (none) | SMTP username |
| `SMTP_PASSWORD` | ❌ Not set | `(from secrets manager)` | `(from secrets manager)` | ⚠️ | (none) | SMTP password |
| `SMTP_FROM_EMAIL` | `dev@localhost` | `noreply@staging.example.com` | `noreply@example.com` | ✅ | `noreply@localhost` | Default sender email |
| **Frontend Build** |
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://api-staging.example.com` | `https://api.example.com` | ✅ | `http://localhost:8000` | Backend API base URL for CRM SPA |
| `VITE_OPS_API_BASE_URL` | `http://localhost:8001` | `https://ops-api-staging.example.com` | `https://ops-api.example.com` | ✅ | `http://localhost:8001` | Backend API base URL for Ops SPA |
| `VITE_SENTRY_DSN` | ❌ Not set | `https://...@sentry.io/...` | `https://...@sentry.io/...` | ⚠️ | (none) | Frontend Sentry DSN |
| `VITE_ENVIRONMENT` | `development` | `staging` | `production` | ✅ | `development` | Frontend environment tag |

## Environment-Specific Notes

### Development (`dev`)

**Purpose:** Local development and testing

**Characteristics:**
- Debug mode enabled
- Verbose logging (DEBUG level)
- SQLite database (fast, no setup)
- Relaxed authentication (longer tokens)
- Shorter password requirements
- No Redis required
- No email sending
- Permissive CORS (localhost)
- Feature flags enabled for testing

**Security Relaxations:**
- Insecure default `SECRET_KEY` (acceptable for local dev)
- No HTTPS enforcement
- Shorter passwords allowed
- Webhook signature validation optional

**Setup:**
```bash
cp .env.example .env.dev
# Edit .env.dev with dev values
export ENV_FILE=.env.dev
```

### Staging (`staging`)

**Purpose:** Pre-production testing and QA validation

**Characteristics:**
- Production-like configuration
- Real PostgreSQL database
- Redis caching enabled
- Shorter token lifetimes than dev
- Moderate logging (INFO level)
- Email notifications enabled
- Sentry error tracking enabled
- Lower performance tracing rate than prod

**Security:**
- All secrets from secrets manager (AWS Secrets Manager, Vault, etc.)
- HTTPS enforced
- CORS restricted to staging domains
- Rate limiting enabled
- Webhook signatures strictly validated

**Setup:**
```bash
# Secrets loaded from AWS Secrets Manager or similar
terraform apply -var="environment=staging"
# Or manually:
export SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id staging/crm/secret-key --query SecretString --output text)
```

### Production (`prod`)

**Purpose:** Live production system

**Characteristics:**
- Maximum security settings
- Minimal logging (WARNING level only)
- High-performance database with connection pooling
- Redis caching required
- Shortest token lifetimes
- Strict webhook validation
- Full monitoring and alerting
- Low performance tracing rate (cost optimization)

**Security:**
- All secrets from secrets manager
- HTTPS strictly enforced
- CORS restricted to production domains
- Rate limiting enabled
- Strong password requirements (12+ chars)
- Webhook timestamp window enforced (5 min)
- No debug mode
- No SQL query logging

**Setup:**
```bash
# Secrets loaded from secrets manager
terraform apply -var="environment=prod"
# Manual deployment requires all secrets configured
```

## Environment Variable Validation

### Startup Checks

Both APIs perform startup validation:

```python
# crm_api/app/core/config.py
class Settings(BaseSettings):
    # Required fields raise ValidationError if missing
    SECRET_KEY: str
    DATABASE_URL: str

    # Optional with defaults
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        if values.get("ENVIRONMENT") == "prod":
            if v == "dev-secret-key-change-in-prod":
                raise ValueError("Must set secure SECRET_KEY in production")
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
```

### Missing Required Variables

If required variables are missing, the API will:
1. Log error with missing variable name
2. Raise `ValidationError` with helpful message
3. Exit with non-zero status code
4. Include remediation steps in error message

Example error:
```
ValidationError: 1 validation error for Settings
SECRET_KEY
  field required (type=value_error.missing)

Remediation:
  1. Set SECRET_KEY environment variable
  2. Or add SECRET_KEY to .env file
  3. Generate secure key: openssl rand -hex 32
```

## Secrets Management

### Development

Store secrets in `.env.dev` file (gitignored):
```bash
SECRET_KEY=dev-secret-key-change-in-prod
FB_APP_SECRET=dev_fb_secret
```

### Staging & Production

**Recommended:** Use a secrets manager:

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name prod/crm/secret-key \
  --secret-string "$(openssl rand -hex 32)"
```

**HashiCorp Vault:**
```bash
vault kv put secret/prod/crm \
  secret_key="$(openssl rand -hex 32)" \
  fb_app_secret="..."
```

**Kubernetes Secrets:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: crm-secrets
type: Opaque
data:
  secret-key: <base64-encoded>
```

## Feature Flag Configuration

Feature flags can be set via:

1. **Environment variables** (persistent):
   ```bash
   export ENABLE_NEW_DASHBOARD=true
   ```

2. **Runtime config** (backend):
   ```python
   from app.core.feature_flags import set_flag
   set_flag("ENABLE_NEW_DASHBOARD", True)
   ```

3. **localStorage override** (frontend, for testing):
   ```javascript
   localStorage.setItem('ff_enableNewDashboard', 'true')
   ```

See `docs/FEATURE_FLAGS.md` for detailed flag documentation.

## Validation Checklist

Before deploying to a new environment:

- [ ] All required variables are set
- [ ] Secrets are loaded from secrets manager (staging/prod)
- [ ] `SECRET_KEY` is cryptographically random and ≥32 characters
- [ ] CORS origins match the environment's frontend URLs
- [ ] Database connection is tested and accessible
- [ ] Redis is accessible (staging/prod)
- [ ] SMTP credentials are valid (if email enabled)
- [ ] Webhook secrets match external service configuration
- [ ] Sentry DSN is correct and environment tag matches
- [ ] Feature flags are set appropriately for the environment

## Common Pitfalls

### ⚠️ Foot-Gun #1: Using Dev Secrets in Production

**Problem:** Accidentally using `dev-secret-key-change-in-prod` in production.

**Prevention:** Startup validation checks for this and fails the app.

**Remediation:** Generate secure key: `openssl rand -hex 32`

### ⚠️ Foot-Gun #2: Permissive CORS in Production

**Problem:** Setting `CORS_ORIGINS=*` in production.

**Prevention:** Explicitly set allowed origins per environment.

**Remediation:** Set `CRM_CORS_ORIGINS=https://crm.example.com`

### ⚠️ Foot-Gun #3: Debug Mode in Production

**Problem:** Leaving `DEBUG=true` in production exposes stack traces.

**Prevention:** Default is `false`, staging/prod explicitly set to `false`.

**Remediation:** Set `DEBUG=false`

### ⚠️ Foot-Gun #4: Missing Redis in Production

**Problem:** Production performance degrades without caching.

**Prevention:** Startup warning if `REDIS_URL` not set in prod.

**Remediation:** Configure Redis and set `REDIS_URL`

### ⚠️ Foot-Gun #5: Incorrect API URLs in Frontend Build

**Problem:** Frontend built with wrong `VITE_API_BASE_URL` can't connect to backend.

**Prevention:** CI/CD validates environment-specific build configs.

**Remediation:** Rebuild with correct `VITE_API_BASE_URL`

## Related Documentation

- `docs/FEATURE_FLAGS.md` - Feature flag system details
- `docs/ERROR_HANDLING.md` - Error codes and handling
- `.env.example` - Template for environment variables
- `scripts/config/check.sh` - Configuration validation script
