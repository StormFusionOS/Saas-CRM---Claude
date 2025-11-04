# STEP 06: MAIN DASHBOARD UI - STATUS REPORT

**Status**:   DESIGN COMPLETE, IMPLEMENTATION PENDING
**Date**: 2025-11-03
**Phase**: Design Specification Complete, Awaiting React Implementation

---

## Executive Summary

Step 06 involves building the **Main Dashboard UI** - a comprehensive React-based governance review queue and visualization system. Unlike Steps 04 and 05 (where implementations were already complete), Step 06 has a **complete design specification** but the **React implementation has not been started**.

### Current State

| Deliverable | Status | Lines | Location |
|-------------|--------|-------|----------|
| Design Specification |  Complete | 856 | `ai-suite/step06-dashboard-design-spec.md` |
| Ops Console Infrastructure |  Complete | ~3,231 | `ops-console/src/` |
| UI Components (generic) |  Complete | ~400 | `ops-console/src/components/ui/` |
| Governance UI Components | L Not Started | 0 | - |
| API Integration | L Not Started | 0 | - |
| Review Queue Interface | L Not Started | 0 | - |
| Visualization Components | L Not Started | 0 | - |

---

## What Exists: Ops Console Infrastructure

The `ops-console` React application exists with basic infrastructure:

### 1. Existing Pages (~600 lines)

**`src/pages/DashboardPage.tsx`** (86 lines)
- Generic system overview (Services, Alerts, CPU, Memory)
- **NOT** governance-specific
- Shows placeholder KPIs: "12/12 services", "3 alerts", "45% CPU"
- Needs to be replaced with actual governance dashboard

**`src/pages/SystemHealth.tsx`** (80 lines)
- Generic service health monitoring
- Shows: API Gateway, Database Primary, Redis Cache, Worker Queue
- **NOT** AI Suite specific
- Needs governance-specific health metrics

**`src/pages/LoginPage.tsx`** (~100 lines)
- Authentication page
- Can be reused as-is

**`src/pages/VisualCheckPage.tsx`** (~400 lines)
- Visual regression testing interface
- Not related to AI Suite governance

### 2. UI Components (~400 lines)

**Existing Components** (can be reused):
- `components/ui/Card.tsx` (49 lines) - Card container with variants (default, glass, neon)
- `components/ui/Button.tsx` (~80 lines) - Button with variants
- `components/ui/Input.tsx` (~60 lines) - Form input component
- `components/ui/Donut.tsx` (~100 lines) - Donut chart component
- `components/ui/Gauge.tsx` (~100 lines) - Gauge visualization

**Common Components**:
- `components/Layout.tsx` (~200 lines) - Main layout with sidebar navigation
- `components/ErrorDisplay.tsx` (~300 lines) - Error boundary component

### 3. Infrastructure (~500 lines)

**`src/lib/api.ts`** (30 lines)
- Axios client configured for ops API
- Only has `authAPI.login()` endpoint
- **Needs**: Governance API methods (change logs, task logs, audit issues, module configs)

**`src/lib/auth-context.tsx`** (~150 lines)
- Authentication context provider
- Can be reused as-is

**`src/lib/featureFlags.ts`** (~100 lines)
- Feature flag system
- Can be reused for gradual rollout

**`src/routes/App.tsx`** (33 lines)
- React Router setup
- Current routes: `/login`, `/dashboard`, `/health`, `/visual-check`
- **Needs**: `/governance`, `/review-queue`, `/audit-issues`, `/task-logs`

### 4. Styling (~1,500 lines)

**`src/index.css`** (~3,700 lines total in theme)
- Dark theme with design tokens
- Neon/cyberpunk aesthetic
- Custom color palette: `--color-primary`, `--color-success`, `--color-warning`, etc.
- **Can be reused** for governance UI

---

## What is Missing: Governance UI Implementation

Based on the design spec (`step06-dashboard-design-spec.md`), the following components need to be built:

### Required Components (~5,150 lines estimated)

#### 1. Core Dashboard Components (~1,100 lines)
- **GovernanceDashboard.tsx** (~400 lines) - Main dashboard page
- **KPITile.tsx** (~150 lines) - Reusable KPI display component
- **ReviewQueueWidget.tsx** (~200 lines) - Top 5 pending changes
- **SystemHealthWidget.tsx** (~150 lines) - AI module health status
- **SEOHealthWidget.tsx** (~200 lines) - SEO metrics grid

#### 2. Tables (~1,200 lines)
- **ChangeLogTable.tsx** (~400 lines) - Review queue with approve/reject
- **AuditIssuesTable.tsx** (~300 lines) - System health issues
- **StaleLeadsTable.tsx** (~250 lines) - Follow-up reminders
- **TableFilters.tsx** (~150 lines) - Filter component
- **BatchActions.tsx** (~100 lines) - Bulk operations

#### 3. Charts (~600 lines)
- **LeadTrendChart.tsx** (~150 lines) - 30-day line chart
- **ConversionFunnelChart.tsx** (~150 lines) - Funnel visualization
- **RankDistributionChart.tsx** (~150 lines) - Keyword positions
- **ResponseTimeTrendChart.tsx** (~150 lines) - 7-day response times

#### 4. API Integration (~550 lines)
- **governance-api.ts** (~300 lines) - API client methods
- **useGovernanceMetrics.ts** (~100 lines) - Dashboard metrics hook
- **useChangeLogs.ts** (~50 lines) - Change log data hook
- **useAuditIssues.ts** (~50 lines) - Audit issues data hook
- **useTaskLogs.ts** (~50 lines) - Task logs data hook

#### 5. Polish & Testing (~1,700 lines)
- Accessibility improvements (~200 lines)
- Loading/error states (~300 lines)
- Unit tests (~800 lines)
- E2E tests (~400 lines)

---

## Design Specification Summary

The complete design spec (`step06-dashboard-design-spec.md`, 856 lines) includes:

### KPI Tiles (Specified)
- **CRM**: Leads, Conversion Rate, Response Time, Revenue (MTD)
- **SEO**: Site Health Score, Index Coverage, Core Web Vitals, Citations, Backlinks, Rank Movement
- **AI Governance**: Review Queue Count, SLA Compliance, System Health Status

### Tables (Specified)
1. **Audit Issues Table**
   - Columns: Type, Severity, Title, Affected Resource, Age, Status
   - Sortable, filterable, color-coded by severity
   - Row actions: View, Acknowledge, Resolve, Ignore

2. **Change Log Table** (Review Queue)
   - Columns: Module, Action, Target, Confidence, Age, Status, Actions
   - Expandable rows with full change details
   - Batch operations: Bulk approve/reject
   - Inline approve/reject buttons

3. **Stale Leads Table**
   - CRM-specific follow-up tracking
   - Not directly AI Suite related

### Charts (Specified)
- **Lead Trend** (Line chart, 30 days)
- **Conversion Funnel** (Funnel chart)
- **Rank Distribution** (Histogram of keyword positions)
- **Response Time Trend** (Line chart, 7 days)

### Layout Specifications
- **Desktop** (1920x1080): Full dashboard with all KPIs, charts, tables
- **Tablet** (768x1024): 2-column grid, stacked sections
- **Mobile** (375x667): Single column, collapsible sections, summary view

### UX Specifications
- **Accessibility**: WCAG AA compliance, keyboard navigation, screen reader support
- **Performance**: < 2s initial render, < 500ms chart render, < 200ms table pagination
- **Interactivity**: Approve/reject in < 3 clicks, batch operations, inline editing
- **Error Handling**: Friendly error messages, retry mechanisms, offline mode with cached data

### KPI SQL Formulas
Complete queries provided for:
- CRM metrics (leads count, conversion rate, avg response time, revenue)
- SEO metrics (site health score = weighted formula, index coverage %, rank movement)
- AI governance (review queue count, SLA compliance %, system health status)

---

## Implementation Estimate

### Total Estimated Lines of Code

| Category | Estimated Lines |
|----------|----------------|
| React Components | ~2,900 |
| API Integration | ~550 |
| Tests | ~1,200 |
| Polish & Accessibility | ~500 |
| **TOTAL** | **~5,150 lines** |

### Timeline Estimate

- **Phase 1**: Core Components (Week 1-2)
- **Phase 2**: Tables (Week 2-3)
- **Phase 3**: Charts (Week 3-4)
- **Phase 4**: API Integration (Week 4)
- **Phase 5**: Polish & Testing (Week 5)

**Total Duration**: 5-6 weeks

---

## Dependencies

### NPM Packages Required

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "react-query": "^3.39.0",
    "recharts": "^2.5.0",
    "date-fns": "^2.29.0",
    "clsx": "^1.2.1"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3",
    "vitest": "^0.29.0",
    "playwright": "^1.31.0"
  }
}
```

### Backend API Dependencies

All required governance API endpoints are already implemented in Step 03:
-  `GET /api/v1/governance/summary`
-  `GET /api/v1/governance/change-log`
-  `PUT /api/v1/governance/change-log/{id}`
-  `POST /api/v1/governance/change-log/{id}/execute`
-  `GET /api/v1/governance/task-log`
-  `GET /api/v1/governance/audit-issues`
-  `GET /api/v1/governance/modules`

**No backend work required** - all APIs ready for frontend integration.

---

## Recommendation: Defer Implementation

### Option 1: Skip Frontend, Continue with Backend AI Modules P **RECOMMENDED**

**Rationale**:
1. **No data to display yet**: The `change_log` table is currently empty. Building a review queue UI would only show empty states.
2. **Backend is more critical**: AI modules (Steps 07-16) are the core value proposition. The UI is just a review interface.
3. **Faster time to value**: AI modules deliver actual SEO improvements. Frontend is "nice to have" for governance.
4. **Complete design exists**: When ready to implement, the 856-line design spec has all specifications.

**Next Steps**:
- Proceed with **Step 07: SEO Meta Optimizer**
- Build AI modules that generate real AI suggestions
- Defer dashboard UI until there's actual data to review

**Interim Solution**: Use database queries or simple CLI tool for reviewing changes:
```bash
python scripts/review_changes.py list --status pending
python scripts/review_changes.py approve chg_meta_12345
```

### Option 2: Build MVP Dashboard (2 weeks)

Minimal version with core features:
- GovernanceDashboard.tsx with basic layout
- Review Queue Widget (top 5 pending)
- Change Log Table (basic, no batch actions)
- Audit Issues Table (read-only)

**Deliverable**: ~1,500 lines, functional review interface
**Timeline**: 1-2 weeks

### Option 3: Build Full Dashboard (6 weeks)

Complete implementation per design spec:
- All KPI tiles, widgets, tables, charts
- Full API integration
- Accessibility features
- Comprehensive tests

**Deliverable**: ~5,150 lines, production-ready UI
**Timeline**: 5-6 weeks

---

## Conclusion

**Step 06 Status Summary**:
-  Design specification complete (856 lines)
-  Ops console infrastructure exists (~3,231 lines)
-  Reusable UI components available (~400 lines)
-  Backend governance APIs ready (Step 03)
- L Governance-specific UI components not started (0 lines)
- L API integration hooks not started (0 lines)

**Recommended Path**: **Defer dashboard implementation**, proceed with Step 07 (SEO Meta Optimizer).

**Key Decision Point**: Should we invest 5-6 weeks building a dashboard UI before we have any AI-generated changes to review? Or build the AI modules first, then add the UI when there's real data to display?

---

**Files**:
- Design Spec: `ai-suite/step06-dashboard-design-spec.md` (856 lines)
- Status Report: `ai-suite/STEP06_STATUS.md` (this document)
- Existing Code: `ops-console/src/` (~3,231 lines infrastructure)

**Next Step**: User decision - implement dashboard now, build MVP, or proceed to Step 07?
