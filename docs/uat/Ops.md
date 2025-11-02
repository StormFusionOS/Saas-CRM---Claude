# Ops Console SPA - User Acceptance Test (UAT) Script

**Application:** RiverCityClean Operations Console
**Version:** 0.1.0
**Test Type:** Business User Validation (No Terminal Required)
**Duration:** ~15 minutes

---

## Pre-Test Setup

**Access the Application:**
- Open your web browser (Chrome, Firefox, Safari, or Edge)
- Navigate to: `http://localhost:3001` (or scan QR code provided)
- Ensure you're on a desktop or laptop for best experience

**Test Credentials:**
- **Email:** `ops@RiverCityClean.com`
- **Password:** `opspassword123`

---

## Test Steps

### Step 1: Access Login Page
**Route:** `/login`

**Actions:**
1. Open the Ops Console application URL in your browser
2. You should be automatically redirected to the login page

**Expected Result:**
- ✅ Page displays "Operations Login" or similar heading in gradient text
- ✅ Subtitle indicates this is an operations/admin portal
- ✅ Form contains two input fields (Email and Password)
- ✅ "Sign In" button is visible
- ✅ Background has dark theme
- ✅ Login card has glass-morphism effect

**Visual Cue:** Look for operations-themed login heading with dark background

---

### Step 2: Test Invalid Login
**Route:** `/login`

**Actions:**
1. Enter an invalid email: `wrong@ops.com`
2. Enter an invalid password: `wrongpass`
3. Click "Sign In" button

**Expected Result:**
- ✅ Error message appears in red/pink error banner
- ✅ Error indicates authentication failure
- ✅ You remain on the login page
- ✅ Form remains interactive

**Visual Cue:** Red error banner appears above or within the form

---

### Step 3: Successful Login
**Route:** `/login` → `/dashboard`

**Actions:**
1. Clear both fields
2. Enter email: `ops@RiverCityClean.com`
3. Enter password: `opspassword123`
4. Click "Sign In" button

**Expected Result:**
- ✅ Page redirects to operations dashboard automatically
- ✅ URL changes to `/dashboard`
- ✅ No error messages
- ✅ Dashboard loads within 2 seconds

**Visual Cue:** URL bar changes from `/login` to `/dashboard`

---

### Step 4: Verify Ops Dashboard Layout
**Route:** `/dashboard`

**Actions:**
1. Observe the page heading
2. Scan the main content area
3. Note the overall color scheme

**Expected Result:**
- ✅ Page heading displays "Ops Dashboard"
- ✅ Dark background (gray-900 or similar)
- ✅ White text for good contrast
- ✅ Three metric tiles visible in a row (on desktop)
- ✅ Page has consistent padding and spacing

**Visual Cue:** "Ops Dashboard" heading in large, bold white text

---

### Step 5: Verify Services Status Tile
**Route:** `/dashboard`

**Actions:**
1. Locate the first tile labeled "Services"
2. Read the displayed values

**Expected Result:**
- ✅ Tile heading: "Services"
- ✅ Large number display: "12 / 12" in green color
- ✅ Tile has dark background (gray-800)
- ✅ Tile has rounded corners
- ✅ Green color indicates healthy status

**Visual Cue:** Green "12 / 12" text showing all services operational

---

### Step 6: Verify Alerts Tile
**Route:** `/dashboard`

**Actions:**
1. Locate the second tile labeled "Alerts"
2. Read the displayed value

**Expected Result:**
- ✅ Tile heading: "Alerts"
- ✅ Large number: "3" in yellow/amber color
- ✅ Tile matches styling of other tiles
- ✅ Yellow color indicates warning level

**Visual Cue:** Yellow "3" indicating there are 3 active alerts

---

### Step 7: Verify CPU Usage Tile
**Route:** `/dashboard`

**Actions:**
1. Locate the third tile labeled "CPU Usage"
2. Read the displayed percentage

**Expected Result:**
- ✅ Tile heading: "CPU Usage"
- ✅ Large number: "45%" in blue color
- ✅ Tile matches styling of other tiles
- ✅ Blue color indicates normal/informational status

**Visual Cue:** Blue "45%" showing CPU utilization

---

### Step 8: Navigate to System Health
**Route:** `/dashboard` → `/health`

**Actions:**
1. Change the URL to: `http://localhost:3001/health`
2. Press Enter

**Expected Result:**
- ✅ Page navigates to System Health section
- ✅ Top header displays "System Health" in gradient text
- ✅ Status indicator shows "All Systems Operational" with green pulsing dot
- ✅ Glass-effect header bar is sticky at the top
- ✅ Multiple service cards are visible below

**Visual Cue:** "System Health" gradient heading with green pulsing dot status indicator

---

### Step 9: Verify Service Health Cards
**Route:** `/health`

**Actions:**
1. Count the service cards displayed
2. Read each service's status and metrics

**Expected Result:**

**You should see 4 service cards:**

**Card 1 - API Gateway:**
- ✅ Service name: "API Gateway"
- ✅ Status badge: "healthy" (green)
- ✅ Uptime: "99.98%"
- ✅ Latency: "45ms"

**Card 2 - Database Primary:**
- ✅ Service name: "Database Primary"
- ✅ Status badge: "healthy" (green)
- ✅ Uptime: "99.99%"
- ✅ Latency: "12ms"

**Card 3 - Redis Cache:**
- ✅ Service name: "Redis Cache"
- ✅ Status badge: "healthy" (green)
- ✅ Uptime: "100%"
- ✅ Latency: "3ms"

**Card 4 - Worker Queue:**
- ✅ Service name: "Worker Queue"
- ✅ Status badge: "degraded" (yellow/amber)
- ✅ Uptime: "97.5%"
- ✅ Latency: "120ms"

**Visual Cue:** Cards have neon accent bars at the bottom - green for healthy, yellow/orange for degraded

---

### Step 10: Verify Service Card Interactivity
**Route:** `/health`

**Actions:**
1. Hover your mouse over each service card
2. Observe any visual effects

**Expected Result:**
- ✅ Cards have subtle glow or elevation effect on hover
- ✅ Neon accent bar at bottom glows more intensely on hover
- ✅ Cursor changes to indicate interactivity
- ✅ Card transitions are smooth (no jarring movements)

**Visual Cue:** Neon glow intensifies when hovering over cards

---

### Step 11: Test Status Badge Color Coding
**Route:** `/health`

**Actions:**
1. Identify the "Worker Queue" card (should show "degraded")
2. Compare its status badge and accent bar to healthy services

**Expected Result:**
- ✅ "Worker Queue" has yellow/amber "degraded" badge
- ✅ Bottom accent bar is yellow/orange (vs green for healthy)
- ✅ Badge has colored background matching status
- ✅ Text is readable against badge background
- ✅ Color coding is consistent and intuitive

**Visual Cue:** Yellow/amber warning color clearly differentiates degraded service from healthy ones

---

### Step 12: Test Visual Accessibility Page
**Route:** `/health` → `/visual-check`

**Actions:**
1. Navigate to: `http://localhost:3001/visual-check`
2. Observe the page content

**Expected Result:**
- ✅ Page loads successfully
- ✅ Visual components are displayed
- ✅ UI demonstrates design system components
- ✅ Consistent dark theme throughout
- ✅ Components showcase accessibility features

**Visual Cue:** Page displays various UI components for validation

---

## Test Completion Checklist

**Overall Application Quality:**
- [ ] All 12 test steps completed successfully
- [ ] No console errors (press F12 to verify)
- [ ] Page load times acceptable (< 3 seconds)
- [ ] Dark theme consistent across all pages
- [ ] Text contrast is readable (white on dark)
- [ ] Color coding is intuitive (green = healthy, yellow = warning)
- [ ] Service metrics display correctly
- [ ] Status badges render properly
- [ ] Neon effects and gradients work smoothly
- [ ] Application feels professional and responsive

**Dashboard Metrics:**
- [ ] Services tile shows "12 / 12" in green
- [ ] Alerts tile shows "3" in yellow
- [ ] CPU Usage tile shows "45%" in blue
- [ ] All tiles have consistent styling
- [ ] Numbers are large and easily readable

**System Health Page:**
- [ ] All 4 service cards display
- [ ] Each card shows: name, status, uptime, latency
- [ ] 3 services show "healthy" status
- [ ] 1 service shows "degraded" status
- [ ] Status badges use appropriate colors
- [ ] Neon accent bars match status (green/yellow)
- [ ] "All Systems Operational" status indicator present
- [ ] Green pulsing dot animation works

**Navigation:**
- [ ] URL changes reflect current page
- [ ] Direct URL access works
- [ ] Browser back/forward buttons work
- [ ] Refresh maintains route

**Authentication:**
- [ ] Login works with correct credentials
- [ ] Login fails with wrong credentials
- [ ] Error messages are clear
- [ ] Session persists across refreshes

---

## Issues Found

**Instructions:** Document any issues encountered during testing

| Step | Issue Description | Severity | Screenshot/Notes |
|------|------------------|----------|------------------|
| #    |                  | Low/Med/High |               |
| #    |                  | Low/Med/High |               |
| #    |                  | Low/Med/High |               |

---

## Functional Observations

**Instructions:** Note any functional observations or suggestions

**Services Monitoring:**
- Does the "12 / 12" services count make sense for your infrastructure?
- Are the 4 displayed services the correct ones to monitor?
- Is the "degraded" Worker Queue status expected or concerning?

**Metrics Accuracy:**
- Do the uptime percentages align with your SLA targets?
- Are latency values within expected ranges?
- Would you like to see additional metrics (memory, disk, network)?

**Visual Design:**
- Is the dark theme appropriate for operations monitoring?
- Are colors intuitive (green = good, yellow = warning)?
- Is text size large enough for at-a-glance monitoring?

---

## Sign-Off

**Tester Name:** ___________________________
**Date:** ___________________________
**Result:** ⬜ PASS  ⬜ PASS WITH ISSUES  ⬜ FAIL

**Additional Comments:**

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________
