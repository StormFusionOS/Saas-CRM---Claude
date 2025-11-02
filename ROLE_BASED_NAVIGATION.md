# Role-Based Navigation Guide

## Overview
Users are automatically directed to the appropriate dashboard based on their role when they log in.

## Role Mapping

| Role | Landing Page | Description |
|------|-------------|-------------|
| **OWNER** | `/dashboard` | Executive dashboard with high-level metrics |
| **SALES** | `/leads` | Sales funnel and lead management |
| **SALES_MANAGER** | `/leads` | Sales team oversight and leads |
| **DISPATCH** | `/calendar` | Operations board and scheduling |
| **TECH** | `/pwa` | Technician mobile app interface |
| **FINANCE** | `/quotes` | Invoices and financial documents |
| **SEO** | `/seo` | SEO dashboard and analytics |
| **MARKETING** | `/seo` | Marketing and SEO metrics |
| **ADMIN** | `/health` | System health and settings |

## Test Users

All users have the password: `password123`

### SALES Role
- **Email**: `Nathan@RiverCityClean.com`
- **Lands on**: `/leads`
- **Access**: Sales funnel, lead management, inbox

### SALES_MANAGER Role
- **Email**: `manager@rivercityclean.com`
- **Lands on**: `/leads`
- **Access**: Sales oversight, team performance, all sales features

### OWNER Role
- **Email**: `owner@rivercityclean.com`
- **Lands on**: `/dashboard`
- **Access**: Full system access, executive metrics

## Implementation Details

### Auth Context (`crm/src/lib/auth-context.tsx`)

The auth context now includes:
```typescript
interface User {
  id: number;
  email: string;
  roles: string[];
}
```

### useRoleLanding Hook

The `useRoleLanding(roles)` hook determines the landing page:
```typescript
export function useRoleLanding(roles: string[] | undefined): string {
  // Returns the appropriate route based on the first matching role
  // Defaults to /dashboard if no match
}
```

### Login Flow

1. User enters credentials
2. Backend authenticates and returns JWT with roles
3. Frontend decodes JWT to extract roles
4. `useRoleLanding()` determines destination
5. User navigated to role-appropriate page

### JWT Token Structure

```json
{
  "sub": "user@example.com",
  "user_id": 1,
  "roles": ["SALES"],
  "exp": 1234567890
}
```

## Testing

### Test SALES User
```bash
# Login as sales user
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "Nathan@RiverCityClean.com", "password": "password123"}'

# Expected: Should land on /leads
```

### Test OWNER User
```bash
# Login as owner
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "owner@rivercityclean.com", "password": "password123"}'

# Expected: Should land on /dashboard
```

## Adding New Roles

To add a new role:

1. Add the role to the backend (e.g., in `app/core/security.py`)
2. Update the `roleMap` in `useRoleLanding()` hook
3. Create the corresponding dashboard page
4. Add route to `App.tsx`

Example:
```typescript
const roleMap: Record<string, string> = {
  // ... existing roles
  SUPPORT: '/support',  // New support role
};
```

## User Menu Display

The Shell component now displays:
- User's email address
- Primary role (first in roles array)
- Avatar with first letter of email

## Security Notes

- JWT tokens are decoded client-side (safe, as they're signed by server)
- Roles are verified server-side on API calls
- Front-end routing is for UX only - backend enforces permissions
- Token is stored in localStorage as `auth_token`

## Future Enhancements

- [ ] Multi-role switching UI
- [ ] Custom landing page preferences
- [ ] Role-based feature flags
- [ ] Dynamic navigation based on permissions
