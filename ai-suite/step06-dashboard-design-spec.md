# Step 06: Main Dashboard Design & UX Specification

**Status:** Complete (Design Spec)
**Date:** 2025-11-03
**Objective:** Design comprehensive dashboard blending CRM KPIs with SEO/AI health metrics

---

## Overview

The Main Dashboard provides a unified view of:
- **CRM Performance** - Leads, conversion, response time, revenue
- **SEO Health** - Site health, rankings, backlinks, Core Web Vitals
- **AI Governance** - Review queue, system health, SLA compliance
- **Actionable Insights** - Direct paths to resolve issues

---

## Component Inventory

### 1. KPI Tiles (CRM)
- **Leads Count** - Total active leads
- **Conversion Rate** - Lead → Customer conversion %
- **Avg Response Time** - Time to first response
- **Revenue (MTD)** - Month-to-date revenue

### 2. SEO Tiles
- **Site Health Score** - Overall SEO health (0-100)
- **Index Coverage** - Pages indexed / total pages
- **Core Web Vitals** - LCP, FID, CLS scores
- **Citation Count** - Brand mentions
- **Backlink Count** - Total inbound links
- **Rank Movement** - Keywords up/down/stable

### 3. AI Governance Widgets
- **Review Queue** - Pending AI suggestions count
- **SLA Gauge** - % within SLA
- **System Health** - AI modules status
- **SEO Wins Stream** - Recent approved changes

### 4. Tables
- **Audit Issues** - System health issues
- **Change Log** - Recent AI suggestions
- **Stale Leads** - Leads needing follow-up

### 5. Charts
- **Lead Trend** - 30-day lead volume
- **Conversion Funnel** - Pipeline stages
- **Rank Distribution** - Keywords by position
- **Response Time Trend** - 7-day response times

---

## Layout Specification

### Desktop Layout (1920x1080)

```
┌────────────────────────────────────────────────────────────────────┐
│  Header: Logo | Navigation | User Menu                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─── CRM KPIs ────────────────────────────────────────────┐      │
│  │ [Leads]  [Conversion]  [Response Time]  [Revenue]       │      │
│  │  1,234      12.3%         2.5 hrs       $45,230         │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌─── SEO Health ───────────────────────────────────────────┐     │
│  │ [Site Health] [Index] [CWV] [Citations] [Backlinks] [Ranks] │  │
│  │      87         92%    Good     234        1,523     ↑12 │    │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌─── AI Governance ────────────┬─── Quick Actions ────────┐      │
│  │ Review Queue: 23 pending     │ • Review Suggestions     │      │
│  │ SLA Compliance: 94%          │ • View Audit Issues      │      │
│  │ System Health: ✓ Healthy     │ • Analyze Keywords       │      │
│  └──────────────────────────────┴──────────────────────────┘      │
│                                                                     │
│  ┌─── Lead Trend Chart ─────────────────────────────────────┐     │
│  │                                                           │     │
│  │  │                                  ╱──╲                  │     │
│  │  │                        ╱──╲   ╱─      ─╲              │     │
│  │  │              ╱──╲   ╱─      ─          ╲             │     │
│  │  │            ╱      ─                      ─╲           │     │
│  │  └──────────────────────────────────────────────          │     │
│  │    1   5   10   15   20   25   30 (days)                │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
│  ┌─── Audit Issues ──────────┬─── Change Log ─────────────┐      │
│  │ Type  | Severity | Age     │ Module | Action | Status   │      │
│  │ SLA   | Critical | 2h      │ CTR    | Meta   | Pending  │      │
│  │ Job   | Error    | 5h      │ FAQ    | Schema | Approved │      │
│  └────────────────────────────┴──────────────────────────────┘     │
│                                                                     │
│  ┌─── SEO Wins Stream ──────────────────────────────────────┐     │
│  │ • Meta title optimized for "SEO guide" → +15% CTR        │     │
│  │ • FAQ schema added to 3 pages → Featured snippets        │     │
│  │ • 5 internal links suggested → Improved site structure   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Tablet Layout (768x1024)

```
┌──────────────────────────────────┐
│  Header (Collapsible Nav)        │
├──────────────────────────────────┤
│  ┌─── CRM KPIs (2x2 Grid) ───┐  │
│  │ [Leads]  [Conversion]      │  │
│  │ [Response] [Revenue]       │  │
│  └────────────────────────────┘  │
│                                   │
│  ┌─── SEO Health (2x3 Grid) ─┐  │
│  │ [Health] [Index]           │  │
│  │ [CWV] [Citations]          │  │
│  │ [Backlinks] [Ranks]        │  │
│  └────────────────────────────┘  │
│                                   │
│  ┌─── Review Queue ───────────┐  │
│  │ 23 Pending | View All →    │  │
│  └────────────────────────────┘  │
│                                   │
│  ┌─── Chart (Compressed) ────┐  │
│  │  (30-day lead trend)       │  │
│  └────────────────────────────┘  │
│                                   │
│  ┌─── Tables (Stacked) ──────┐  │
│  │  Audit Issues              │  │
│  │  Change Log                │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

### Mobile Layout (375x667)

```
┌─────────────────────┐
│  ☰ Logo   [User]    │
├─────────────────────┤
│  ┌─── Summary ───┐  │
│  │ Leads: 1,234  │  │
│  │ Revenue: $45K │  │
│  │ Queue: 23     │  │
│  └───────────────┘  │
│                      │
│  [View CRM KPIs]    │
│  [View SEO Health]  │
│  [Review Queue]     │
│  [Audit Issues]     │
│                      │
│  ┌─── Mini Chart ─┐ │
│  │   (Sparkline)  │ │
│  └────────────────┘ │
│                      │
│  ┌─── Recent ─────┐ │
│  │ • Item 1       │ │
│  │ • Item 2       │ │
│  │ • Item 3       │ │
│  └────────────────┘ │
└─────────────────────┘
```

---

## Component Specifications

### KPI Tile Component

```tsx
<KPITile
  title="Active Leads"
  value={1234}
  change={+12}
  changeType="increase"  // increase, decrease, neutral
  trend="up"              // up, down, stable
  onClick={() => navigate('/leads')}
  loading={false}
  error={null}
  aria-label="Active Leads: 1,234, up 12 from last period"
/>
```

**Props:**
- `title`: string - Display name
- `value`: number | string - Current value
- `change`: number - Period-over-period change
- `changeType`: 'increase' | 'decrease' | 'neutral'
- `trend`: 'up' | 'down' | 'stable'
- `onClick`: () => void - Click handler
- `loading`: boolean - Loading state
- `error`: string | null - Error message
- `icon`: ReactNode - Optional icon

**Visual States:**
- **Default**: White background, gray border
- **Hover**: Light blue background, cursor pointer
- **Focus**: Blue outline (2px solid)
- **Loading**: Skeleton animation
- **Error**: Red border, error icon

**Color Tokens:**
```css
/* Positive (green) */
--color-positive: #10b981;
--color-positive-bg: #d1fae5;

/* Negative (red) */
--color-negative: #ef4444;
--color-negative-bg: #fee2e2;

/* Neutral (gray) */
--color-neutral: #6b7280;
--color-neutral-bg: #f3f4f6;

/* Warning (yellow) */
--color-warning: #f59e0b;
--color-warning-bg: #fef3c7;
```

---

### Chart Specification: Lead Trend

**Type**: Line Chart

**Metrics:**
- **X-Axis**: Date (last 30 days)
- **Y-Axis**: Lead count
- **Line Color**: Primary blue (#3b82f6)
- **Fill**: Gradient (blue to transparent)

**Tooltip:**
```
Date: Nov 3, 2025
Leads: 42
Change: +5 from previous day
```

**Interactions:**
- Hover: Show tooltip
- Click: Navigate to leads on that date
- Zoom: Pinch/drag to zoom timeframe

**Accessibility:**
- `role="img"`
- `aria-label="Lead trend chart showing 30-day history"`
- Keyboard: Tab to focus, Arrow keys to navigate data points
- Screen reader: Announce data on focus

---

### Table Specification: Audit Issues

**Columns:**

| Column | Width | Type | Sortable | Filterable |
|--------|-------|------|----------|------------|
| Type | 15% | String | ✓ | ✓ |
| Severity | 12% | Enum | ✓ | ✓ |
| Title | 30% | String | ✓ | ✓ |
| Affected Resource | 20% | String | ✓ | ✗ |
| Age | 10% | Duration | ✓ | ✗ |
| Status | 13% | Enum | ✓ | ✓ |

**Row Actions:**
- **View**: Open issue details modal
- **Acknowledge**: Mark as acknowledged
- **Resolve**: Mark as resolved
- **Ignore**: Mark as ignored

**Color Coding:**
```tsx
severity === 'critical' → Red background
severity === 'error' → Orange background
severity === 'warning' → Yellow background
severity === 'info' → Blue background
```

**Empty State:**
```
┌─────────────────────────────────┐
│   ✓ No issues found             │
│   Your system is healthy!       │
│                                  │
│   [View Resolved Issues]        │
└─────────────────────────────────┘
```

**Loading State:**
```
┌─────────────────────────────────┐
│  ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░  │
│  ▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░  │
└─────────────────────────────────┘
```

---

### Table Specification: Change Log (Review Queue)

**Columns:**

| Column | Width | Type | Sortable | Actions |
|--------|-------|------|----------|---------|
| Module | 15% | String | ✓ | - |
| Action | 20% | String | ✓ | - |
| Target | 25% | String | ✓ | Click to view |
| Confidence | 10% | % | ✓ | - |
| Age | 10% | Duration | ✓ | - |
| Status | 10% | Enum | ✓ | - |
| Actions | 10% | Buttons | ✗ | Approve/Reject |

**Row Expansion:**
Click row to expand details:
```
┌──────────────────────────────────────────┐
│ Module: CTR Optimizer                     │
│ Action: Update Meta Title                │
│ Target: Page /seo-guide                  │
│                                           │
│ Current: "SEO Guide"                     │
│ Proposed: "Complete SEO Guide 2025"      │
│                                           │
│ Confidence: 87%                          │
│ Generated: 2 hours ago                   │
│                                           │
│ [View Context] [View Diff] [🗑️ Reject] [✓ Approve] │
└──────────────────────────────────────────┘
```

**Batch Actions:**
- Select multiple rows → Bulk approve/reject
- Filter by module, status, age
- Sort by confidence, age

---

## Microcopy

### Empty States

**Review Queue Empty:**
```
✨ All caught up!

No pending AI suggestions right now.
The AI will generate new optimization
suggestions as opportunities are found.

[View Approved Suggestions]
```

**Audit Issues Empty:**
```
✓ System Healthy

No issues detected. All systems
operating normally.

[View System Logs]
```

**Stale Leads Empty:**
```
👍 Great Follow-Up!

No stale leads. Your team is on top
of all active opportunities.

[View All Leads]
```

### Error States

**Data Load Error:**
```
⚠️ Unable to Load Data

We couldn't fetch the latest metrics.
This might be a temporary connection issue.

[Retry] [View Cached Data]

Last updated: 5 minutes ago
```

**API Error:**
```
❌ Service Unavailable

The {service_name} service is currently
unavailable. Our team has been notified.

Error Code: {error_code}
Time: {timestamp}

[Contact Support] [Dismiss]
```

### Loading States

**Initial Load:**
```
Loading dashboard...
Fetching latest metrics
```

**Partial Load:**
```
CRM KPIs: ✓ Loaded
SEO Health: ⏳ Loading...
AI Governance: ⏳ Loading...
```

**Background Refresh:**
```
(Small spinner in corner)
Refreshing data...
```

---

## KPI Formulas

### CRM KPIs

**Leads Count:**
```sql
SELECT COUNT(*)
FROM leads
WHERE status IN ('new', 'contacted', 'qualified')
  AND deleted_at IS NULL
```

**Conversion Rate:**
```sql
SELECT
  (COUNT(*) FILTER (WHERE status = 'customer') * 100.0 /
   NULLIF(COUNT(*) FILTER (WHERE status IN ('new', 'contacted', 'qualified', 'customer')), 0))::DECIMAL(5,2)
FROM leads
WHERE created_at >= DATE_TRUNC('month', NOW())
```

**Avg Response Time:**
```sql
SELECT AVG(EXTRACT(EPOCH FROM (first_contact_at - created_at)) / 3600)::DECIMAL(4,1)
FROM leads
WHERE first_contact_at IS NOT NULL
  AND created_at >= NOW() - INTERVAL '30 days'
```

**Revenue (MTD):**
```sql
SELECT SUM(amount)
FROM quotes
WHERE status = 'accepted'
  AND accepted_at >= DATE_TRUNC('month', NOW())
```

### SEO KPIs

**Site Health Score:**
```sql
SELECT
  (
    -- Index coverage (30%)
    (COUNT(*) FILTER (WHERE is_indexed = true) * 30.0 / NULLIF(COUNT(*), 0)) +
    -- CWV passing (30%)
    (COUNT(*) FILTER (WHERE core_web_vitals_score >= 90) * 30.0 / NULLIF(COUNT(*), 0)) +
    -- No critical issues (20%)
    (COUNT(*) FILTER (WHERE ARRAY_LENGTH(health_issues, 1) = 0) * 20.0 / NULLIF(COUNT(*), 0)) +
    -- Has schema (20%)
    (COUNT(*) FILTER (WHERE has_schema_markup = true) * 20.0 / NULLIF(COUNT(*), 0))
  )::INTEGER
FROM page_metrics
WHERE deleted_at IS NULL
```

**Index Coverage:**
```sql
SELECT
  (COUNT(*) FILTER (WHERE is_indexed = true) * 100.0 /
   NULLIF(COUNT(*), 0))::DECIMAL(5,2)
FROM page_metrics
```

**Rank Movement (7 days):**
```sql
SELECT
  COUNT(*) FILTER (WHERE rank_change > 0) as up,
  COUNT(*) FILTER (WHERE rank_change < 0) as down,
  COUNT(*) FILTER (WHERE rank_change = 0) as stable
FROM (
  SELECT
    k.id,
    k.current_rank - k.previous_rank as rank_change
  FROM keywords k
  WHERE k.is_active = true
    AND k.last_checked_at >= NOW() - INTERVAL '7 days'
) rank_changes
```

### AI Governance KPIs

**Review Queue Count:**
```sql
SELECT COUNT(*)
FROM change_log
WHERE status = 'pending'
```

**SLA Compliance:**
```sql
SELECT
  (COUNT(*) FILTER (WHERE is_sla_violated = false) * 100.0 /
   NULLIF(COUNT(*), 0))::DECIMAL(5,2)
FROM review_queue
WHERE status = 'pending'
```

**System Health:**
```sql
SELECT
  CASE
    WHEN COUNT(*) FILTER (WHERE severity IN ('critical', 'error')) = 0
    THEN 'healthy'
    WHEN COUNT(*) FILTER (WHERE severity = 'critical') > 0
    THEN 'critical'
    ELSE 'degraded'
  END as health_status
FROM audit_issues
WHERE status = 'open'
```

---

## Accessibility Checklist

### Color Contrast

- [ ] All text meets WCAG AA contrast ratio (4.5:1 minimum)
- [ ] Large text (18pt+) meets 3:1 ratio
- [ ] UI components meet 3:1 contrast ratio
- [ ] Color is not the only indicator of state (use icons/text)

**Test:**
```
Background: #ffffff (white)
Text: #1f2937 (gray-900) → Ratio: 16.1:1 ✓

Background: #3b82f6 (primary)
Text: #ffffff (white) → Ratio: 4.8:1 ✓

Background: #10b981 (success)
Text: #ffffff (white) → Ratio: 3.2:1 ✓
```

### Keyboard Navigation

- [ ] All interactive elements reachable via Tab
- [ ] Focus order follows visual layout (top to bottom, left to right)
- [ ] Focus indicator visible (2px outline)
- [ ] Escape closes modals/dropdowns
- [ ] Arrow keys navigate within components (tables, charts)
- [ ] Enter/Space activates buttons
- [ ] No keyboard traps

**Tab Order:**
```
1. Skip to main content
2. Navigation menu
3. KPI Tile 1 (Leads)
4. KPI Tile 2 (Conversion)
5. KPI Tile 3 (Response Time)
6. KPI Tile 4 (Revenue)
7. SEO Tile 1 (Site Health)
...
n. Review Queue Table
n+1. First table row
n+2. Approve button
n+3. Reject button
```

### Screen Reader Support

- [ ] All images have alt text
- [ ] Charts have aria-labels with data summary
- [ ] Tables have proper headers (th, scope)
- [ ] Form inputs have associated labels
- [ ] Status messages use aria-live regions
- [ ] Modal focus management (trap focus, return on close)

**ARIA Labels:**
```tsx
<KPITile
  aria-label="Active Leads: 1,234, increased by 12 from last week, click to view details"
  role="button"
  tabIndex={0}
/>

<table aria-label="Audit Issues" aria-describedby="audit-issues-desc">
  <caption id="audit-issues-desc">
    System health issues requiring attention
  </caption>
  ...
</table>

<div role="status" aria-live="polite" aria-atomic="true">
  Data refreshed successfully
</div>
```

### Focus Management

**Modal Open:**
```tsx
// Trap focus within modal
const handleModalOpen = () => {
  previousFocus = document.activeElement
  modal.querySelector('[autofocus]').focus()
}

const handleModalClose = () => {
  previousFocus.focus()
}
```

**Table Navigation:**
```tsx
// Arrow keys navigate cells
const handleKeyDown = (e) => {
  if (e.key === 'ArrowRight') focusNextCell()
  if (e.key === 'ArrowLeft') focusPreviousCell()
  if (e.key === 'ArrowDown') focusCellBelow()
  if (e.key === 'ArrowUp') focusCellAbove()
}
```

---

## UX Acceptance Criteria

### Performance

- [ ] Initial render < 2 seconds (3G connection)
- [ ] Interactive (TTI) < 3.5 seconds
- [ ] Charts render < 500ms
- [ ] Table pagination < 200ms
- [ ] API calls return < 1 second
- [ ] Background refresh doesn't block UI

### Responsiveness

- [ ] Usable on 375px mobile (iPhone SE)
- [ ] Optimized for 768px tablet
- [ ] Full features on 1920px desktop
- [ ] Touch targets minimum 44x44px (mobile)
- [ ] No horizontal scroll on any breakpoint

### Data Accuracy

- [ ] KPIs match backend calculations
- [ ] Charts reflect real-time data (within 1 min)
- [ ] Tables show correct sort order
- [ ] Filters apply correctly
- [ ] Search returns relevant results

### Error Handling

- [ ] Network errors show friendly message
- [ ] 404 errors redirect to dashboard
- [ ] 500 errors logged and reported
- [ ] Offline mode shows cached data
- [ ] Retry mechanism for failed requests

### User Actions

- [ ] Approve/reject changes in < 3 clicks
- [ ] Navigate to detail view in 1 click
- [ ] Filter data in 1-2 clicks
- [ ] Export data in 1 click
- [ ] Refresh data in 1 click

---

## Analytics Events

### Page Views

```javascript
analytics.page('Dashboard', {
  user_id: currentUser.id,
  user_role: currentUser.role,
  timestamp: Date.now()
})
```

### KPI Tile Clicks

```javascript
analytics.track('KPI Tile Clicked', {
  tile_name: 'Active Leads',
  tile_value: 1234,
  tile_change: +12,
  destination: '/leads'
})
```

### Review Queue Actions

```javascript
analytics.track('AI Suggestion Reviewed', {
  suggestion_id: 'uuid',
  module: 'ctr_optimizer',
  action: 'update_meta_title',
  decision: 'approved',  // or 'rejected'
  confidence_score: 0.87,
  time_to_decision_seconds: 45
})
```

### Chart Interactions

```javascript
analytics.track('Chart Interacted', {
  chart_type: 'lead_trend',
  interaction_type: 'hover',  // or 'click', 'zoom'
  data_point: '2025-11-03',
  value: 42
})
```

### Filter Usage

```javascript
analytics.track('Filter Applied', {
  component: 'audit_issues_table',
  filter_type: 'severity',
  filter_value: 'critical',
  results_count: 3
})
```

### Error Occurrences

```javascript
analytics.track('Dashboard Error', {
  error_type: 'api_error',
  error_message: 'Failed to fetch metrics',
  component: 'KPITiles',
  error_code: 500
})
```

---

## Implementation Roadmap

### Phase 1: Core Layout (Week 1)
- [ ] Responsive grid system
- [ ] Header and navigation
- [ ] KPI Tiles component
- [ ] Basic routing

### Phase 2: Data Integration (Week 2)
- [ ] API client setup
- [ ] Data fetching hooks
- [ ] Loading states
- [ ] Error boundaries

### Phase 3: Charts & Tables (Week 3)
- [ ] Lead trend chart
- [ ] Audit issues table
- [ ] Change log table
- [ ] Sorting and filtering

### Phase 4: Interactions (Week 4)
- [ ] Review queue actions
- [ ] Modal dialogs
- [ ] Batch operations
- [ ] Export functionality

### Phase 5: Polish (Week 5)
- [ ] Accessibility audit
- [ ] Performance optimization
- [ ] Analytics integration
- [ ] User testing

---

## Design Tokens Reference

```css
/* Colors */
--color-primary: #3b82f6;
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error: #ef4444;
--color-neutral: #6b7280;

/* Spacing */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;

/* Typography */
--font-family: 'Inter', sans-serif;
--font-size-xs: 12px;
--font-size-sm: 14px;
--font-size-md: 16px;
--font-size-lg: 18px;
--font-size-xl: 24px;

/* Borders */
--border-radius-sm: 4px;
--border-radius-md: 8px;
--border-radius-lg: 12px;

/* Shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.1);
--shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
```

---

## Status Summary

**✅ Complete:**
- Component inventory
- Layout specifications (desktop/tablet/mobile)
- Chart specifications
- Table specifications
- Microcopy (empty/error/loading states)
- KPI formulas (SQL)
- Accessibility checklist
- UX acceptance criteria
- Analytics events
- Design tokens

**⏭️ Pending:**
- React component implementation
- API integration
- Unit tests
- E2E tests
- User acceptance testing

---

**Next Step:** Implement React components based on this specification
