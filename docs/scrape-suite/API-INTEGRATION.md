# Scrape Suite - API Integration Guide

**For Developers: Integrate Scrape Suite into your applications**

---

## Overview

The Scrape Suite provides a RESTful API for programmatic access to all features. Use this API to:

- Integrate ranking data into custom dashboards
- Automate competitive intelligence workflows
- Build custom reporting tools
- Trigger scrapes from external systems
- Export data to third-party analytics platforms

---

## Authentication

All API requests require a JWT token in the Authorization header.

### Getting an Access Token

```bash
# Login to get token
curl -X POST https://crm.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "your-password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  https://crm.yourdomain.com/api/v1/scrape/keywords
```

---

## Base URL

```
Production: https://crm.yourdomain.com/api/v1
Development: http://localhost:8000/api/v1
```

---

## Endpoints

### Keywords

#### List Keywords
```http
GET /scrape/keywords
```

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `intent` (string): Filter by intent type
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 50, max: 100)

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://crm.yourdomain.com/api/v1/scrape/keywords?is_active=true&page=1&page_size=20"
```

**Response:**
```json
{
  "keywords": [
    {
      "id": 1,
      "keyword_text": "pressure washing services",
      "target_domain": "yourcompany.com",
      "target_page": "/services/pressure-washing",
      "current_rank": 5,
      "previous_rank": 7,
      "best_rank": 3,
      "worst_rank": 15,
      "search_volume": 1000,
      "difficulty": 45,
      "intent": "commercial",
      "impressions": 5420,
      "clicks": 271,
      "ctr": 0.05,
      "is_active": true,
      "last_checked_at": "2025-01-10T15:30:00Z",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-10T15:30:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

#### Create Keyword
```http
POST /scrape/keywords
```

**Request Body:**
```json
{
  "keyword_text": "commercial cleaning services",
  "target_domain": "yourcompany.com",
  "target_page": "/services/commercial",
  "intent": "commercial",
  "search_volume": 800,
  "difficulty": 52,
  "is_active": true
}
```

**Response:** Returns created keyword object (status 201)

#### Get Keyword by ID
```http
GET /scrape/keywords/{keyword_id}
```

#### Update Keyword
```http
PUT /scrape/keywords/{keyword_id}
```

**Request Body:**
```json
{
  "is_active": false
}
```

#### Delete Keyword
```http
DELETE /scrape/keywords/{keyword_id}
```

---

### SERP Snapshots

#### List SERP Snapshots
```http
GET /scrape/serp/snapshots
```

**Query Parameters:**
- `keyword_id` (int): Filter by keyword
- `start_date` (string): ISO 8601 date
- `end_date` (string): ISO 8601 date
- `page` (int): Page number
- `page_size` (int): Items per page

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://crm.yourdomain.com/api/v1/scrape/serp/snapshots?keyword_id=1&page=1&page_size=10"
```

**Response:**
```json
{
  "snapshots": [
    {
      "id": 123,
      "keyword_id": 1,
      "search_date": "2025-01-10T03:00:00Z",
      "rank": 5,
      "url": "https://yourcompany.com/services/pressure-washing",
      "featured_snippet": false,
      "people_also_ask": true,
      "local_pack": false,
      "knowledge_panel": false,
      "serp_features": ["paa", "images"],
      "created_at": "2025-01-10T03:05:00Z"
    }
  ],
  "total": 90,
  "page": 1,
  "page_size": 10
}
```

#### Get SERP Results
```http
GET /scrape/serp/results?snapshot_id={snapshot_id}
```

**Response:**
```json
{
  "snapshot_id": 123,
  "results": [
    {
      "id": 1001,
      "snapshot_id": 123,
      "rank": 1,
      "url": "https://competitor.com/pressure-washing",
      "domain": "competitor.com",
      "title": "Professional Pressure Washing Services",
      "snippet": "We offer top-rated pressure washing...",
      "is_ours": false,
      "created_at": "2025-01-10T03:05:00Z"
    }
  ],
  "total": 20
}
```

---

### Competitors

#### List Competitors
```http
GET /scrape/competitors
```

**Query Parameters:**
- `is_active` (boolean)
- `category` (string)
- `priority` (string): low, medium, high, critical
- `page` (int)
- `page_size` (int)

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://crm.yourdomain.com/api/v1/scrape/competitors?is_active=true&priority=high"
```

**Response:**
```json
{
  "competitors": [
    {
      "id": 1,
      "domain": "competitor.com",
      "name": "Competitor Inc.",
      "category": "Direct Competitor",
      "priority": "high",
      "is_active": true,
      "last_scraped": "2025-01-08T02:00:00Z",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-08T02:00:00Z"
    }
  ],
  "total": 12,
  "page": 1,
  "page_size": 50
}
```

#### Create Competitor
```http
POST /scrape/competitors
```

**Request Body:**
```json
{
  "domain": "newcompetitor.com",
  "name": "New Competitor LLC",
  "category": "Indirect Competitor",
  "priority": "medium",
  "is_active": true
}
```

#### Update Competitor
```http
PUT /scrape/competitors/{competitor_id}
```

#### Delete Competitor
```http
DELETE /scrape/competitors/{competitor_id}
```

#### Get Competitor Pages
```http
GET /scrape/pages?site_id={competitor_id}
```

**Query Parameters:**
- `site_id` (int): Competitor ID
- `changed_only` (boolean): Only show changed pages
- `page` (int)
- `page_size` (int)

---

### Backlinks

#### List Backlinks
```http
GET /scrape/backlinks
```

**Query Parameters:**
- `domain` (string): Filter by domain
- `alive` (boolean): Active links only
- `dofollow` (boolean): DoFollow links only
- `page` (int)
- `page_size` (int)

**Example:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://crm.yourdomain.com/api/v1/scrape/backlinks?domain=yourcompany.com&dofollow=true"
```

**Response:**
```json
{
  "backlinks": [
    {
      "id": 501,
      "source_url": "https://industry-blog.com/article",
      "source_domain": "industry-blog.com",
      "target_url": "https://yourcompany.com/services",
      "anchor_text": "professional pressure washing",
      "is_dofollow": true,
      "is_inbody": true,
      "first_seen": "2025-01-05T10:00:00Z",
      "last_seen": "2025-01-10T10:00:00Z",
      "last_checked": "2025-01-10T10:00:00Z",
      "is_lost": false
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 50
}
```

#### Get Referring Domains
```http
GET /scrape/referring-domains
```

**Query Parameters:**
- `min_authority` (int): Minimum authority score

---

### Citations

#### List Citations
```http
GET /scrape/citations
```

**Query Parameters:**
- `listed` (boolean): Only listed citations
- `nap_match` (boolean): Only matching NAP

**Response:**
```json
{
  "citations": [
    {
      "id": 1,
      "platform": "Google Business Profile",
      "listing_url": "https://g.page/yourcompany",
      "is_listed": true,
      "name_found": "Your Company Name",
      "address_found": "123 Main St, City, ST 12345",
      "phone_found": "(555) 123-4567",
      "nap_match": true,
      "first_checked": "2025-01-01T10:00:00Z",
      "last_checked": "2025-01-10T10:00:00Z"
    }
  ],
  "total": 24
}
```

---

### Page Audits

#### List Page Audits
```http
GET /scrape/audits
```

**Query Parameters:**
- `severity` (string): critical, error, warning, info
- `fixed` (boolean): Only fixed or unfixed issues
- `page` (int)
- `page_size` (int)

**Response:**
```json
{
  "audits": [
    {
      "id": 1,
      "page_url": "https://yourcompany.com/services",
      "audit_date": "2025-01-10T01:00:00Z",
      "status_code": 200,
      "performance_proxy": {
        "load_time_ms": 1250,
        "first_contentful_paint": 850
      },
      "issues_found": 5,
      "notes": null,
      "created_at": "2025-01-10T01:05:00Z",
      "issues": [
        {
          "id": 101,
          "audit_id": 1,
          "type": "missing_meta_description",
          "description": "Page is missing meta description tag",
          "severity": "warning",
          "fixed": false,
          "fixed_date": null,
          "created_at": "2025-01-10T01:05:00Z"
        }
      ]
    }
  ],
  "total": 45,
  "page": 1,
  "page_size": 20
}
```

---

### Jobs

#### Trigger Job
```http
POST /scrape/jobs
```

**Request Body:**
```json
{
  "type": "serp",
  "payload": {
    "keyword_ids": [1, 2, 3]
  }
}
```

**Job Types:**
- `serp`: SERP snapshot
- `crawl`: Competitor crawl
- `backlinks`: Backlink check
- `citations`: Citation audit

**Response:**
```json
{
  "job_id": "job_abc123",
  "task_id": "task_xyz789",
  "status": "queued",
  "task_name": "serp_snapshot",
  "queued_at": "2025-01-10T15:00:00Z",
  "started_at": null,
  "completed_at": null,
  "duration_seconds": null,
  "items_processed": 0,
  "items_succeeded": 0,
  "items_failed": 0,
  "error_message": null,
  "output_summary": null
}
```

#### Get Job Status
```http
GET /scrape/jobs/{job_id}
```

**Response:**
```json
{
  "job_id": "job_abc123",
  "task_id": "task_xyz789",
  "status": "completed",
  "task_name": "serp_snapshot",
  "queued_at": "2025-01-10T15:00:00Z",
  "started_at": "2025-01-10T15:00:05Z",
  "completed_at": "2025-01-10T15:02:30Z",
  "duration_seconds": 145,
  "items_processed": 3,
  "items_succeeded": 3,
  "items_failed": 0,
  "error_message": null,
  "output_summary": {
    "snapshots_created": 3,
    "results_captured": 60
  }
}
```

---

### Settings

#### Get Settings
```http
GET /scrape/settings
```

**Response:**
```json
{
  "review_mode": false,
  "daily_serp_enabled": true,
  "weekly_crawl_enabled": true,
  "monthly_crawl_enabled": true,
  "backlinks_refresh_days": 7,
  "citations_refresh_days": 30,
  "max_pages_per_crawl": 100,
  "proxy_pool_enabled": false
}
```

#### Update Settings
```http
PUT /scrape/settings
```

**Request Body:**
```json
{
  "daily_serp_enabled": true,
  "backlinks_refresh_days": 14
}
```

---

### Dashboard Stats

#### Get Dashboard Statistics
```http
GET /scrape/dashboard
```

**Response:**
```json
{
  "serp_snapshots_count": 1250,
  "competitors_tracked": 12,
  "pages_monitored": 450,
  "backlinks_count": 156,
  "citations_count": 24,
  "recent_changes": 8,
  "pending_reviews": 3,
  "last_serp_snapshot": "2025-01-10T03:00:00Z",
  "last_competitor_crawl": "2025-01-09T02:00:00Z",
  "last_backlinks_refresh": "2025-01-08T10:00:00Z"
}
```

---

## Server-Sent Events (SSE)

Monitor job progress in real-time using SSE.

### Stream Job Updates
```http
GET /scrape/jobs/{job_id}/stream
```

**Example (JavaScript):**
```javascript
const eventSource = new EventSource(
  `https://crm.yourdomain.com/api/v1/scrape/jobs/${jobId}/stream`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Job update:', data);
  
  if (data.status === 'completed') {
    eventSource.close();
  }
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
  eventSource.close();
};
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (delete) |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Server Error |

### Error Response Format

```json
{
  "detail": "Keyword with domain 'example.com' already exists"
}
```

**Validation errors include field details:**
```json
{
  "detail": [
    {
      "loc": ["body", "keyword_text"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Rate Limiting

**Limits:**
- 1000 requests per hour per user
- 60 SERP snapshots per hour
- 10 competitor crawls per hour
- 20 backlink checks per hour

**Rate Limit Headers:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1641830400
```

---

## Code Examples

### Python

```python
import requests

# Authentication
response = requests.post(
    'https://crm.yourdomain.com/api/v1/auth/login',
    json={
        'email': 'your@email.com',
        'password': 'your-password'
    }
)
token = response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# Get keywords
keywords = requests.get(
    'https://crm.yourdomain.com/api/v1/scrape/keywords',
    headers=headers,
    params={'is_active': True}
).json()

# Create keyword
new_keyword = requests.post(
    'https://crm.yourdomain.com/api/v1/scrape/keywords',
    headers=headers,
    json={
        'keyword_text': 'commercial cleaning',
        'target_domain': 'yourcompany.com',
        'is_active': True
    }
).json()

# Trigger SERP snapshot
job = requests.post(
    'https://crm.yourdomain.com/api/v1/scrape/jobs',
    headers=headers,
    json={
        'type': 'serp',
        'payload': {'keyword_ids': [1, 2, 3]}
    }
).json()

print(f"Job ID: {job['job_id']}")
```

### JavaScript/TypeScript

```typescript
// Using fetch API
const login = async () => {
  const response = await fetch('https://crm.yourdomain.com/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'your@email.com',
      password: 'your-password'
    })
  });
  const data = await response.json();
  return data.access_token;
};

const getKeywords = async (token: string) => {
  const response = await fetch(
    'https://crm.yourdomain.com/api/v1/scrape/keywords?is_active=true',
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
};

// Usage
const token = await login();
const keywords = await getKeywords(token);
console.log(keywords);
```

### cURL

```bash
# Login
TOKEN=$(curl -s -X POST https://crm.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"your-password"}' \
  | jq -r '.access_token')

# Get keywords
curl -H "Authorization: Bearer $TOKEN" \
  https://crm.yourdomain.com/api/v1/scrape/keywords

# Create keyword
curl -X POST https://crm.yourdomain.com/api/v1/scrape/keywords \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword_text": "commercial cleaning",
    "target_domain": "yourcompany.com",
    "is_active": true
  }'
```

---

## Webhooks (Coming Soon)

Subscribe to events:
- `keyword.rank_changed` - Ranking increased/decreased
- `competitor.updated` - Competitor site changed
- `backlink.lost` - Backlink removed
- `audit.issue_found` - New audit issue

---

## API Changelog

**v1.0.0** (January 2025)
- Initial release
- Keywords, SERP, Competitors, Backlinks, Citations, Audits
- SSE for real-time job monitoring
- Rate limiting

---

## Support

- 📧 **API Support:** api-support@yourcompany.com
- 📚 **OpenAPI Spec:** https://crm.yourdomain.com/api/v1/docs
- 🐛 **Report API Bug:** GitHub Issues

---

**Happy Building!** 🚀
