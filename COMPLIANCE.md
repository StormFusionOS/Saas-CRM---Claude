# Compliance & Privacy Documentation

## Overview

The RiverCityClean CRM includes comprehensive compliance and consent management features to ensure GDPR, CCPA, and other privacy regulation compliance.

---

## Features

### 1. Consent Management

#### Consent Types
- **Essential:** Required for service operation (always enabled)
- **Marketing:** Marketing communications and campaigns
- **Analytics:** Usage tracking and performance analytics
- **Personalization:** Customized content and recommendations
- **Third-Party:** Data sharing with third-party services

#### Consent Banner
**Location:** `crm/src/components/ConsentBanner.tsx`

Features:
- Glass morphism design with slide-in animation
- Customizable preferences with detailed descriptions
- "Accept All", "Reject All", and "Save Preferences" options
- Links to privacy policy
- Accessibility-compliant (keyboard navigation, screen reader support)

#### Consent Context Provider
**Location:** `crm/src/lib/consent-context.tsx`

Features:
- Global consent state management
- LocalStorage persistence with expiry (365 days)
- Version tracking (auto-refresh on policy updates)
- Automatic tracking script initialization based on consent
- Reset and update preferences functionality

---

### 2. Backend Consent Tracking

#### Models
**Location:** `crm_api/app/models/consent.py`

**ConsentRecord:** Individual consent records
- Tracks type, granted status, source
- IP address and user agent capture
- Expiry and revocation dates
- Exact consent text shown to user

**ConsentHistory:** Audit trail of consent changes
- Tracks all changes (granted, revoked, updated, expired)
- Records who made the change
- IP address tracking
- Reason for change

**DataProcessingAgreement:** Privacy policy acceptance
- Policy version tracking
- URL to accepted policy
- Timestamp and IP address

**GDPRRequest:** Data subject requests
- Request types: access, deletion, portability, rectification, restriction
- Status tracking: pending, in_progress, completed, rejected
- Completion tracking with staff member ID
- Notes field for internal communication

#### API Endpoints
**Location:** `crm_api/app/api/routes/consent.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/consent` | POST | Create new consent record |
| `/consent/contact/{contact_id}` | GET | Get all consent records for a contact |
| `/consent/contact/{contact_id}/summary` | GET | Get consent summary for a contact |
| `/consent/{consent_id}` | PUT | Update consent (grant/revoke) |
| `/consent/{consent_id}/history` | GET | Get consent change history |
| `/data-processing-agreement` | POST | Record privacy policy acceptance |
| `/data-processing-agreement/contact/{contact_id}` | GET | Get DPA records for a contact |
| `/gdpr-request` | POST | Create GDPR data subject request |
| `/gdpr-request` | GET | List all GDPR requests (with status filter) |
| `/gdpr-request/contact/{contact_id}` | GET | Get GDPR requests for a contact |
| `/gdpr-request/{request_id}` | PUT | Update GDPR request status |
| `/gdpr-request/{request_id}/execute` | DELETE | Execute GDPR deletion (admin only) |

---

### 3. GDPR Compliance Page

**Location:** `crm/src/pages/CompliancePage.tsx`
**Route:** `/admin/compliance`

Features:
- Dashboard with request statistics
- Status filters (pending, in_progress, completed, rejected)
- Request management workflow:
  - View all data subject requests
  - Update request status
  - Mark requests as complete
  - Color-coded request types and statuses
- Animated stats cards showing pending, in-progress, and completed requests
- Compliance timeline information (30-day GDPR requirement)
- Warning alerts for irreversible actions

#### Request Types

**Access Request:**
- Provide a copy of all personal data
- Must include all data collected and processed
- Common format: PDF or structured data export

**Deletion Request (Right to be Forgotten):**
- Permanently delete all personal data
- IRREVERSIBLE operation
- Must verify identity before execution
- Keep audit trail for compliance
- Send confirmation email after completion

**Portability Request:**
- Export data in machine-readable format (JSON, CSV, XML)
- Include all personal data
- Must be in commonly used format

**Rectification Request:**
- Correct inaccurate personal data
- Update incorrect information
- Notify contact of changes

**Restriction Request:**
- Limit processing of personal data
- Maintain data but don't process
- Used when accuracy is disputed

---

## Implementation Guide

### Frontend Integration

#### 1. Add Consent Provider

Wrap your app with the ConsentProvider:

```tsx
import { ConsentProvider } from './lib/consent-context';

function App() {
  return (
    <ConsentProvider>
      {/* Your app components */}
    </ConsentProvider>
  );
}
```

#### 2. Display Consent Banner

Show the banner when user hasn't consented:

```tsx
import ConsentBanner from './components/ConsentBanner';
import { useConsent } from './lib/consent-context';

function Layout() {
  const { showBanner, acceptConsent, rejectConsent } = useConsent();

  return (
    <>
      {/* Your layout */}
      {showBanner && (
        <ConsentBanner
          onAccept={acceptConsent}
          onReject={rejectConsent}
          privacyPolicyUrl="/privacy-policy"
        />
      )}
    </>
  );
}
```

#### 3. Check Consent Before Tracking

```tsx
import { useConsent } from './lib/consent-context';

function AnalyticsWrapper() {
  const { preferences } = useConsent();

  useEffect(() => {
    if (preferences?.analytics) {
      // Initialize analytics
      initializeGoogleAnalytics();
    }
  }, [preferences]);
}
```

### Backend Integration

#### 1. Track Consent on Signup

```python
from app.models.consent import CreateConsentRequest, ConsentType

# When user signs up
consent_request = CreateConsentRequest(
    contact_id=new_contact.id,
    consent_type=ConsentType.ESSENTIAL,
    granted=True,
    source="web_signup",
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
    consent_text="I agree to the Terms of Service and Privacy Policy"
)

# Store consent record
await create_consent_record(consent_request)
```

#### 2. Handle GDPR Deletion Request

```python
# 1. Create GDPR request
gdpr_request = CreateGDPRRequest(
    contact_id=contact_id,
    request_type="deletion",
    notes="Customer requested account deletion"
)

# 2. Review and process
# ... verify identity, backup data if needed ...

# 3. Update status to in_progress
update_request = UpdateGDPRRequest(
    status="in_progress",
    notes="Identity verified, beginning deletion process"
)

# 4. Execute deletion
# ... delete/anonymize data ...

# 5. Mark as completed
update_request = UpdateGDPRRequest(
    status="completed",
    notes="All personal data has been deleted"
)
```

---

## Compliance Checklist

### GDPR Compliance

- ✅ **Consent Management**
  - Granular consent options
  - Easy-to-understand descriptions
  - Ability to withdraw consent
  - Consent version tracking

- ✅ **Data Subject Rights**
  - Right to access (data export)
  - Right to be forgotten (deletion)
  - Right to portability (data export in machine-readable format)
  - Right to rectification (data correction)
  - Right to restriction (limit processing)

- ✅ **Transparency**
  - Clear privacy policy
  - Consent banner with detailed explanations
  - Audit trail of all consent changes
  - IP address and timestamp tracking

- ✅ **Data Minimization**
  - Only essential data collected by default
  - Optional consent for marketing, analytics, etc.
  - Regular data retention reviews

- ✅ **Accountability**
  - Comprehensive audit logs
  - Staff member tracking for GDPR actions
  - Timestamped consent records
  - Compliance dashboard for monitoring

### CCPA Compliance

- ✅ **Right to Know:** Access request functionality
- ✅ **Right to Delete:** Deletion request functionality
- ✅ **Right to Opt-Out:** Granular consent controls
- ✅ **Non-Discrimination:** No service penalties for opting out

### Best Practices

1. **Response Time:** Respond to GDPR requests within 30 days (required by law)
2. **Identity Verification:** Always verify identity before fulfilling requests
3. **Data Backup:** Backup data before deletion for recovery if needed
4. **Audit Trail:** Maintain comprehensive logs of all compliance actions
5. **Staff Training:** Train staff on GDPR procedures and requirements
6. **Regular Reviews:** Audit consent records and GDPR requests monthly
7. **Policy Updates:** Version privacy policy and re-request consent on updates

---

## Security Considerations

### Consent Records
- Store IP addresses and user agents for proof of consent
- Track exact text shown to user
- Use HTTPS for all consent-related communications
- Implement rate limiting on consent API endpoints

### GDPR Requests
- Verify identity via email confirmation or other secure method
- Require admin role for destructive operations (deletion)
- Log all GDPR-related actions with staff member ID
- Implement approval workflow for sensitive requests
- Backup data before permanent deletion

### Data Retention
- Keep consent records for minimum 3 years after revocation
- Maintain GDPR request history indefinitely for compliance
- Anonymize historical data after retention period
- Regular purging of expired consent records

---

## API Examples

### Creating a Consent Record

```bash
curl -X POST http://localhost:8000/api/v1/consent \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "contact_id": 123,
    "consent_type": "marketing",
    "granted": true,
    "source": "web",
    "consent_text": "I agree to receive marketing communications"
  }'
```

### Getting Consent Summary

```bash
curl http://localhost:8000/api/v1/consent/contact/123/summary \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "contact_id": 123,
  "essential": true,
  "marketing": true,
  "analytics": false,
  "personalization": true,
  "third_party": false,
  "privacy_policy_accepted": true,
  "privacy_policy_version": "1.0",
  "last_updated": "2025-11-03T14:30:00Z"
}
```

### Creating GDPR Deletion Request

```bash
curl -X POST http://localhost:8000/api/v1/gdpr-request \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "contact_id": 123,
    "request_type": "deletion",
    "notes": "Customer requested full account deletion"
  }'
```

### Updating GDPR Request Status

```bash
curl -X PUT http://localhost:8000/api/v1/gdpr-request/456 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "status": "completed",
    "notes": "All personal data has been deleted successfully"
  }'
```

---

## Testing

### Manual Testing Checklist

**Consent Banner:**
- [ ] Banner displays on first visit
- [ ] "Accept All" grants all permissions
- [ ] "Reject All" grants only essential
- [ ] "Customize Preferences" shows details
- [ ] Preferences persist across sessions
- [ ] Banner respects 365-day expiry
- [ ] Banner shows on version change

**GDPR Compliance Page:**
- [ ] All requests display correctly
- [ ] Status filters work
- [ ] Request status can be updated
- [ ] Stats cards show accurate counts
- [ ] Request types are color-coded
- [ ] Animations play smoothly

**API Endpoints:**
- [ ] Consent creation works
- [ ] Consent history tracked
- [ ] GDPR requests created successfully
- [ ] Status updates work
- [ ] Authorization required for all endpoints

---

## Troubleshooting

### Consent Banner Not Showing
1. Check if consent is already saved in localStorage
2. Clear localStorage: `localStorage.removeItem('user_consent_preferences')`
3. Verify ConsentProvider is wrapping the app
4. Check browser console for errors

### GDPR Requests Not Loading
1. Verify API server is running on port 8000
2. Check authentication token is valid
3. Verify consent router is registered in main.py
4. Check browser network tab for API errors

### Consent Not Persisting
1. Check localStorage is enabled in browser
2. Verify JSON serialization is working
3. Check for localStorage quota errors
4. Verify consent data structure is correct

---

## Regulatory References

- **GDPR:** [https://gdpr.eu](https://gdpr.eu)
- **CCPA:** [https://oag.ca.gov/privacy/ccpa](https://oag.ca.gov/privacy/ccpa)
- **Article 12:** Right to access and transparency
- **Article 17:** Right to erasure (right to be forgotten)
- **Article 20:** Right to data portability

---

## Files Reference

### Backend
- `crm_api/app/models/consent.py` - Consent data models
- `crm_api/app/api/routes/consent.py` - Consent API endpoints
- `crm_api/app/main.py` - Router registration (line 113-115)

### Frontend
- `crm/src/components/ConsentBanner.tsx` - Consent banner component
- `crm/src/lib/consent-context.tsx` - Consent state management
- `crm/src/pages/CompliancePage.tsx` - GDPR compliance dashboard
- `crm/src/routes/App.tsx` - Route configuration (line 51)
- `crm/src/components/navigation/suites.config.ts` - Navigation menu (line 347-353)

---

## Changelog

### Version 1.0.0 (2025-11-03)
- ✨ Initial compliance features release
- 📦 Consent banner component
- 📦 Consent context provider
- 📦 GDPR compliance page
- 📦 Backend consent tracking models
- 📦 Consent API endpoints
- 📦 Data subject request management
- 📦 Audit trail for consent changes
- 📝 Comprehensive documentation

---

*Compliance features maintained by the RiverCityClean Engineering Team*
*Last updated: 2025-11-03*

**IMPORTANT:** This system provides tools for compliance but does not constitute legal advice. Consult with legal counsel to ensure your specific use case meets all applicable regulations.
