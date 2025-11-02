#!/usr/bin/env bash
set -euo pipefail

#==============================================================================
# UAT Documentation Print Script
#==============================================================================
# Collates UAT documentation and generates QR codes for local web URLs
# Usage: ./scripts/uat/print.sh [--output <file>]
#==============================================================================

# Color codes
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'
BOLD='\033[1m'

# Configuration
CRM_URL="http://localhost:3000"
OPS_URL="http://localhost:3001"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UAT_DOCS_DIR="$PROJECT_ROOT/docs/uat"
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --output|-o)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--output <file>]"
      exit 1
      ;;
  esac
done

# If output file specified, redirect stdout
if [[ -n "$OUTPUT_FILE" ]]; then
  exec > "$OUTPUT_FILE"
fi

#==============================================================================
# Helper Functions
#==============================================================================

print_header() {
  echo -e "${CYAN}================================================================================${RESET}"
  echo -e "${CYAN}$1${RESET}"
  echo -e "${CYAN}================================================================================${RESET}"
  echo ""
}

print_section() {
  echo ""
  echo -e "${BLUE}--------------------------------------------------------------------------------${RESET}"
  echo -e "${BOLD}$1${RESET}"
  echo -e "${BLUE}--------------------------------------------------------------------------------${RESET}"
  echo ""
}

generate_qr_code() {
  local url="$1"
  local label="$2"

  echo -e "${YELLOW}${label}${RESET}"
  echo -e "${GREEN}URL: ${url}${RESET}"
  echo ""

  # Check if qrencode is available
  if command -v qrencode &> /dev/null; then
    # Generate QR code as UTF-8 terminal output
    qrencode -t UTF8 "$url"
    echo ""
  else
    # Fallback: ASCII QR code placeholder
    echo "╔════════════════════════════════════╗"
    echo "║                                    ║"
    echo "║      [QR CODE PLACEHOLDER]         ║"
    echo "║                                    ║"
    echo "║   Install 'qrencode' to generate  ║"
    echo "║   actual QR codes:                 ║"
    echo "║   apt-get install qrencode         ║"
    echo "║   brew install qrencode            ║"
    echo "║                                    ║"
    echo "╚════════════════════════════════════╝"
    echo ""
    echo "Manual URL: ${url}"
    echo ""
  fi
}

#==============================================================================
# Main Output
#==============================================================================

print_header "USER ACCEPTANCE TESTING (UAT) GUIDE"

echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Version: 0.1.0"
echo ""
echo "This document collates all UAT scripts and provides quick access"
echo "to the test applications via QR codes."
echo ""

#==============================================================================
# Quick Access URLs
#==============================================================================

print_section "📱 Quick Access URLs"

echo "Scan these QR codes with your mobile device or use the URLs directly:"
echo ""

generate_qr_code "$CRM_URL" "🔹 CRM Application"
generate_qr_code "$OPS_URL" "🔹 Ops Console Application"

#==============================================================================
# Test Credentials
#==============================================================================

print_section "🔑 Test Credentials"

cat <<EOF
CRM SPA:
  Email:    Nathan@RiverCityClean.com
  Password: password123
  URL:      ${CRM_URL}

Ops Console:
  Email:    ops@RiverCityClean.com
  Password: opspassword123
  URL:      ${OPS_URL}

EOF

#==============================================================================
# Pre-Test Checklist
#==============================================================================

print_section "✅ Pre-Test Checklist"

cat <<EOF
Before beginning UAT, ensure the following:

Infrastructure:
  ☐ Development servers are running
  ☐ CRM SPA accessible at ${CRM_URL}
  ☐ Ops Console accessible at ${OPS_URL}
  ☐ Backend APIs are operational
  ☐ Database connections are healthy

Testing Environment:
  ☐ Modern web browser installed (Chrome, Firefox, Safari, Edge)
  ☐ Browser console accessible (F12) for error checking
  ☐ Screen resolution: 1280x720 minimum
  ☐ Stable internet connection (if APIs require external access)
  ☐ Pop-up blockers disabled for test domains

Documentation:
  ☐ CRM UAT script available: docs/uat/CRM.md
  ☐ Ops UAT script available: docs/uat/Ops.md
  ☐ Pen and paper (or digital form) for issue tracking

Team:
  ☐ Business stakeholder identified
  ☐ Technical support available during test
  ☐ Test duration: Allow 30-45 minutes total
  ☐ Clear communication channel established

EOF

#==============================================================================
# CRM UAT Summary
#==============================================================================

print_section "📊 CRM SPA - Test Overview"

if [[ -f "$UAT_DOCS_DIR/CRM.md" ]]; then
  echo "Test Steps: 12"
  echo "Duration: ~15 minutes"
  echo "Focus Areas:"
  echo "  • Login authentication"
  echo "  • Dashboard KPI display"
  echo "  • Navigation between routes"
  echo "  • Data visualization"
  echo ""
  echo "Key Routes to Test:"
  echo "  /login       - Authentication"
  echo "  /dashboard   - KPIs and metrics"
  echo "  /leads       - Leads pipeline"
  echo "  /inbox       - Interactions"
  echo "  /visual-check - Accessibility validation"
  echo ""
  echo "Full documentation: docs/uat/CRM.md"
else
  echo -e "${YELLOW}⚠ Warning: CRM UAT documentation not found at $UAT_DOCS_DIR/CRM.md${RESET}"
fi

echo ""

#==============================================================================
# Ops Console UAT Summary
#==============================================================================

print_section "🖥️  Ops Console - Test Overview"

if [[ -f "$UAT_DOCS_DIR/Ops.md" ]]; then
  echo "Test Steps: 12"
  echo "Duration: ~15 minutes"
  echo "Focus Areas:"
  echo "  • Operations dashboard metrics"
  echo "  • System health monitoring"
  echo "  • Service status indicators"
  echo "  • Real-time data display"
  echo ""
  echo "Key Routes to Test:"
  echo "  /login       - Ops authentication"
  echo "  /dashboard   - Operations overview"
  echo "  /health      - System health cards"
  echo "  /visual-check - Component validation"
  echo ""
  echo "Full documentation: docs/uat/Ops.md"
else
  echo -e "${YELLOW}⚠ Warning: Ops Console UAT documentation not found at $UAT_DOCS_DIR/Ops.md${RESET}"
fi

echo ""

#==============================================================================
# Test Execution Steps
#==============================================================================

print_section "🚀 Test Execution Steps"

cat <<EOF
Recommended Testing Sequence:

1. Environment Verification (5 minutes)
   → Verify both applications are accessible
   → Open browser dev tools (F12)
   → Clear browser cache and cookies
   → Check console for any immediate errors

2. CRM SPA Testing (~15 minutes)
   → Open docs/uat/CRM.md
   → Follow all 12 test steps sequentially
   → Document issues in the Issues Found table
   → Complete the test completion checklist
   → Sign off on results

3. Ops Console Testing (~15 minutes)
   → Open docs/uat/Ops.md
   → Follow all 12 test steps sequentially
   → Document issues in the Issues Found table
   → Complete the test completion checklist
   → Sign off on results

4. Cross-Application Testing (5 minutes)
   → Test switching between CRM and Ops Console
   → Verify separate authentication contexts
   → Check for session isolation
   → Validate no cross-contamination of data

5. Issue Review and Sign-Off (5 minutes)
   → Review all documented issues
   → Categorize by severity (Low/Medium/High)
   → Determine pass/fail status
   → Complete final sign-off

Total Estimated Time: 45 minutes

EOF

#==============================================================================
# Success Criteria
#==============================================================================

print_section "🎯 Success Criteria"

cat <<EOF
For UAT to be considered successful, the following must be true:

Functional Requirements:
  ✓ Login works with correct credentials
  ✓ Login fails gracefully with wrong credentials
  ✓ All routes load without errors
  ✓ Navigation between pages works smoothly
  ✓ Data displays correctly on all pages
  ✓ Browser refresh maintains state (where appropriate)

Visual Requirements:
  ✓ Dark theme applied consistently
  ✓ Text is readable (sufficient contrast)
  ✓ KPIs/metrics display with correct values
  ✓ Charts and visualizations render properly
  ✓ Hover effects work on interactive elements
  ✓ Responsive layout on desktop screen sizes

Performance Requirements:
  ✓ Page load times < 3 seconds
  ✓ Navigation feels instant
  ✓ No visible lag or jank
  ✓ Console shows no critical errors

Acceptance Threshold:
  • PASS: 0 high-severity issues, ≤ 2 medium-severity issues
  • PASS WITH ISSUES: ≤ 1 high-severity issue, ≤ 5 medium-severity issues
  • FAIL: > 1 high-severity issue or > 5 medium-severity issues

EOF

#==============================================================================
# Issue Severity Definitions
#==============================================================================

print_section "📋 Issue Severity Definitions"

cat <<EOF
When documenting issues, use these severity levels:

🔴 HIGH SEVERITY:
  • Application crashes or freezes
  • Critical functionality broken (cannot login, cannot navigate)
  • Data loss or corruption
  • Security vulnerabilities visible
  • Complete feature failure

🟡 MEDIUM SEVERITY:
  • Feature works but with limitations
  • Visual glitches that impact usability
  • Incorrect data display
  • Performance issues (slow load times)
  • Inconsistent behavior across pages

🟢 LOW SEVERITY:
  • Minor visual inconsistencies
  • Typos or text formatting issues
  • Non-critical features missing
  • Nice-to-have improvements
  • Documentation gaps

EOF

#==============================================================================
# Support and Resources
#==============================================================================

print_section "🆘 Support and Resources"

cat <<EOF
If you encounter issues during testing:

Technical Support:
  • Check browser console (F12) for error messages
  • Take screenshots of visual issues
  • Note the exact URL where issue occurred
  • Document steps to reproduce

Documentation:
  • CRM UAT Script:    ${UAT_DOCS_DIR}/CRM.md
  • Ops UAT Script:    ${UAT_DOCS_DIR}/Ops.md
  • Release Policy:    ${PROJECT_ROOT}/POLICY.md
  • Changelog:         ${PROJECT_ROOT}/CHANGELOG.md

Development Team:
  • Provide issue summary via your standard communication channel
  • Include severity level, steps to reproduce, and screenshots
  • For blockers, escalate immediately

EOF

#==============================================================================
# Footer
#==============================================================================

print_header "END OF UAT GUIDE"

echo "Next Steps:"
echo "  1. Open docs/uat/CRM.md to begin CRM testing"
echo "  2. Open docs/uat/Ops.md to begin Ops Console testing"
echo "  3. Use the URLs or QR codes above to access applications"
echo ""
echo "Good luck with testing! 🚀"
echo ""

# If output file was specified, notify user
if [[ -n "$OUTPUT_FILE" ]]; then
  echo "Output saved to: $OUTPUT_FILE" >&2
fi
