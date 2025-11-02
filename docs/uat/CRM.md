# CRM SPA - User Acceptance Test (UAT) Script

**Application:** RiverCityClean CRM
**Version:** 0.1.0
**Test Type:** Business User Validation (No Terminal Required)
**Duration:** ~15 minutes

---

## Pre-Test Setup

**Access the Application:**
- Open your web browser (Chrome, Firefox, Safari, or Edge)
- Navigate to: `http://localhost:3000` (or scan QR code provided)
- Ensure you're on a desktop or laptop for best experience

**Test Credentials:**
- **Email:** `Nathan@RiverCityClean.com`
- **Password:** `password123`

---

## Test Steps

### Step 1: Access Login Page
**Route:** `/login`

**Actions:**
1. Open the CRM application URL in your browser
2. You should be automatically redirected to the login page

**Expected Result:**
- ✅ Page displays "CRM Login" heading in gradient blue text
- ✅ Subtitle shows "RiverCityClean Customer Portal"
- ✅ Form contains two input fields (Email and Password)
- ✅ "Sign In" button is visible at the bottom
- ✅ Background has a dark theme with subtle blue radial gradient
- ✅ Login card has a glass-morphism effect (semi-transparent with blur)

**Visual Cue:** Look for the gradient blue "CRM Login" text at the top center of the card

---

### Step 2: Test Invalid Login
**Route:** `/login`

**Actions:**
1. Clear the email field
2. Enter: `wrong@email.com`
3. Clear the password field
4. Enter: `wrongpassword`
5. Click the "Sign In" button

**Expected Result:**
- ✅ Error message appears above the form in red/pink background
- ✅ Error text reads "Login failed" or similar message
- ✅ You remain on the login page
- ✅ Form fields remain editable

**Visual Cue:** Red/pink error banner with error icon appears below the heading

---

### Step 3: Successful Login
**Route:** `/login` → `/dashboard`

**Actions:**
1. Clear both fields
2. Enter email: `Nathan@RiverCityClean.com`
3. Enter password: `password123`
4. Click "Sign In" button

**Expected Result:**
- ✅ Page redirects to dashboard automatically
- ✅ URL changes to `/dashboard`
- ✅ No error messages appear
- ✅ Dashboard content loads within 2 seconds

**Visual Cue:** URL bar changes from `/login` to `/dashboard`

---

### Step 4: Verify Dashboard Layout
**Route:** `/dashboard`

**Actions:**
1. Observe the top header bar
2. Scan the main content area

**Expected Result:**
- ✅ Top bar displays "Dashboard" heading in gradient text (left side)
- ✅ "RiverCityClean CRM" text visible in top right corner
- ✅ Top bar has a glass/frosted effect and stays sticky when scrolling
- ✅ Main content area has dark background
- ✅ Three KPI cards are visible in a row (on desktop)

**Visual Cue:** The word "Dashboard" appears in a blue-to-cyan gradient in the top left

---

### Step 5: Verify KPI Cards
**Route:** `/dashboard`

**Actions:**
1. Locate the three metric cards below the header
2. Read each card's content

**Expected Result:**

**Card 1 - New Leads:**
- ✅ Heading: "New Leads"
- ✅ Large number: "24"
- ✅ Subtitle: "↑ 12% from last week"
- ✅ Blue glow effect on hover

**Card 2 - In Progress:**
- ✅ Heading: "In Progress"
- ✅ Large number: "12"
- ✅ Subtitle: "Active conversations"
- ✅ Cyan glow effect on hover

**Card 3 - Closed Won:**
- ✅ Heading: "Closed Won"
- ✅ Large number: "8"
- ✅ Subtitle: "This month"
- ✅ Green glow effect on hover

**Visual Cue:** Each card has a colored glow orb in the top-right corner (blue, cyan, green respectively)

---

### Step 6: Verify Recent Activity Section
**Route:** `/dashboard`

**Actions:**
1. Scroll down below the KPI cards
2. Locate the "Recent Activity" card

**Expected Result:**
- ✅ Card displays "Recent Activity" heading
- ✅ Placeholder text: "Activity feed coming soon..."
- ✅ Card has consistent styling with glass effect
- ✅ Card has padding and is easy to read

**Visual Cue:** Large white card with "Recent Activity" heading

---

### Step 7: Navigate to Leads Page
**Route:** `/dashboard` → `/leads`

**Actions:**
1. Manually change the URL to: `http://localhost:3000/leads`
2. Press Enter

**Expected Result:**
- ✅ Page navigates to Leads section
- ✅ Heading displays "Leads Pipeline"
- ✅ Subtitle text: "Kanban board view of leads by status"
- ✅ Page loads without errors
- ✅ URL bar shows `/leads`

**Visual Cue:** "Leads Pipeline" heading is visible

---

### Step 8: Navigate to Inbox
**Route:** `/leads` → `/inbox`

**Actions:**
1. Change the URL to: `http://localhost:3000/inbox`
2. Press Enter

**Expected Result:**
- ✅ Page navigates to Inbox section
- ✅ Heading displays "Inbox"
- ✅ Subtitle text: "Recent interactions and messages"
- ✅ Page loads without errors
- ✅ URL bar shows `/inbox`

**Visual Cue:** "Inbox" heading is visible with gray subtitle text

---

### Step 9: Test Direct Dashboard Access
**Route:** `/inbox` → `/dashboard`

**Actions:**
1. Change the URL to: `http://localhost:3000/dashboard`
2. Press Enter

**Expected Result:**
- ✅ Returns to dashboard immediately
- ✅ All KPI cards still visible
- ✅ No authentication required (already logged in)
- ✅ Dashboard renders in under 1 second

**Visual Cue:** You see the three KPI cards (24, 12, 8) again

---

### Step 10: Test Root Path Redirect
**Route:** `/` → `/dashboard`

**Actions:**
1. Change the URL to: `http://localhost:3000/`
2. Press Enter

**Expected Result:**
- ✅ Automatically redirects to `/dashboard`
- ✅ URL changes from `/` to `/dashboard`
- ✅ Dashboard content displays normally

**Visual Cue:** URL bar updates to show `/dashboard` automatically

---

### Step 11: Test Visual Accessibility Page
**Route:** `/dashboard` → `/visual-check`

**Actions:**
1. Navigate to: `http://localhost:3000/visual-check`
2. Observe the page content

**Expected Result:**
- ✅ Page loads successfully
- ✅ Visual accessibility components are displayed
- ✅ Page demonstrates various UI components (buttons, cards, charts)
- ✅ Components follow consistent design system
- ✅ Dark theme is applied throughout

**Visual Cue:** Page shows multiple visual components for design validation

---

### Step 12: Browser Refresh Test
**Route:** `/visual-check`

**Actions:**
1. Press F5 or click the browser refresh button
2. Wait for page to reload

**Expected Result:**
- ✅ Page refreshes successfully
- ✅ No authentication errors occur
- ✅ You remain on `/visual-check` route
- ✅ Content reloads within 2 seconds
- ✅ Visual appearance remains consistent

**Visual Cue:** Page content reappears identically after refresh

---

## Test Completion Checklist

**Overall Application Quality:**
- [ ] All 12 test steps completed successfully
- [ ] No console errors observed (press F12 to check)
- [ ] Page load times are acceptable (< 3 seconds)
- [ ] Dark theme is consistent across all pages
- [ ] Text is readable and properly contrasted
- [ ] Buttons and interactive elements have hover effects
- [ ] Glass-morphism effects render correctly
- [ ] Gradient text renders smoothly
- [ ] No broken images or missing assets
- [ ] Application feels responsive and snappy

**Navigation:**
- [ ] URL changes reflect current page
- [ ] Direct URL access works for all routes
- [ ] Browser back/forward buttons work correctly
- [ ] Refresh maintains current route (except auth-protected)

**Authentication:**
- [ ] Login works with correct credentials
- [ ] Login fails with incorrect credentials
- [ ] Error messages are clear and helpful
- [ ] Session persists across page refreshes

---

## Issues Found

**Instructions:** Document any issues encountered during testing

| Step | Issue Description | Severity | Screenshot/Notes |
|------|------------------|----------|------------------|
| #    |                  | Low/Med/High |               |
| #    |                  | Low/Med/High |               |
| #    |                  | Low/Med/High |               |

---

## Sign-Off

**Tester Name:** ___________________________
**Date:** ___________________________
**Result:** ⬜ PASS  ⬜ PASS WITH ISSUES  ⬜ FAIL

**Additional Comments:**

___________________________________________________________________________

___________________________________________________________________________

___________________________________________________________________________
