# Pull Request

## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration change
- [ ] ♻️ Refactoring (no functional changes)
- [ ] 🎨 UI/UX improvement
- [ ] 🔒 Security fix
- [ ] ⚡ Performance improvement

## Risk Assessment

### Risk Level
- [ ] 🟢 **Low Risk** - Minor change, well-tested, no production impact
- [ ] 🟡 **Medium Risk** - Moderate change, some production impact, mitigations in place
- [ ] 🔴 **High Risk** - Major change, significant production impact, requires careful review

### Risk Details

**What could go wrong?**
<!-- Describe potential failure modes, edge cases, or unintended consequences -->

**Blast Radius:**
<!-- What systems, users, or data could be affected if this fails? -->
- [ ] Limited to single feature/component
- [ ] Affects multiple features
- [ ] Affects entire service
- [ ] Affects multiple services
- [ ] Affects all users

**Mitigations:**
<!-- What steps have been taken to reduce risk? -->
- [ ] Feature flag implemented
- [ ] Gradual rollout plan
- [ ] Monitoring/alerting configured
- [ ] Load tested
- [ ] Rollback tested

## Test Evidence

### Automated Tests
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved

**Test Results:**
\`\`\`
<!-- Paste test output or link to CI run -->
\`\`\`

### Manual Testing
- [ ] Tested locally
- [ ] Tested in staging/dev environment
- [ ] Tested edge cases
- [ ] Tested error scenarios
- [ ] Cross-browser tested (if UI change)
- [ ] Mobile tested (if UI change)

**Manual Test Checklist:**
<!-- List specific scenarios tested -->
- [ ]
- [ ]
- [ ]

## Rollback Plan

### Can this change be rolled back?
- [ ] ✅ Yes, easily rolled back (revert commit)
- [ ] ⚠️ Yes, but requires additional steps (describe below)
- [ ] ❌ No, requires forward fix (describe why)

### Rollback Steps

**If this PR causes production issues, follow these steps to rollback:**

1. <!-- Step 1 -->
2. <!-- Step 2 -->
3. <!-- Step 3 -->

**Rollback Testing:**
- [ ] Rollback procedure tested locally
- [ ] Rollback procedure documented

**Data Migration Rollback:**
<!-- If this PR includes database migrations -->
- [ ] No database migrations
- [ ] Migrations are reversible (down migration exists)
- [ ] Data backup taken before deployment
- [ ] Rollback migration tested

## Pre-Merge Checklist

### Code Quality
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] No debugging code or console.logs left in
- [ ] No hardcoded credentials or secrets

### Documentation
- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] CHANGELOG.md updated
- [ ] Inline code documentation added

### Deployment
- [ ] Deployment plan documented
- [ ] Rollback plan tested
- [ ] Monitoring configured

---

## Reviewer Checklist

- [ ] Risk assessment is accurate
- [ ] Test evidence is sufficient
- [ ] Rollback plan is clear
- [ ] Code quality meets standards
- [ ] All checks passing
