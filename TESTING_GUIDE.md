# Testing Guide - Full Stack CRM System

## Quick Start - Test Locally

### 1. Services Currently Running ✅

All services should already be running:

```bash
# Backend APIs (Docker containers)
http://localhost:8000 - CRM API
http://localhost:8001 - Ops API

# Frontend SPAs (Vite dev servers)
http://localhost:5173 - CRM Application
http://localhost:5174 - Ops Console
```

### 2. Test Login

1. Open http://localhost:5173 in your browser
2. You should see the login page
3. Credentials are PRE-FILLED:
   - Email: `Nathan@RiverCityClean.com`
   - Password: `password123`
4. Click **"Sign In"**
5. You should be redirected to the Dashboard

### 3. Test Navigation & Pages

Once logged in, use the sidebar to navigate:

- **📊 Dashboard** - Overview with KPIs (currently shows mock counts)
- **🎯 Leads** - Kanban board (connects to real API - will be empty initially)
- **💬 Inbox** - Messages and interactions (mock data for now)
- **🎨 Visual Check** - Design system testing

### 4. Test API Integration

#### Login Test
```bash
# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "Nathan@RiverCityClean.com", "password": "password123"}'

# You should get a JWT token back
```

#### Get Leads
```bash
# First login to get token, then:
TOKEN="your-token-here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/v1/leads
```

### 5. Available Test Users

| Email | Password | Role | Description |
|-------|----------|------|-------------|
| Nathan@RiverCityClean.com | password123 | SALES | Sales representative |
| manager@rivercityclean.com | password123 | SALES_MANAGER | Sales manager |
| owner@rivercityclean.com | password123 | OWNER | Business owner |

## What's Connected (Frontend ↔ Backend)

✅ **Authentication** - Login form → `/api/v1/auth/login`
✅ **Leads Board** - Leads page → `/api/v1/v1/leads`
✅ **Auto-redirect** - Unauthorized users → Login page
✅ **JWT Tokens** - Stored in localStorage, sent with all requests

## What's Still Mock Data

⚠️ **Dashboard KPIs** - Shows hardcoded numbers
⚠️ **Inbox Messages** - Shows fake messages (not from API yet)
⚠️ **Ops Console** - Shows static metrics

## Testing the Full Flow

### Test 1: Login & Logout

1. Visit http://localhost:5173
2. Login with Nathan@RiverCityClean.com
3. Check browser DevTools → Application → LocalStorage
4. You should see `auth_token` stored
5. Open browser console and clear localStorage
6. Refresh - you should be redirected to login

### Test 2: Leads API

1. Login to the app
2. Navigate to **Leads** page
3. Open browser DevTools → Network tab
4. You should see a request to `/api/v1/v1/leads`
5. Check the request headers - should include `Authorization: Bearer <token>`
6. Currently no leads exist, so columns will say "No leads"

### Test 3: Create a Contact via API

```bash
# Get token first by logging in through the UI or:
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "Nathan@RiverCityClean.com", "password": "password123"}' \
  | python3 -m json.tool

# Use the access_token from response:
TOKEN="<your-token-here>"

# Create a contact
curl -X POST http://localhost:8000/api/v1/v1/contacts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "company": "Acme Corp",
    "phone": "+1-555-0100"
  }'
```

## API Documentation

- CRM API Docs: http://localhost:8000/docs
- Ops API Docs: http://localhost:8001/docs

## Troubleshooting

### "Failed to load leads"
- Check if backend is running: `sg docker -c "docker-compose ps"`
- Check backend logs: `sg docker -c "docker-compose logs -f crm-api"`
- Verify you're logged in (check localStorage for token)

### Login doesn't work
- Check frontend console for errors
- Verify backend is accessible: `curl http://localhost:8000/health`
- Try credentials exactly as shown (case-sensitive)

### Port already in use
```bash
# Check what's using the ports
sudo lsof -i :5173  # CRM frontend
sudo lsof -i :5174  # Ops frontend
sudo lsof -i :8000  # CRM API
sudo lsof -i :8001  # Ops API
```

## Stopping Services

```bash
# Stop frontend dev servers
pkill -f "vite --port"

# Stop Docker services
sg docker -c "docker-compose down"

# Stop and remove all data
sg docker -c "docker-compose down -v"
```

## Restarting Services

```bash
# Start backend
sg docker -c "docker-compose up -d"

# Start frontends (in separate terminals or background)
cd crm && npm run dev &
cd ops-console && npm run dev &
```

## Next Steps

### To Complete the Integration:

1. **Add Create/Edit Forms** - Allow creating contacts and leads from UI
2. **Connect Inbox** - Show real interactions from `/api/v1/v1/leads/{id}/interactions`
3. **Connect Dashboard** - Fetch real metrics from `/metrics`
4. **Add Drag-and-Drop** - Move leads between status columns
5. **Add Notifications** - Show toast messages for success/error
6. **Add Loading States** - Better UX while fetching data

### To Deploy to Production:

1. Review `DEPLOYMENT_GUIDE.md` for platform options
2. Choose: Oracle Cloud (FREE), Render.com, or DigitalOcean
3. Follow step-by-step deployment instructions
4. Update environment variables for production
5. Set up SSL/HTTPS with Let's Encrypt

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                                │
│  - http://localhost:5173 (CRM)                          │
│  - http://localhost:5174 (Ops)                          │
│  - Axios client with JWT interceptors                   │
│  - React Router for navigation                          │
└─────────────────────────────────────────────────────────┘
                          ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│  Backend APIs (FastAPI + Docker)                        │
│  - http://localhost:8000 (CRM API)                      │
│  - http://localhost:8001 (Ops API)                      │
│  - JWT authentication with bcrypt                       │
│  - In-memory database (for now)                         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Infrastructure (Docker Compose)                        │
│  - PostgreSQL x2 (CRM + Ops)                            │
│  - Redis (caching/sessions)                             │
│  - Docker networks and volumes                          │
└─────────────────────────────────────────────────────────┘
```

## Support

- Check logs: Browser DevTools Console + Network tab
- Backend logs: `sg docker -c "docker-compose logs -f"`
- API errors: Check `/docs` endpoints for valid request formats
