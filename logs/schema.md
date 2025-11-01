# Log Schema Documentation

**Version**: 1.0
**Last Updated**: 2025-11-01
**Format**: JSON Lines (JSONL)
**Schema**: ECS (Elastic Common Schema) 8.0.0 Compatible

## Overview

All RiverCityClean services log in JSON Lines format with ECS-compatible field names. Each log entry is a single-line JSON object terminated by a newline character.

## Core Fields

Every log entry contains these base fields:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `@timestamp` | string (ISO 8601) | ✅ | Event timestamp in UTC | `"2025-11-01T12:00:00.000Z"` |
| `log.level` | string | ✅ | Log level | `"INFO"`, `"WARNING"`, `"ERROR"` |
| `log.logger` | string | ✅ | Logger name | `"crm_api"`, `"ops_api.auth"` |
| `message` | string | ✅ | Human-readable message | `"User logged in successfully"` |
| `ecs.version` | string | ✅ | ECS schema version | `"8.0.0"` |

## Service Fields

Service identification and metadata:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `service.name` | string | Service name | `"crm_api"`, `"ops_api"` |
| `service.version` | string | Service version | `"1.0.0"` |

## Host Fields

Host/container information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `host.hostname` | string | Hostname | `"app-server-01"` |
| `process.thread.id` | integer | Thread ID | `12345` |
| `process.thread.name` | string | Thread name | `"MainThread"` |

## Log Origin Fields

Source code location:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `log.origin.file.name` | string | Source filename | `"auth.py"` |
| `log.origin.file.line` | integer | Line number | `142` |
| `log.origin.function` | string | Function name | `"handle_login"` |

## HTTP Fields

HTTP request/response data:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `http.request.method` | string | HTTP method | `"GET"`, `"POST"` |
| `http.request.path` | string | Request path | `"/api/v1/users"` |
| `http.response.status_code` | integer | HTTP status code | `200`, `404`, `500` |
| `http.request.bytes` | integer | Request body size (bytes) | `1024` |
| `http.response.bytes` | integer | Response body size (bytes) | `2048` |

## User Fields

User identity information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `user.id` | string | User ID | `"user_12345"` |
| `user.name` | string | Username | `"john.doe"` |
| `user.email` | string | User email (redacted) | `"[EMAIL_REDACTED]"` |

## Client Fields

Client/source information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `client.ip` | string | Client IP (redacted) | `"[IP_REDACTED]"` |
| `client.user_agent` | string | User agent | `"Mozilla/5.0..."` |

## Trace Context Fields

Distributed tracing information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `trace.id` | string | W3C trace ID (32 hex chars) | `"4bf92f3577b34da6a3ce929d0e0e4736"` |
| `span.id` | string | W3C span ID (16 hex chars) | `"00f067aa0ba902b7"` |

## Event Fields

Event classification and metrics:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `event.action` | string | Action performed | `"auth.login.success"` |
| `event.category` | string | Event category | `"authentication"`, `"web"` |
| `event.type` | string | Event type | `"access"`, `"change"` |
| `event.outcome` | string | Event outcome | `"success"`, `"failure"` |
| `event.duration` | float | Duration in milliseconds | `125.5` |

## Error Fields

Error and exception information:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `error.type` | string | Exception class name | `"ValueError"`, `"HTTPException"` |
| `error.message` | string | Error message | `"Invalid credentials"` |
| `error.stack_trace` | string | Stack trace | `"Traceback (most recent..."` |

## Custom Labels

Additional context-specific fields:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `labels.*` | any | Custom labels | `{"environment": "production"}` |

## PII Redaction

The following data types are automatically redacted:

| Data Type | Pattern | Redacted Value |
|-----------|---------|----------------|
| Email | `user@example.com` | `[EMAIL_REDACTED]` |
| IPv4 | `192.168.1.1` | `[IP_REDACTED]` |
| IPv6 | `2001:db8::1` | `[IP_REDACTED]` |
| Credit Card | `4111-1111-1111-1111` | `[CC_REDACTED]` |
| SSN | `123-45-6789` | `[SSN_REDACTED]` |
| JWT Token | `eyJ...` | `[JWT_REDACTED]` |
| Bearer Token | `Bearer abc123...` | `Bearer [TOKEN_REDACTED]` |

**Sensitive Field Names** (automatically redacted):
- `password`, `passwd`, `pwd`
- `secret`, `token`, `api_key`, `apikey`
- `authorization`, `auth`, `credentials`
- `private_key`, `access_token`, `refresh_token`
- `session_id`, `cookie`, `x-api-key`

## Event Actions

Common event actions used across services:

### Authentication
- `auth.login.success` - Successful login
- `auth.login.failure` - Failed login attempt
- `auth.logout` - User logout
- `auth.session.created` - Session created
- `auth.session.expired` - Session expired
- `auth.password.changed` - Password changed
- `auth.mfa.enabled` - MFA enabled
- `auth.mfa.disabled` - MFA disabled

### HTTP
- `http.request` - HTTP request received
- `http.response` - HTTP response sent
- `http.client.request` - Outgoing HTTP request

### Access Control
- `access.granted` - Access granted
- `access.denied` - Access denied (403)
- `authorization.check` - Authorization check performed

### Data Operations
- `data.create` - Record created
- `data.read` - Record read
- `data.update` - Record updated
- `data.delete` - Record deleted

### Tasks
- `task.enqueue` - Task enqueued
- `task.process.start` - Task processing started
- `task.process.complete` - Task completed
- `task.process.failed` - Task failed

## Example Log Entries

### Successful Login
```json
{
  "@timestamp": "2025-11-01T12:00:00.123Z",
  "log.level": "INFO",
  "log.logger": "crm_api.auth",
  "message": "User logged in successfully",
  "ecs.version": "8.0.0",
  "service.name": "crm_api",
  "service.version": "1.0.0",
  "host.hostname": "app-server-01",
  "http": {
    "request.method": "POST",
    "request.path": "/api/v1/auth/login",
    "response.status_code": 200
  },
  "user": {
    "id": "user_12345",
    "name": "john.doe"
  },
  "client": {
    "ip": "[IP_REDACTED]",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  },
  "event": {
    "action": "auth.login.success",
    "category": "authentication",
    "outcome": "success",
    "duration": 125.5
  },
  "trace": {
    "id": "4bf92f3577b34da6a3ce929d0e0e4736"
  },
  "span": {
    "id": "00f067aa0ba902b7"
  }
}
```

### Failed Authentication (Brute Force)
```json
{
  "@timestamp": "2025-11-01T12:05:30.456Z",
  "log.level": "WARNING",
  "log.logger": "crm_api.auth",
  "message": "Login failed: invalid credentials",
  "ecs.version": "8.0.0",
  "service.name": "crm_api",
  "service.version": "1.0.0",
  "http": {
    "request.method": "POST",
    "request.path": "/api/v1/auth/login",
    "response.status_code": 401
  },
  "user": {
    "name": "admin"
  },
  "client": {
    "ip": "[IP_REDACTED]"
  },
  "event": {
    "action": "auth.login.failure",
    "category": "authentication",
    "outcome": "failure",
    "duration": 15.2
  }
}
```

### Access Denied (403)
```json
{
  "@timestamp": "2025-11-01T12:10:15.789Z",
  "log.level": "WARNING",
  "log.logger": "crm_api.access",
  "message": "Access denied to admin endpoint",
  "ecs.version": "8.0.0",
  "service.name": "crm_api",
  "http": {
    "request.method": "GET",
    "request.path": "/admin/users",
    "response.status_code": 403
  },
  "user": {
    "id": "user_67890"
  },
  "event": {
    "action": "access.denied",
    "category": "web",
    "outcome": "failure"
  }
}
```

### Error with Stack Trace
```json
{
  "@timestamp": "2025-11-01T12:15:00.000Z",
  "log.level": "ERROR",
  "log.logger": "crm_api.database",
  "message": "Database connection failed",
  "ecs.version": "8.0.0",
  "service.name": "crm_api",
  "log.origin": {
    "file.name": "database.py",
    "file.line": 45,
    "function": "get_connection"
  },
  "error": {
    "type": "ConnectionError",
    "message": "Unable to connect to database",
    "stack_trace": "Traceback (most recent call last):\n  File..."
  },
  "event": {
    "action": "database.connection.failed",
    "category": "database",
    "outcome": "failure"
  }
}
```

## Querying Logs

### Common Queries

**All failed logins**:
```bash
jq 'select(.event.action == "auth.login.failure")' logs/crm_api.jsonl
```

**High severity errors**:
```bash
jq 'select(.log.level == "ERROR")' logs/crm_api.jsonl
```

**Specific user activity**:
```bash
jq 'select(.user.id == "user_12345")' logs/crm_api.jsonl
```

**Trace specific request**:
```bash
jq 'select(.trace.id == "4bf92f3577b34da6a3ce929d0e0e4736")' logs/*.jsonl
```

**HTTP 5xx errors**:
```bash
jq 'select(.http.response.status_code >= 500)' logs/crm_api.jsonl
```

## Compliance

This schema supports compliance requirements:

- **SOC 2 CC6.8** - Audit logs with timestamps, users, actions
- **ISO 27001 A.12.4.1** - Event logging with PII redaction
- **NIST CSF DE.AE-3** - Correlated event analysis via trace IDs
- **GDPR Article 32** - PII redaction and pseudonymization

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial schema documentation |
