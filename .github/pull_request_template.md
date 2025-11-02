# Pull Request

## Summary

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security fix
- [ ] 🏗️ Infrastructure/build changes
- [ ] 🧪 Test improvements

---

## Risk Assessment

<!-- Select ONE risk level and provide justification -->

### Risk Level

- [ ] 🟢 **LOW** - Minor changes, well-tested, easy rollback
- [ ] 🟡 **MEDIUM** - Moderate complexity, some risk to existing functionality
- [ ] 🟠 **HIGH** - Significant changes, potential for widespread impact
- [ ] 🔴 **CRITICAL** - Database migrations, security changes, or infrastructure updates

### Risk Justification

<!-- Explain why you selected this risk level -->

**Impact Scope:**
<!-- e.g., "Affects only admin UI", "Changes core authentication", "Touches all user-facing endpoints" -->

**Blast Radius:**
<!-- e.g., "10 users", "All users", "Internal systems only" -->

**Rollback Complexity:**
<!-- e.g., "Simple config revert", "Requires data migration rollback", "Cannot rollback without downtime" -->

---

## Test Evidence

<!-- Provide evidence that this change has been tested -->

### Unit Tests

- [ ] Unit tests added/updated
- [ ] All unit tests passing locally
- [ ] Code coverage maintained or improved

**Coverage Report:**
```
<!-- Paste relevant coverage output or link to CI report -->
Backend: ___%
Frontend: ___%
```

### Integration Tests

- [ ] Integration tests added/updated
- [ ] All integration tests passing

### Manual Testing

- [ ] Tested locally in development environment
- [ ] Tested in staging/preview environment
- [ ] Tested with realistic data volumes

**Test Scenarios Executed:**
<!-- List the scenarios you manually tested -->
1.
2.
3.

**Screenshots/Videos:**
<!-- Add screenshots or videos demonstrating the change -->

### Performance Testing

- [ ] Load testing performed (if applicable)
- [ ] Performance budgets met
- [ ] No performance regressions detected

**Performance Results:**
```
<!-- Paste performance test results if applicable -->
Endpoint: ___
p50: ___ ms (budget: ___ ms)
p95: ___ ms (budget: ___ ms)
```

### Security Testing

- [ ] Security implications reviewed
- [ ] DLP scan passed
- [ ] Dependency vulnerabilities checked
- [ ] No secrets in code

---

## Rollback Plan

<!-- Required for MEDIUM, HIGH, and CRITICAL risk changes -->

### Can this change be rolled back?

- [ ] ✅ Yes, simple rollback
- [ ] ⚠️ Yes, but requires additional steps (describe below)
- [ ] ❌ No, rollback not possible (requires forward fix)

### Rollback Procedure

<!-- Provide step-by-step instructions for rolling back this change -->

**Rollback Steps:**
1.
2.
3.

**Rollback Time Estimate:** <!-- e.g., "< 5 minutes", "15-30 minutes", "1-2 hours" -->

**Data Impact on Rollback:**
<!-- e.g., "No data loss", "Data created after deployment will be lost", "Requires data migration rollback" -->

### Forward Fix Plan (if rollback not possible)

<!-- If rollback is not possible, describe the forward fix strategy -->

---

## Deployment Plan

### Deployment Timing

- [ ] 🕐 Can be deployed anytime
- [ ] 📅 Should be deployed during maintenance window
- [ ] 🚨 Requires coordinated deployment with other services

**Preferred Deployment Time:**
<!-- e.g., "Off-peak hours (2-4 AM UTC)", "Next maintenance window", "ASAP" -->

### Deployment Dependencies

- [ ] No external dependencies
- [ ] Requires database migration
- [ ] Requires configuration changes
- [ ] Requires infrastructure changes
- [ ] Requires coordination with other teams

**Dependency Details:**
<!-- List any dependencies and coordination requirements -->

### Feature Flags

- [ ] Change is behind a feature flag
- [ ] Gradual rollout planned
- [ ] Not applicable

**Feature Flag Details:**
<!-- Name of feature flag, rollout percentage, etc. -->

---

## Change Control Checklist

<!-- Required for all PRs -->

### Code Quality

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Comments added for complex logic
- [ ] No debugging code or console.logs left in
- [ ] Error handling implemented appropriately

### Documentation

- [ ] README updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Architecture diagrams updated (if applicable)
- [ ] CHANGELOG entry prepared
- [ ] Runbook/operational docs updated (if applicable)

### Security & Compliance

- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] Authentication/authorization checked
- [ ] GDPR/privacy implications reviewed
- [ ] Audit logging added (if applicable)

### Dependencies

- [ ] No new dependencies added, OR
- [ ] New dependencies reviewed for security/license
- [ ] SBOM will be updated by CI
- [ ] License compliance verified

### Testing

- [ ] All CI checks passing
- [ ] Code coverage ≥85% backend / ≥80% frontend
- [ ] Performance budgets met
- [ ] No flaky tests introduced

### Database Changes

- [ ] No database changes, OR
- [ ] Migration scripts tested locally
- [ ] Migration is reversible
- [ ] Migration tested with production-like data volume
- [ ] Indexes added for new queries
- [ ] Backward compatible with current version (for zero-downtime)

---

## Post-Deployment Validation

<!-- How will you verify the deployment was successful? -->

### Success Metrics

**Functional Validation:**
<!-- e.g., "Login flow works", "New endpoint returns 200", "Background job processes successfully" -->
1.
2.
3.

**Monitoring Checks:**
<!-- e.g., "Error rate < 0.1%", "p95 latency < 500ms", "No spike in failed jobs" -->
- [ ] Error rate within acceptable range
- [ ] Latency metrics normal
- [ ] No increase in 5xx errors
- [ ] Dashboard shows expected behavior

**Alerts to Monitor:**
<!-- List specific alerts or metrics to watch after deployment -->
-
-

### Validation Timeline

**Immediate (0-15 min):**
<!-- What to check immediately after deployment -->

**Short-term (1-4 hours):**
<!-- What to monitor over the first few hours -->

**Long-term (24-48 hours):**
<!-- What to watch over the next 1-2 days -->

---

## Approvals Required

<!-- Auto-filled based on CODEOWNERS, but can be expanded -->

### Technical Approvals

- [ ] Code owner approval obtained
- [ ] Architecture review completed (for HIGH/CRITICAL changes)
- [ ] Security review completed (for security-sensitive changes)

### Business Approvals

- [ ] Product owner approval (for feature changes)
- [ ] Compliance review (for data/privacy changes)
- [ ] Not applicable

---

## Related Issues & PRs

<!-- Link to related issues, PRs, or discussions -->

**Closes:** #
**Related:** #
**Depends on:** #
**Blocks:** #

---

## Additional Notes

<!-- Any additional context, concerns, or notes for reviewers -->

---

## Pre-Merge Checklist

<!-- Final checklist before merging -->

- [ ] All required approvals obtained
- [ ] All CI checks passing
- [ ] Policy gates passing (tests, coverage, SBOM, licenses, performance)
- [ ] Branch is up to date with target branch
- [ ] Rollback plan documented and validated
- [ ] Deployment plan reviewed
- [ ] Post-deployment validation plan in place
- [ ] On-call engineer notified (for HIGH/CRITICAL changes)

---

**Risk Level Summary:** [LOW/MEDIUM/HIGH/CRITICAL]
**Rollback Available:** [YES/NO/CONDITIONAL]
**Deployment Window:** [ANYTIME/MAINTENANCE/COORDINATED]
