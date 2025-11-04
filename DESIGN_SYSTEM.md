# RiverCityClean CRM Design System

## Overview

This design system provides a consistent visual language and component library for the RiverCityClean SaaS CRM platform. The system is built on a dark-first theme with electric blue and cyan accents, optimized for professional use.

---

## Design Principles

### 1. **Dark-First & Professional**
- Dark backgrounds reduce eye strain during extended use
- High contrast for readability
- Electric cyan accents for key interactions

### 2. **Consistent & Predictable**
- Reusable components with consistent behavior
- Standardized spacing and sizing
- Predictable interaction patterns

### 3. **Accessible & Inclusive**
- WCAG AA compliant color contrast
- Keyboard navigation support
- Clear focus indicators

### 4. **Fast & Responsive**
- Smooth animations (150-350ms)
- Optimized for performance
- Mobile-responsive layouts

---

## Color System

### Brand Colors

```css
Storm Blue:      #005AE0  /* Primary brand color */
Electric Cyan:   #00B7FD  /* Accent color */
Midnight:        #041631  /* Deep background */
Deep Ocean:      #0A2647  /* Secondary background */
Steel Gray:      #7A8B99  /* Neutral */
```

### Semantic Colors

#### Backgrounds
```css
--color-bg-base:   #0A0F1C  /* Base background */
--color-bg-elev:   #12192B  /* Elevated surfaces (cards, modals) */
--color-bg-hover:  #1A2538  /* Hover states */
--color-bg-active: #243447  /* Active/pressed states */
```

#### Text
```css
--color-text-primary:   #FFFFFF  /* Primary text */
--color-text-secondary: #A8B4C4  /* Secondary text */
--color-text-muted:     #6B7A8D  /* Muted/disabled text */
--color-text-inverse:   #0A0F1C  /* Text on light backgrounds */
```

#### Borders
```css
--color-border-subtle:  rgba(255, 255, 255, 0.06)  /* Subtle dividers */
--color-border-default: rgba(255, 255, 255, 0.12)  /* Standard borders */
--color-border-strong:  rgba(255, 255, 255, 0.24)  /* Emphasized borders */
```

#### Status Colors
```css
Success:  #10B981  /* Green - success states */
Warning:  #F59E0B  /* Amber - warning states */
Error:    #EF4444  /* Red - error states */
Info:     #3B82F6  /* Blue - informational states */
```

### Color Usage

| Use Case | Color | When to Use |
|----------|-------|-------------|
| Primary Actions | Storm Blue (#005AE0) | CTAs, primary buttons, important actions |
| Secondary Actions | Electric Cyan (#00B7FD) | Links, secondary buttons, highlights |
| Success | Green (#10B981) | Successful operations, completed states |
| Warning | Amber (#F59E0B) | Warnings, pending states |
| Error | Red (#EF4444) | Errors, destructive actions |
| Info | Blue (#3B82F6) | Informational messages, tooltips |

---

## Typography

### Font Families

```css
Sans-serif (Body):    Inter
Display (Headings):   Sora
Monospace (Code):     IBM Plex Mono
```

### Type Scale

| Level | Size | Weight | Line Height | Use Case |
|-------|------|--------|-------------|----------|
| Display | 48px | 700 | 1.2 | Hero sections |
| H1 | 36px | 600 | 1.2 | Page titles |
| H2 | 30px | 600 | 1.3 | Section headings |
| H3 | 24px | 600 | 1.4 | Subsection headings |
| H4 | 20px | 600 | 1.5 | Card titles |
| H5 | 18px | 600 | 1.5 | Small headings |
| Body Large | 16px | 400 | 1.6 | Large body text |
| Body | 14px | 400 | 1.6 | Default body text |
| Body Small | 12px | 400 | 1.5 | Small text, captions |
| Code | 14px | 400 | 1.5 | Code blocks, formulas |

### Font Weights

- **Regular (400)**: Body text
- **Medium (500)**: Emphasized text
- **Semi-Bold (600)**: Headings, buttons
- **Bold (700)**: Display text, strong emphasis

---

## Spacing System

### Scale

Based on 4px base unit (0.25rem):

```
0   = 0px
1   = 4px    (0.25rem)
2   = 8px    (0.5rem)
3   = 12px   (0.75rem)
4   = 16px   (1rem)
5   = 20px   (1.25rem)
6   = 24px   (1.5rem)
8   = 32px   (2rem)
10  = 40px   (2.5rem)
12  = 48px   (3rem)
16  = 64px   (4rem)
20  = 80px   (5rem)
24  = 96px   (6rem)
```

### Usage Guidelines

| Spacing | Usage |
|---------|-------|
| 2-3 (8-12px) | Compact padding, icon spacing |
| 4 (16px) | Default padding, button padding |
| 6 (24px) | Card padding, section spacing |
| 8 (32px) | Large section spacing |
| 12+ (48px+) | Major section dividers |

---

## Border Radius

```css
--radius-sm:   6px    /* Small elements, badges */
--radius-base: 12px   /* Default (buttons, inputs, cards) */
--radius-lg:   16px   /* Large cards, modals */
--radius-full: 9999px /* Pills, circular buttons */
```

---

## Shadows & Elevation

### Shadow Scale

```css
--shadow-sm:   Subtle shadow for subtle elevation
--shadow-base: Default shadow for cards
--shadow-md:   Medium shadow for dropdowns
--shadow-lg:   Large shadow for modals, overlays
```

### Glow Effects

```css
--shadow-glow-cyan: Cyan glow for interactive elements
--shadow-glow-blue: Blue glow for hover states
```

### Elevation Levels

| Level | Use Case | Shadow |
|-------|----------|--------|
| 0 | Flat elements, embedded content | none |
| 1 | Cards, tiles | shadow-base |
| 2 | Dropdowns, tooltips | shadow-md |
| 3 | Modals, dialogs | shadow-lg |
| Glow | Interactive hover states | glow-cyan/blue |

---

## Animation & Motion

### Timing Functions

```css
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1)  /* Quick interactions */
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1)  /* Default transitions */
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1)  /* Slower, deliberate */
```

### Motion Principles

1. **Fast Feedback** (150ms)
   - Button presses
   - Toggle switches
   - Checkbox/radio selection

2. **Standard Transitions** (250ms)
   - Hover states
   - Color changes
   - Opacity changes
   - Scale transforms

3. **Deliberate Motions** (350ms)
   - Modal appearances
   - Drawer slides
   - Page transitions

### Animation Guidelines

- **Keep it subtle**: Animations should enhance, not distract
- **Use cubic-bezier**: Natural easing for smooth motion
- **Respect reduce-motion**: Honor user preferences
- **Consistent timing**: Use predefined durations

---

## Component Patterns

### Buttons

#### Variants

```tsx
<Button variant="primary">   Primary Action   </Button>
<Button variant="secondary"> Secondary Action </Button>
<Button variant="outline">   Outline Button   </Button>
<Button variant="ghost">     Ghost Button     </Button>
```

#### Sizes

```tsx
<Button size="sm">  Small  </Button>
<Button size="md">  Medium </Button>  {/* Default */}
<Button size="lg">  Large  </Button>
```

#### States
- Default
- Hover (scale + glow)
- Active (pressed)
- Disabled (reduced opacity)
- Loading (with spinner)

### Cards

```tsx
<Card>                    {/* Standard card */}
<Card className="glow-hover"> {/* With hover glow */}
<Card className="glass-surface"> {/* Glass morphism */}
```

#### Card Anatomy
- Padding: 24px (1.5rem)
- Border radius: 12px
- Background: bg-elev
- Border: 1px solid border-default

### Inputs

```tsx
<Input
  label="Field Label"
  placeholder="Enter text..."
  helperText="Helper text"
  error="Error message"
/>
```

#### Input States
- Default
- Focus (cyan ring)
- Error (red border + message)
- Disabled (reduced opacity)

---

## Utility Classes

### Focus Ring

```css
.focus-ring:focus {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}
```

### Glass Surface

```css
.glass-surface {
  backdrop-filter: blur(12px);
  background-color: rgba(18, 25, 43, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Neon Border

```css
.neon-border {
  box-shadow: 0 0 0 1px var(--color-electric-cyan),
              0 0 10px rgba(0, 183, 253, 0.3);
}
```

### Glow Hover

```css
.glow-hover:hover {
  box-shadow: var(--shadow-glow-cyan);
}
```

### Text Gradient

```css
.text-gradient {
  background: linear-gradient(135deg,
    var(--color-electric-cyan),
    var(--color-storm-blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## Accessibility

### Color Contrast

All color combinations meet WCAG AA standards:
- Text on backgrounds: minimum 4.5:1 contrast
- Large text (18px+): minimum 3:1 contrast
- UI components: minimum 3:1 contrast

### Keyboard Navigation

All interactive elements support:
- Tab navigation
- Enter/Space activation
- Escape to close modals
- Arrow keys for lists/menus

### Focus Indicators

- Visible focus rings (2px cyan outline)
- 2px offset from element
- High contrast with background

### Screen Readers

- Semantic HTML elements
- ARIA labels where needed
- Proper heading hierarchy
- Alt text for images

---

## Responsive Breakpoints

```css
sm:  640px   /* Small devices */
md:  768px   /* Tablets */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
2xl: 1536px  /* Extra large */
```

### Mobile-First Approach

```tsx
{/* Mobile default, desktop override */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
```

---

## Z-Index Scale

```css
--z-base:     1    /* Base level */
--z-elevated: 10   /* Elevated elements */
--z-modal:    100  /* Modals */
--z-popover:  200  /* Popovers, dropdowns */
--z-tooltip:  300  /* Tooltips (top layer) */
```

---

## Usage Examples

### Creating a Card with Glow Effect

```tsx
<Card className="glow-hover">
  <h3 className="text-xl font-display font-semibold text-gradient">
    Card Title
  </h3>
  <p className="text-text-secondary mt-2">
    Card content goes here...
  </p>
</Card>
```

### Button with Loading State

```tsx
<Button
  onClick={handleSubmit}
  disabled={loading}
>
  {loading ? 'Saving...' : 'Save Changes'}
</Button>
```

### Input with Validation

```tsx
<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={emailError}
  helperText="We'll never share your email"
/>
```

---

## Resources

### Design Tokens
- `src/styles/tokens.css` - CSS custom properties
- `tailwind.config.js` - Tailwind configuration

### Components
- `src/components/ui/` - Reusable UI components
- `src/components/layout/` - Layout components

### Documentation
- `DESIGN_SYSTEM.md` - This file
- `COMPONENT_LIBRARY.md` - Component API reference

---

## Changelog

### Version 1.0.0 (2025-11-03)
- Initial design system documentation
- Color system established
- Typography scale defined
- Component patterns documented
- Accessibility guidelines added

---

*Design System maintained by the RiverCityClean Engineering Team*
*Last updated: 2025-11-03*
