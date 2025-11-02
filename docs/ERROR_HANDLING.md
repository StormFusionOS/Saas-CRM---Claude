# Error Handling Guide

## Overview

This document describes the standardized error handling system used across the RiverCityClean SaaS CRM platform.

All APIs return errors in a consistent format, and all SPAs display user-friendly messages with copy-to-clipboard error IDs for support.

## Error Response Format

All API errors follow this envelope structure:

```json
{
  "error": {
    "code": "ERR_AUTH_EXPIRED",
    "message": "Your session has expired",
    "details": {
      "request_id": "req_abc123"
    }
  }
}
```

## Error Categories

### Authentication Errors (401)

| Error Code | User Message | When It Occurs |
|------------|--------------|----------------|
| `ERR_AUTH_INVALID_CREDENTIALS` | "Invalid email or password. Please check your credentials and try again." | Login with wrong credentials |
| `ERR_AUTH_EXPIRED` | "Your session has expired. Please log in again to continue." | JWT token expired |
| `ERR_AUTH_MISSING` | "You must be logged in to access this resource." | No auth token provided |
| `ERR_AUTH_INVALID_TOKEN` | "Your session is invalid. Please log in again." | Malformed or invalid JWT |

### Authorization Errors (403)

| Error Code | User Message | When It Occurs |
|------------|--------------|----------------|
| `ERR_FORBIDDEN` | "You don't have permission to access this resource." | User lacks required permissions |
| `ERR_FORBIDDEN_REALM` | "You don't have permission to access this section. Please contact your administrator." | Cross-realm access denied |
| `ERR_FORBIDDEN_INACTIVE` | "Your account is inactive. Please contact your administrator." | User account disabled (CRM) |
| `ERR_FORBIDDEN_NOT_ADMIN` | "This action requires administrator privileges." | Admin-only action (Ops Console) |
| `ERR_WEBHOOK_SIGNATURE` | "Webhook signature verification failed." | Invalid webhook HMAC signature |
| `ERR_WEBHOOK_VERIFICATION` | "Webhook verification failed." | General webhook verification failure |
| `ERR_WEBHOOK_INVALID_SECRET` | "Invalid webhook secret." | Wrong shared secret |

### Resource Not Found (404)

#### CRM API

| Error Code | User Message |
|------------|--------------|
| `ERR_NOT_FOUND` | "The requested resource was not found." |
| `ERR_CONTACT_NOT_FOUND` | "Contact not found. It may have been deleted." |
| `ERR_LEAD_NOT_FOUND` | "Lead not found. It may have been deleted." |
| `ERR_USER_NOT_FOUND` | "User not found." |

#### Ops Console API

| Error Code | User Message |
|------------|--------------|
| `ERR_NOT_FOUND` | "The requested resource was not found." |
| `ERR_SERVICE_NOT_FOUND` | "Service not found. It may have been removed or renamed." |
| `ERR_ALERT_NOT_FOUND` | "Alert not found. It may have been resolved or deleted." |
| `ERR_METRIC_NOT_FOUND` | "Metric not found. Please check the metric name." |

### Validation Errors (400)

#### CRM API

| Error Code | User Message |
|------------|--------------|
| `ERR_VALIDATION` | "Please check your input and try again." |
| `ERR_DUPLICATE_EMAIL` | "A contact with this email already exists." |
| `ERR_INVALID_INPUT` | "The information you entered is invalid. Please check and try again." |
| `ERR_MISSING_FIELD` | "Please fill in all required fields." |
| `ERR_CONTACT_HAS_LEADS` | "Cannot delete this contact because it has associated leads..." |

#### Ops Console API

| Error Code | User Message |
|------------|--------------|
| `ERR_VALIDATION` | "Please check your input and try again." |
| `ERR_INVALID_INPUT` | "The information you entered is invalid. Please check and try again." |
| `ERR_MISSING_FIELD` | "Please fill in all required fields." |
| `ERR_INVALID_TIME_RANGE` | "Invalid time range selected. Please choose a valid date range." |

### Rate Limiting (429)

| Error Code | User Message |
|------------|--------------|
| `ERR_RATE_LIMIT` | "Too many requests. Please wait a moment and try again." |
| `ERR_RATE_LIMIT_EXCEEDED` | "You've made too many requests. Please wait a few minutes before trying again." |

### Server Errors (500)

#### CRM API

| Error Code | User Message |
|------------|--------------|
| `ERR_INTERNAL` | "Something went wrong on our end. Please try again later." |
| `ERR_DATABASE` | "A database error occurred. Please try again later." |
| `ERR_EXTERNAL_SERVICE` | "An external service is currently unavailable. Please try again later." |
| `ERR_INGESTION` | "Failed to process the request. Please try again." |

#### Ops Console API

| Error Code | User Message |
|------------|--------------|
| `ERR_INTERNAL` | "Something went wrong on our end. Please try again later." |
| `ERR_DATABASE` | "A database error occurred. Please try again later." |
| `ERR_EXTERNAL_SERVICE` | "An external service is currently unavailable. Please try again later." |
| `ERR_METRICS_SERVICE` | "The metrics service is currently unavailable. Please try again later." |
| `ERR_MONITORING_SERVICE` | "The monitoring service is currently unavailable. Please try again later." |

### Client-Side Errors

| Error Code | User Message | When It Occurs |
|------------|--------------|----------------|
| `ERR_NETWORK` | "Network error. Please check your internet connection and try again." | Network connectivity issues |
| `ERR_TIMEOUT` | "The request timed out. Please try again." | Request exceeds timeout |
| `ERR_UNKNOWN` | "An unexpected error occurred. Please try again." | Fallback for unmapped errors |

## Request ID Tracking

Every request gets a unique `request_id` that is:
- Generated on the backend or passed from frontend
- Included in the `X-Request-ID` response header
- Logged with every error
- Available in error details for support

## Frontend Error Display

### Toast Notifications

Errors are automatically displayed as toast notifications in the top-right corner with:
- **Color-coded severity**: Red (error), Yellow (warning), Blue (info)
- **Auto-dismiss**: Non-auth errors auto-dismiss after 10 seconds
- **Copy-to-clipboard error ID**: Click to copy for support tickets
- **Validation details**: Expanded list for validation errors

### Inline Errors

Use the `<InlineError>` component for form-level or page-section errors:

```tsx
import { InlineError } from "@/components/ErrorDisplay";
import { parseError } from "@/lib/errors";

// In component
const [error, setError] = useState<ErrorDetail | null>(null);

try {
  // API call
} catch (err) {
  setError(parseError(err));
}

return <InlineError error={error} />;
```

### Error Context

Wrap your app with `ErrorProvider` for global error management:

```tsx
import { ErrorProvider, useErrors } from "@/components/ErrorDisplay";

function App() {
  return (
    <ErrorProvider>
      <YourApp />
    </ErrorProvider>
  );
}

// In any component
function MyComponent() {
  const { showError } = useErrors();

  try {
    // API call
  } catch (err) {
    const parsed = parseError(err);
    showError(parsed); // Shows toast
  }
}
```

## Backend Implementation

### Raising Custom Errors

```python
from app.core.errors import (
    ErrorCode,
    AuthenticationError,
    NotFoundError,
    ValidationError,
)

# Authentication error
raise AuthenticationError(
    code=ErrorCode.ERR_AUTH_EXPIRED,
    message="Your session has expired",
)

# Not found
raise NotFoundError(
    code=ErrorCode.ERR_LEAD_NOT_FOUND,
    message="Lead not found",
    details={"lead_id": lead_id},
)

# Validation error
raise ValidationError(
    code=ErrorCode.ERR_DUPLICATE_EMAIL,
    message="Email already exists",
    details={"email": contact.email},
)
```

### Logging Errors

All errors are automatically logged with structured logging:

```json
{
  "event": "app_exception",
  "request_id": "req_abc123",
  "error_code": "ERR_AUTH_EXPIRED",
  "message": "Your session has expired",
  "status_code": 401,
  "path": "/api/v1/leads",
  "method": "GET",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Testing

### Backend Tests

Test error responses in API route tests:

```python
def test_auth_expired():
    response = client.get("/api/v1/leads", headers={"Authorization": "Bearer expired_token"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ERR_AUTH_EXPIRED"
```

### Frontend Tests

Test error mapping and message display:

```typescript
import { getErrorMessage, parseError, ErrorCode } from "@/lib/errors";

test("should map auth errors correctly", () => {
  const message = getErrorMessage(ErrorCode.ERR_AUTH_EXPIRED);
  expect(message).toBe("Your session has expired. Please log in again to continue.");
});
```

## Coverage

**Backend:**
- ✅ All CRM API routes covered (auth, leads, contacts, webhooks, scheduler)
- ✅ All Ops Console API routes covered (health, services, metrics, alerts)
- ✅ Automatic HTTPException mapping to error codes
- ✅ Pydantic validation errors mapped to ERR_VALIDATION
- ✅ Request ID tracking on all requests

**Frontend:**
- ✅ All error codes have user-friendly messages
- ✅ Toast notifications with auto-dismiss
- ✅ Inline error components
- ✅ Copy-to-clipboard error IDs
- ✅ Validation error details display
- ✅ 20+ unit tests per SPA (40+ total)

## Support Workflow

When a user reports an error:

1. **User copies error ID** from toast/inline error (e.g., `ERR_1LM2N3_ABC4D`)
2. **Support searches logs** using error ID:
   ```bash
   grep "ERR_1LM2N3_ABC4D" /var/log/app.log
   ```
3. **Logs show full context**:
   - Request ID
   - Error code
   - User ID
   - Request path
   - Stack trace (for 500 errors)
   - Timestamp

## Future Enhancements

- [ ] Error rate monitoring and alerting
- [ ] Automatic retry for transient errors
- [ ] Error recovery suggestions
- [ ] Multi-language error messages
- [ ] Error analytics dashboard
