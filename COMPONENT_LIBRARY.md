# Component Library

## Overview

This document provides a comprehensive reference for the RiverCityClean CRM component library. All components are built with React + TypeScript and styled with Tailwind CSS following the design system.

---

## Core UI Components

### Button

**Location:** `crm/src/components/ui/Button.tsx`

A flexible button component with multiple variants, sizes, and built-in animations.

#### Features
- ✅ Four variants: primary, secondary, outline, ghost
- ✅ Three sizes: sm, md, lg
- ✅ Full-width support
- ✅ Hover scale animation (1.02x)
- ✅ Active press animation (0.98x)
- ✅ Disabled state with reduced opacity
- ✅ Focus ring for accessibility

#### Props

```typescript
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
}
```

#### Usage Examples

```tsx
import Button from '@/components/ui/Button';

// Primary CTA button
<Button variant="primary" size="lg">
  Get Started
</Button>

// Secondary action
<Button variant="secondary">
  Cancel
</Button>

// Outline button for less emphasis
<Button variant="outline" size="sm">
  Learn More
</Button>

// Ghost button for subtle actions
<Button variant="ghost">
  Skip
</Button>

// Full-width button
<Button fullWidth>
  Continue
</Button>

// With loading state
<Button disabled={loading}>
  {loading ? 'Processing...' : 'Submit'}
</Button>
```

#### Animations
- **Hover:** Scales to 102% with smooth transition
- **Active:** Scales to 98% for press feedback
- **Transition:** 250ms cubic-bezier easing

---

### Card

**Location:** `crm/src/components/ui/Card.tsx`

A versatile card component for content containers with entrance animations.

#### Features
- ✅ Three variants: default, glass, neon
- ✅ Three padding sizes: sm, md, lg
- ✅ Four entrance animations: none, fade-in, slide-in-up, scale-in
- ✅ Hover effects available via className
- ✅ Glass morphism support
- ✅ Neon border effects

#### Props

```typescript
interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass' | 'neon';
  padding?: 'sm' | 'md' | 'lg';
  animate?: 'none' | 'fade-in' | 'slide-in-up' | 'scale-in';
}
```

#### Usage Examples

```tsx
import Card from '@/components/ui/Card';

// Basic card with fade-in animation
<Card animate="fade-in">
  <h2>Card Title</h2>
  <p>Card content goes here</p>
</Card>

// Glass morphism card
<Card variant="glass" animate="slide-in-up">
  <p>Semi-transparent card with blur effect</p>
</Card>

// Neon border card with scale animation
<Card variant="neon" animate="scale-in">
  <p>Card with glowing cyan border</p>
</Card>

// Card with hover glow effect
<Card className="glow-hover" padding="lg">
  <p>Hover over this card</p>
</Card>

// Interactive clickable card
<Card
  animate="scale-in"
  className="glow-hover cursor-pointer"
  onClick={handleClick}
>
  <h3>Clickable Card</h3>
</Card>

// Compact card
<Card padding="sm">
  <p>Less padding for tight layouts</p>
</Card>
```

#### Animations
- **fade-in:** Opacity 0 → 1 over 250ms
- **slide-in-up:** Slides from 10px below while fading in
- **scale-in:** Scales from 95% to 100% while fading in

#### Variants
- **default:** Standard elevated card with border and shadow
- **glass:** Semi-transparent with backdrop blur (glass morphism)
- **neon:** Electric cyan border with glow effect

---

### Input

**Location:** `crm/src/components/ui/Input.tsx`

A styled input component with label, helper text, and error handling.

#### Features
- ✅ Label support
- ✅ Helper text
- ✅ Error state with message
- ✅ Disabled state
- ✅ Focus ring animation
- ✅ All HTML input types supported
- ✅ Accessible (proper labeling)

#### Props

```typescript
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  helperText?: string;
  error?: string;
}
```

#### Usage Examples

```tsx
import Input from '@/components/ui/Input';

// Basic text input
<Input
  id="email"
  label="Email Address"
  type="email"
  placeholder="you@example.com"
/>

// Input with helper text
<Input
  id="password"
  label="Password"
  type="password"
  helperText="Must be at least 8 characters"
/>

// Input with error
<Input
  id="username"
  label="Username"
  error="Username is already taken"
/>

// Number input with step
<Input
  id="price"
  label="Price"
  type="number"
  step="0.01"
  placeholder="0.00"
/>

// Disabled input
<Input
  id="readonly"
  label="Read Only"
  value="Cannot edit"
  disabled
/>

// Controlled input with state
const [value, setValue] = useState('');
<Input
  id="name"
  label="Name"
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

---

## Animation Utilities

### Available Animations

All animations are defined in `tailwind.config.js` and can be applied using Tailwind classes.

#### Entrance Animations

```tsx
// Fade in
<div className="animate-fade-in">Content</div>

// Fade out
<div className="animate-fade-out">Content</div>

// Slide in from bottom
<div className="animate-slide-in-up">Content</div>

// Slide in from top
<div className="animate-slide-in-down">Content</div>

// Slide in from left
<div className="animate-slide-in-left">Content</div>

// Slide in from right
<div className="animate-slide-in-right">Content</div>

// Scale in
<div className="animate-scale-in">Content</div>

// Bounce in (playful entrance)
<div className="animate-bounce-in">Content</div>
```

#### Continuous Animations

```tsx
// Pulsing glow effect
<div className="animate-pulse-glow">Glowing element</div>

// Shimmer effect (loading states)
<div className="animate-shimmer bg-gradient-to-r from-transparent via-white/10 to-transparent">
  Loading...
</div>

// Slow spin (for loading spinners)
<div className="animate-spin-slow">
  <LoadingIcon />
</div>
```

### Animation Timing

Use these classes to control animation behavior:

```tsx
// Animation delays
<div className="animate-fade-in delay-100">Delayed 100ms</div>
<div className="animate-fade-in delay-300">Delayed 300ms</div>

// Animation duration
<div className="animate-fade-in duration-fast">Fast (150ms)</div>
<div className="animate-fade-in duration-base">Base (250ms)</div>
<div className="animate-fade-in duration-slow">Slow (350ms)</div>

// Animation iteration
<div className="animate-pulse-glow animate-infinite">Never stops</div>
```

---

## Utility Classes

### Focus Ring

Accessible focus indicator for interactive elements:

```tsx
<button className="focus-ring">
  Accessible Button
</button>
```

### Glass Surface

Semi-transparent glass morphism effect:

```tsx
<div className="glass-surface p-6 rounded-lg">
  <p>Content with backdrop blur</p>
</div>
```

### Neon Border

Glowing cyan border effect:

```tsx
<div className="neon-border p-4 rounded-base">
  <p>Glowing border</p>
</div>
```

### Glow Hover

Adds a cyan glow effect on hover:

```tsx
<div className="glow-hover p-4 rounded-base bg-bg-elev cursor-pointer">
  <p>Hover me for glow</p>
</div>
```

### Text Gradient

Electric gradient text effect:

```tsx
<h1 className="text-gradient text-4xl font-bold">
  Gradient Text
</h1>
```

---

## Layout Components

### Navigation

**Location:** `crm/src/components/navigation/`

#### Sidebar Navigation
- Collapsible sidebar with suites
- Icon-only collapsed mode
- Badge support for notifications
- Role-based access control

#### Top Bar
- User profile dropdown
- Notifications
- Global search
- Theme toggle

---

## Best Practices

### Accessibility

1. **Always use labels for inputs:**
   ```tsx
   <Input id="email" label="Email" type="email" />
   ```

2. **Provide focus indicators:**
   ```tsx
   <button className="focus-ring">Button</button>
   ```

3. **Use semantic HTML:**
   ```tsx
   <Card as="article">
     <h2>Title</h2>
     <p>Content</p>
   </Card>
   ```

4. **Add ARIA labels when needed:**
   ```tsx
   <Button aria-label="Close dialog">×</Button>
   ```

### Performance

1. **Use animations sparingly:**
   - Don't animate everything
   - Prefer entrance animations over continuous ones
   - Respect `prefers-reduced-motion`

2. **Optimize re-renders:**
   - Use `React.memo()` for expensive components
   - Lift state appropriately
   - Use `useCallback` for event handlers

3. **Lazy load heavy components:**
   ```tsx
   const HeavyComponent = React.lazy(() => import('./HeavyComponent'));
   ```

### Design System Consistency

1. **Always use design tokens:**
   ```tsx
   // ✅ Good
   <div className="bg-bg-elev text-text-primary">

   // ❌ Bad
   <div className="bg-gray-800 text-white">
   ```

2. **Use semantic color names:**
   ```tsx
   // ✅ Good
   <Button variant="primary">Submit</Button>

   // ❌ Bad
   <button className="bg-blue-500">Submit</button>
   ```

3. **Follow spacing scale:**
   ```tsx
   // ✅ Good - Uses 4px scale
   <div className="p-6 gap-4">

   // ❌ Bad - Random values
   <div className="p-5 gap-3">
   ```

---

## Real-World Examples

### Formula Testing Lab Cards

From `FormulaTestingPage.tsx`:

```tsx
// Main formula editor card - slides in from bottom
<Card animate="slide-in-up">
  <h2 className="text-xl font-display font-semibold mb-4">Formula</h2>
  {/* Formula editor content */}
</Card>

// Tab content cards - fade in on tab change
{activeTab === 'single' && (
  <Card animate="fade-in">
    <h2>Test Variables</h2>
    {/* Test inputs */}
  </Card>
)}

// Example cards - scale in with hover glow
{examples.map((example, i) => (
  <Card
    key={i}
    animate="scale-in"
    className="glow-hover cursor-pointer"
    onClick={() => loadExample(example)}
  >
    <h3 className="text-gradient">{example.name}</h3>
    {/* Example details */}
  </Card>
))}

// Sidebar reference cards - slide in from bottom
<Card animate="slide-in-up">
  <h3>Quick Reference</h3>
  {/* Reference content */}
</Card>
```

### Dashboard Stats Cards

```tsx
// Stats cards with staggered animations
<div className="grid grid-cols-3 gap-6">
  <Card animate="scale-in" className="delay-0">
    <StatCard title="Revenue" value="$125,430" />
  </Card>
  <Card animate="scale-in" className="delay-100">
    <StatCard title="Customers" value="1,248" />
  </Card>
  <Card animate="scale-in" className="delay-200">
    <StatCard title="Growth" value="+23%" />
  </Card>
</div>
```

### Modal Dialog

```tsx
// Animated modal overlay and content
<div className="fixed inset-0 z-modal animate-fade-in">
  {/* Backdrop */}
  <div className="absolute inset-0 bg-black/50" />

  {/* Modal content */}
  <div className="relative flex items-center justify-center min-h-screen p-4">
    <Card
      variant="glass"
      animate="scale-in"
      className="max-w-md w-full"
    >
      <h2 className="text-2xl font-bold mb-4">Modal Title</h2>
      <p className="mb-6">Modal content goes here</p>
      <div className="flex gap-3">
        <Button variant="secondary" fullWidth>Cancel</Button>
        <Button variant="primary" fullWidth>Confirm</Button>
      </div>
    </Card>
  </div>
</div>
```

### Loading States

```tsx
// Loading spinner with shimmer
<div className="flex items-center justify-center p-8">
  <div className="relative">
    <div className="w-12 h-12 border-4 border-border-default border-t-primary rounded-full animate-spin-slow" />
  </div>
</div>

// Loading card with shimmer effect
<Card>
  <div className="space-y-3">
    <div className="h-4 bg-bg-hover rounded animate-shimmer" />
    <div className="h-4 bg-bg-hover rounded animate-shimmer" />
    <div className="h-4 w-3/4 bg-bg-hover rounded animate-shimmer" />
  </div>
</Card>

// Loading button state
<Button disabled={loading}>
  {loading && (
    <div className="mr-2 w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin-slow" />
  )}
  {loading ? 'Processing...' : 'Submit'}
</Button>
```

---

## Testing Components

### Visual Testing Checklist

When implementing new components or updating existing ones:

- [ ] Test all variants (default, glass, neon, etc.)
- [ ] Test all sizes (sm, md, lg)
- [ ] Test hover states
- [ ] Test focus states (keyboard navigation)
- [ ] Test disabled states
- [ ] Test with different content lengths
- [ ] Test on mobile/tablet/desktop breakpoints
- [ ] Test with light and dark themes (if applicable)
- [ ] Test animations (ensure smooth, no jank)
- [ ] Test accessibility with screen reader

### Animation Testing

1. **Performance:** Animations should run at 60fps
2. **Timing:** Follow design system timing (fast/base/slow)
3. **Reduced Motion:** Test with `prefers-reduced-motion: reduce`
4. **Mobile:** Ensure animations work smoothly on mobile devices

---

## Resources

- **Design System:** [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)
- **Test Coverage:** [TEST_COVERAGE.md](./TEST_COVERAGE.md)
- **Tailwind Config:** `crm/tailwind.config.js`
- **Design Tokens:** `crm/src/styles/tokens.css`
- **Component Source:** `crm/src/components/ui/`

---

## Changelog

### Version 1.1.0 (2025-11-03)
- ✨ Added entrance animations to Card component
- ✨ Added scale animations to Button component
- ✨ Enhanced animation utilities in Tailwind config
- 📝 Created comprehensive component library documentation
- 🎨 Applied animations to Formula Testing Lab

### Version 1.0.0 (2025-11-03)
- 🎉 Initial component library release
- 📦 Button, Card, Input components
- 🎨 Design system implementation
- ♿ Accessibility features

---

*Component Library maintained by the RiverCityClean Engineering Team*
*Last updated: 2025-11-03*
