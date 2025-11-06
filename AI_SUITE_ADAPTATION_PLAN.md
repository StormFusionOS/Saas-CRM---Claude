# AI Suite - Vite/React Router Adaptation Plan

## Overview

Adapt the Next.js-based AI Suite build specifications to work with the existing Vite + React Router + TypeScript stack.

## Stack Translation

### Next.js → Vite/React Router

| Next.js Feature | Vite/React Router Equivalent |
|----------------|------------------------------|
| App Router | React Router v6 |
| Server Components | Client components with TanStack Query |
| SSR/ISR | Client-side rendering with skeleton loaders |
| API Routes | Separate backend API (Python FastAPI) |
| Route Groups | React Router nested routes |
| Loading.tsx | Suspense + skeleton components |
| Error.tsx | Error boundaries + error pages |

## Existing Architecture

**Current Stack:**
- ✅ Vite + React 18 + TypeScript
- ✅ React Router v6
- ✅ Tailwind CSS + Design tokens
- ✅ shadcn/ui (Radix) components
- ✅ Custom UI components (Card, Button, etc.)
- ✅ Auth context + protected routes

**Needs to Add:**
- TanStack Query (React Query) for data fetching
- WebSocket or SSE for real-time updates
- Zustand for global state (optional - can use Context)
- Recharts or Visx for charts
- TanStack Table v8 (already added)

## Module Implementation Plan

### 1. AI Server Overview (Dashboard)

**File:** `src/pages/AIDashboardPage.tsx`

**Components to Build:**
- `NodeSummaryCard` - Server info (hostname, uptime, OS, model versions)
- `LiveMetricRings` - CPU, GPU, RAM, Disk, Net with thresholds
- `ActiveJobsPanel` - Running/queued jobs with progress, ETA, cancel
- `QuickActionsBar` - Run Prompt, View Logs, Health Check, Backup

**API Endpoints Needed:**
```typescript
GET /api/ai/overview         // Summaries + live metrics baseline
GET /api/ai/jobs?state=running  // Running/queued jobs
POST /api/ai/jobs/:id/cancel    // Cancel job
GET /api/health/summary         // Compact health snapshot
```

**Real-time Strategy:**
- Poll every 5 seconds for metrics (or use SSE)
- Optimistic updates for job cancellation
- Skeleton loaders during initial fetch

### 2. Prompt Runner & Library

**File:** `src/pages/AIPromptsPage.tsx`

**Components to Build:**
- `PromptLibraryTable` - TanStack Table with templates
- `PromptRunnerModal` - Execute prompt with context
- `TemplateEditor` - CRUD for templates
- `ValidationGate` - Self-healing validation
- `TemplateMetrics` - Success rate, rejection stats

**API Endpoints:**
```typescript
GET /api/prompts/templates      // List templates
POST /api/prompts/templates     // Create template
PUT /api/prompts/templates/:id  // Update template
DELETE /api/prompts/templates/:id
POST /api/prompts/run           // Execute with template_id + context
POST /api/prompts/validate      // Validate before run
GET /api/prompts/stats          // Performance metrics
```

### 3. Job Scheduler & Task Logs

**File:** `src/pages/AIJobsPage.tsx`

**Components to Build:**
- `JobScheduleTable` - List all scheduled jobs
- `GanttTimeline` - Visual timeline of jobs
- `JobCard` - Individual job with Run Now/Pause/Edit
- `TaskLogsTable` - TanStack Table with filters
- `JobEditorDrawer` - Create/edit job schedules

**API Endpoints:**
```typescript
GET /api/scheduler/jobs              // List jobs & schedules
POST /api/scheduler/jobs             // Create job
PUT /api/scheduler/jobs/:id          // Update job
POST /api/scheduler/jobs/:id/run     // Run ad-hoc
POST /api/scheduler/jobs/:id/toggle  // Enable/disable
GET /api/task-logs?job_id=&status=&from=&to= // Paginated logs
```

## Implementation Phases

### Phase 1: Foundation (Current)
- ✅ Vite + React + TypeScript setup
- ✅ React Router with routes
- ✅ shadcn/ui components
- ✅ Basic AI pages created
- ✅ Authentication system
- ✅ Design system tokens

### Phase 2: Data Layer (Next)
- [ ] Install TanStack Query (`@tanstack/react-query`)
- [ ] Create API client (`src/lib/ai-api.ts`)
- [ ] Define TypeScript interfaces for all data
- [ ] Setup query keys and hooks
- [ ] Add error handling + retry logic
- [ ] Create mock data for development

### Phase 3: AI Dashboard Enhancement
- [ ] Build NodeSummaryCard with shadcn Card
- [ ] Build LiveMetricRings with progress rings
- [ ] Build ActiveJobsPanel with real-time updates
- [ ] Add QuickActionsBar with shadcn Buttons
- [ ] Integrate TanStack Query for data fetching
- [ ] Add skeleton loaders
- [ ] Add error boundaries

### Phase 4: Prompt Runner
- [ ] Build PromptLibraryTable with TanStack Table
- [ ] Build PromptRunnerModal with shadcn Dialog
- [ ] Add template CRUD operations
- [ ] Implement validation gate
- [ ] Add metrics dashboard
- [ ] Add optimistic updates

### Phase 5: Job Scheduler
- [ ] Build JobScheduleTable
- [ ] Create GanttTimeline component
- [ ] Build JobCard components
- [ ] Implement TaskLogsTable with filters
- [ ] Add job editor with cron expression builder
- [ ] Add real-time job status updates

### Phase 6: Additional Modules
- [ ] System Health dashboard
- [ ] Storage Management
- [ ] Anomaly Detection Loop
- [ ] Hardware Telemetry
- [ ] Reports & Analytics
- [ ] Review Queue
- [ ] Import/Export

## Component Architecture

```
src/
├── pages/
│   ├── AIDashboardPage.tsx        # Overview
│   ├── AIPromptsPage.tsx          # Prompt Runner
│   ├── AIJobsPage.tsx             # Job Scheduler
│   ├── AIGovernancePage.tsx       # Governance
│   └── AIContextPage.tsx          # Context Management
├── components/
│   ├── ai/
│   │   ├── dashboard/
│   │   │   ├── NodeSummaryCard.tsx
│   │   │   ├── LiveMetricRings.tsx
│   │   │   ├── ActiveJobsPanel.tsx
│   │   │   └── QuickActionsBar.tsx
│   │   ├── prompts/
│   │   │   ├── PromptLibraryTable.tsx
│   │   │   ├── PromptRunnerModal.tsx
│   │   │   ├── TemplateEditor.tsx
│   │   │   └── ValidationGate.tsx
│   │   ├── jobs/
│   │   │   ├── JobScheduleTable.tsx
│   │   │   ├── GanttTimeline.tsx
│   │   │   ├── JobCard.tsx
│   │   │   └── TaskLogsTable.tsx
│   │   └── shared/
│   │       ├── MetricRing.tsx
│   │       ├── ProgressBar.tsx
│   │       └── StatusBadge.tsx
│   └── ui/
│       └── shadcn/      # Existing shadcn components
├── lib/
│   ├── ai-api.ts                  # API client
│   ├── ai-types.ts                # TypeScript interfaces
│   ├── ai-queries.ts              # TanStack Query hooks
│   └── ai-utils.ts                # Utilities
└── hooks/
    ├── useAIOverview.ts           # Dashboard data
    ├── usePrompts.ts              # Prompts data
    └── useJobs.ts                 # Jobs data
```

## Data Contracts

### Overview Data
```typescript
interface AIOverview {
  node: {
    hostname: string;
    uptime: number;
    os: string;
    model_versions: Record<string, string>;
  };
  metrics: {
    cpu: number;      // 0-100
    gpu: number;      // 0-100
    ram: number;      // 0-100
    disk: number;     // 0-100
    network: number;  // Mbps
  };
  thresholds: {
    warning: number;  // 75
    critical: number; // 90
  };
}

interface Job {
  id: number;
  name: string;
  state: 'running' | 'queued' | 'completed' | 'failed';
  progress: number; // 0-100
  eta: string;      // ISO date
  started_at: string;
  template_id?: number;
}
```

### Prompt Templates
```typescript
interface PromptTemplate {
  id: number;
  name: string;
  description: string;
  template: string;
  version: string;
  tags: string[];
  metrics: {
    success_rate: number;
    total_runs: number;
    avg_duration: number;
    rejection_count: number;
  };
  created_at: string;
  updated_at: string;
}

interface PromptRun {
  template_id: number;
  context: Record<string, any>;
  validate?: boolean;
}
```

### Scheduled Jobs
```typescript
interface ScheduledJob {
  id: number;
  name: string;
  description: string;
  schedule: string;      // cron expression
  enabled: boolean;
  last_run?: string;
  next_run: string;
  task_type: string;
  config: Record<string, any>;
}

interface TaskLog {
  id: number;
  job_id: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  started_at: string;
  completed_at?: string;
  duration?: number;
  output?: string;
  error?: string;
}
```

## Query Keys Convention

```typescript
// src/lib/ai-queries.ts
export const aiKeys = {
  all: ['ai'] as const,
  overview: () => [...aiKeys.all, 'overview'] as const,
  jobs: () => [...aiKeys.all, 'jobs'] as const,
  jobsByState: (state: string) => [...aiKeys.jobs(), state] as const,
  prompts: () => [...aiKeys.all, 'prompts'] as const,
  promptById: (id: number) => [...aiKeys.prompts(), id] as const,
  promptStats: () => [...aiKeys.prompts(), 'stats'] as const,
  scheduler: () => [...aiKeys.all, 'scheduler'] as const,
  taskLogs: (filters: any) => [...aiKeys.all, 'task-logs', filters] as const,
};
```

## Real-time Updates

### Option 1: Polling (Simple)
```typescript
const { data } = useQuery({
  queryKey: aiKeys.overview(),
  queryFn: fetchOverview,
  refetchInterval: 5000, // Poll every 5 seconds
});
```

### Option 2: SSE (Better)
```typescript
useEffect(() => {
  const eventSource = new EventSource('/api/ai/stream');
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    queryClient.setQueryData(aiKeys.overview(), data);
  };
  return () => eventSource.close();
}, []);
```

### Option 3: WebSocket (Best)
```typescript
const ws = useWebSocket('/api/ai/ws');
useEffect(() => {
  if (ws.data) {
    queryClient.setQueryData(aiKeys.overview(), ws.data);
  }
}, [ws.data]);
```

## Accessibility Checklist

- [ ] All interactive elements have focus states
- [ ] Keyboard navigation works (Tab, Enter, ESC)
- [ ] ARIA labels on all controls
- [ ] Color contrast meets AA standard
- [ ] Loading states announced to screen readers
- [ ] Error messages are clear and actionable
- [ ] Forms have proper validation messages

## Testing Strategy

- **Unit Tests:** Vitest + Testing Library for components
- **Integration Tests:** Test data fetching with Mock Service Worker
- **E2E Tests:** Playwright for critical user flows
- **Visual Tests:** Chromatic or Percy (optional)

## Performance Optimizations

- [ ] Code splitting for AI routes
- [ ] Lazy load charts and heavy components
- [ ] Virtual scrolling for large tables
- [ ] Debounce search inputs
- [ ] Optimize re-renders with React.memo
- [ ] Use TanStack Query caching effectively
- [ ] Skeleton loaders for perceived speed

## Next Steps

1. ✅ Create this adaptation plan
2. Install TanStack Query
3. Create API client with mock data
4. Enhance AIDashboardPage with spec features
5. Add real-time metrics
6. Implement Prompt Runner
7. Build Job Scheduler
8. Add remaining modules progressively

## Notes

- Keep existing CRM functionality intact
- Use shadcn components for consistency
- Follow existing design tokens and styles
- Maintain current authentication flow
- No breaking changes to existing pages
- Progressive enhancement approach
