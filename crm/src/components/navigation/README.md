# LeftSuitesNav Component

An accessible, collapsible left sidebar navigation component with five Suites (AI, SEO, Scrape, Sales, Admin). Built with React + TypeScript, featuring full ARIA support, keyboard navigation, and fuzzy search.

## Features

✅ **ARIA Tree Pattern** - Full `role="tree"` and `role="treeitem"` support
✅ **Keyboard Navigation** - ↑ ↓ → ← Home End Enter Space
✅ **LocalStorage Persistence** - Per-user suite open/closed state
✅ **Badge Counts** - Show pending items with badges (e.g., Review Queue, Anomalies)
✅ **Role-Based Filtering** - Hide items based on user roles
✅ **Fuzzy Search** - Quick filter with auto-expand and highlighting
✅ **Abstract Styling** - CSS variables for easy theming (Tailwind or CSS Modules)
✅ **Dark/Light Theme** - Built-in theme support
✅ **No External Dependencies** - Zero UI library dependencies

## File Structure

```
crm/src/components/navigation/
├── suites.config.ts          # SUITES data structure and types
├── LeftSuitesNav.tsx          # Main navigation component
├── LeftSuitesNav.css          # CSS variables and styling
├── LeftSuitesNavHarness.tsx   # Test harness/demo component
└── README.md                  # This file
```

## Quick Start

### 1. Import and Use

```tsx
import { LeftSuitesNav } from './components/navigation/LeftSuitesNav';
import './components/navigation/LeftSuitesNav.css';

function App() {
  const [activeRoute, setActiveRoute] = useState('/ai/prompt-runner');

  return (
    <LeftSuitesNav
      activeRoute={activeRoute}
      userRoles={['ADMIN', 'SALES']}
      onNavigate={(route) => {
        setActiveRoute(route);
        // Your navigation logic here
      }}
      badges={{
        reviewQueue: 12,
        anomalyCount: 3,
        pendingChanges: 5,
      }}
      userId="user-123"
    />
  );
}
```

### 2. Run Test Harness

```tsx
import { LeftSuitesNavHarness } from './components/navigation/LeftSuitesNavHarness';

function App() {
  return <LeftSuitesNavHarness />;
}
```

## Props API

```typescript
interface LeftSuitesNavProps {
  /** Current active route path */
  activeRoute: string;

  /** User's roles for filtering available tools */
  userRoles: string[];

  /** Callback when navigation item is clicked */
  onNavigate: (route: string) => void;

  /** Optional badge counts (key: badgeKey from tool, value: count) */
  badges?: Record<string, number>;

  /** Optional icon mapping function */
  renderIcon?: (iconName: string) => React.ReactNode;

  /** Optional CSS class name for styling */
  className?: string;

  /** LocalStorage key for persisting state (defaults to 'suites-nav-state') */
  storageKey?: string;

  /** User ID for user-specific state (defaults to 'default') */
  userId?: string;
}
```

## SUITES Configuration

The menu structure is defined in `suites.config.ts`:

```typescript
export type ToolItem = {
  id: string;
  label: string;
  route: string;
  icon?: string;
  roles?: string[];
  description?: string;
  badgeKey?: string; // Maps to badges prop
};

export type Suite = {
  id: string;
  label: string;
  icon?: string;
  defaultOpen?: boolean;
  items: ToolItem[];
};

export const SUITES: Suite[] = [
  // 5 suites: AI, SEO, Scrape, Sales, Admin
  // See suites.config.ts for full structure
];
```

### Suites Overview

1. **AI Suite** (10 tools) - AI-powered content generation and analysis
2. **SEO Suite** (6 tools) - SEO management, schema, and reporting
3. **Scrape Suite** (8 tools) - Data acquisition and monitoring
4. **Sales Suite** (7 tools) - CRM, pipeline, quotes, and portal
5. **Admin Suite** (9 tools) - System governance and integrations

## Keyboard Navigation

| Key | Action |
|-----|--------|
| `↑` | Move to previous item |
| `↓` | Move to next item |
| `→` | Expand suite (if collapsed) |
| `←` | Collapse suite (if expanded) or move to parent |
| `Home` | Move to first item |
| `End` | Move to last item |
| `Enter` / `Space` | Activate item (navigate or toggle suite) |

## Fuzzy Search

Type in the search box to filter tools:
- Auto-expands suites with matches
- Highlights matching characters
- Press `×` or clear input to reset
- Search works on tool labels and routes

## Badge System

Badges show counts for items requiring attention:

```tsx
<LeftSuitesNav
  badges={{
    reviewQueue: 12,      // Review Queue (AI + Admin)
    anomalyCount: 3,      // Rank/Traffic Anomaly Explainer
    pendingChanges: 5,    // Change Log & Approvals
    auditIssues: 8,       // Technical/A11y Audit
    unread: 24,           // Unified Inbox
    healthAlerts: 2,      // System Health & Alerts
  }}
/>
```

Badges only show when count > 0.

## Role-Based Filtering

Tools with `roles` array require user to have at least one matching role:

```typescript
{
  id: 'users',
  label: 'Users & Roles',
  route: '/admin/users',
  roles: ['ADMIN'],  // Only visible to ADMIN users
}
```

The `filterSuitesByRoles()` helper handles filtering automatically.

## Theming

### CSS Variables

Override CSS variables in your stylesheet:

```css
:root {
  --suite-nav-bg: #0f1419;
  --suite-nav-text-primary: #e6edf3;
  --suite-nav-tool-active-border: #00d9ff;
  /* See LeftSuitesNav.css for full list */
}
```

### Light Theme

Apply `data-theme="light"` to parent element:

```tsx
<div data-theme="light">
  <LeftSuitesNav {...props} />
</div>
```

### Custom Icons

Provide custom icon renderer:

```tsx
import { FaBolt, FaTarget } from 'react-icons/fa';

const iconMap = {
  bolt: <FaBolt />,
  target: <FaTarget />,
  // ...
};

<LeftSuitesNav
  renderIcon={(iconName) => iconMap[iconName] || <FaCircle />}
  {...props}
/>
```

## LocalStorage Persistence

Suite open/closed state is persisted per user:

```
localStorage key: `${storageKey}-${userId}`
value: ["ai", "sales"]  // Array of open suite IDs
```

Change the storage key via props:

```tsx
<LeftSuitesNav
  storageKey="my-custom-nav-state"
  userId={currentUser.id}
  {...props}
/>
```

## Accessibility

- ✅ `<nav>` landmark with `aria-label="Main navigation"`
- ✅ ARIA tree pattern (`role="tree"`, `role="treeitem"`, `role="group"`)
- ✅ `aria-expanded` on suite buttons
- ✅ `aria-current="page"` on active route
- ✅ All interactive elements keyboard accessible
- ✅ Focus management with `tabIndex` roving
- ✅ Screen reader labels for badges

## Integration Tips

### With React Router

```tsx
import { useNavigate, useLocation } from 'react-router-dom';

function Layout() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <LeftSuitesNav
      activeRoute={location.pathname}
      onNavigate={(route) => navigate(route)}
      {...props}
    />
  );
}
```

### With Next.js

```tsx
import { useRouter } from 'next/router';

function Layout() {
  const router = useRouter();

  return (
    <LeftSuitesNav
      activeRoute={router.pathname}
      onNavigate={(route) => router.push(route)}
      {...props}
    />
  );
}
```

### Mobile Responsive

On mobile, the search box becomes sticky at the top:

```css
@media (max-width: 768px) {
  .suite-nav-search {
    position: sticky;
    top: 0;
    z-index: 10;
  }
}
```

Consider auto-collapsing all suites on mobile for better UX.

## Examples

### Minimal Setup

```tsx
<LeftSuitesNav
  activeRoute="/ai/prompt-runner"
  userRoles={['SALES']}
  onNavigate={(route) => console.log('Navigate to:', route)}
/>
```

### Full-Featured Setup

```tsx
<LeftSuitesNav
  activeRoute={currentRoute}
  userRoles={user.roles}
  onNavigate={handleNavigation}
  badges={badgeCounts}
  renderIcon={customIconRenderer}
  className="my-custom-nav"
  storageKey="app-nav-state"
  userId={user.id}
/>
```

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support

## License

MIT License - Copyright (c) 2025 RiverCityClean

## Support

For issues or questions, please refer to the test harness (`LeftSuitesNavHarness.tsx`) for working examples of all features.
