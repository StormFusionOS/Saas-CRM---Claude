# User Acceptance Testing (UAT) Documentation

This directory contains comprehensive UAT scripts for business users to test the RiverCityClean CRM and Operations Console applications **without requiring terminal access**.

## 📁 Contents

- **[CRM.md](./CRM.md)** - Complete UAT script for the CRM SPA (12 steps, ~15 minutes)
- **[Ops.md](./Ops.md)** - Complete UAT script for the Ops Console SPA (12 steps, ~15 minutes)

## 🚀 Quick Start

### Option 1: Print Collated Guide (Recommended)

Run the print script to generate a comprehensive UAT guide with QR codes:

```bash
./scripts/uat/print.sh
```

To save the output to a file:

```bash
./scripts/uat/print.sh --output uat-guide.txt
```

### Option 2: Direct Documentation Access

Open the documentation files directly:

1. **CRM Testing**: Open `docs/uat/CRM.md` in your browser or markdown viewer
2. **Ops Console Testing**: Open `docs/uat/Ops.md` in your browser or markdown viewer

## 🔗 Application URLs

- **CRM SPA**: http://localhost:3000
- **Ops Console**: http://localhost:3001

## 🔑 Test Credentials

**CRM:**
- Email: `Nathan@RiverCityClean.com`
- Password: `password123`

**Ops Console:**
- Email: `ops@RiverCityClean.com`
- Password: `opspassword123`

## 📋 Testing Process

1. **Environment Setup** (5 min)
   - Ensure both applications are running
   - Open browser dev tools (F12)
   - Clear cache and cookies

2. **CRM Testing** (~15 min)
   - Follow all 12 steps in CRM.md
   - Document issues in the provided table
   - Complete checklist and sign-off

3. **Ops Console Testing** (~15 min)
   - Follow all 12 steps in Ops.md
   - Document issues in the provided table
   - Complete checklist and sign-off

4. **Review and Sign-Off** (5 min)
   - Review documented issues
   - Determine pass/fail status
   - Complete final sign-off

**Total Time**: ~45 minutes

## ✅ Success Criteria

For UAT to pass:
- ✅ All routes load without errors
- ✅ Login authentication works correctly
- ✅ Navigation is smooth and functional
- ✅ Data displays accurately
- ✅ Visual design is consistent
- ✅ Performance is acceptable (< 3s page loads)

**Acceptance Thresholds**:
- **PASS**: 0 high-severity issues, ≤ 2 medium issues
- **PASS WITH ISSUES**: ≤ 1 high issue, ≤ 5 medium issues
- **FAIL**: > 1 high issue or > 5 medium issues

## 🆘 Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Take screenshots of visual problems
3. Document steps to reproduce
4. Contact technical support with:
   - Issue severity (High/Medium/Low)
   - Steps to reproduce
   - Screenshots
   - URL where issue occurred

## 📖 Additional Resources

- [Release Policy](../../POLICY.md) - Definition of Done for releases
- [Changelog](../../CHANGELOG.md) - Version history
- [A11y Checklist](../A11Y_CHECKLIST.md) - Accessibility guidelines

## 📝 Issue Severity Guide

**🔴 High**: Crashes, broken features, data loss, security issues
**🟡 Medium**: Limited functionality, visual glitches, performance issues
**🟢 Low**: Minor visual issues, typos, nice-to-have improvements

---

**Questions?** Contact your technical lead or refer to the documentation in `/docs`.
