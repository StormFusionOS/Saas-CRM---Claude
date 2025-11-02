# Release Policy

**Definition of Done for Releases**

This document defines the requirements and quality gates that must be met before a release can be cut and deployed to production.

---

## Table of Contents

- [Release Process Overview](#release-process-overview)
- [Definition of Done](#definition-of-done)
- [Quality Gates](#quality-gates)
- [Artifact Requirements](#artifact-requirements)
- [Approval Process](#approval-process)
- [Rollback Requirements](#rollback-requirements)
- [Post-Release Requirements](#post-release-requirements)

---

## Release Process Overview

**Release Stages:**

1. **Development** - Feature branches merged to main via PR
2. **Pre-Release Gates** - Automated checks via `scripts/release/cut.sh`
3. **Artifact Generation** - Build and archive release artifacts
4. **Tagging** - Create git tag for release version
5. **Deployment** - Follow deployment runbook
6. **Post-Release Monitoring** - Monitor metrics for 24-48 hours

**Release Cadence:**
- **Patch releases:** As needed for critical bugs/security fixes
- **Minor releases:** Every 2-4 weeks for features
- **Major releases:** Quarterly or as needed for breaking changes

---

## Definition of Done

A release is considered "Done" and ready for production when **ALL** of the following criteria are met:

### ✅ Code Quality

- [ ] All code merged via reviewed Pull Requests
- [ ] PR template completed with risk assessment and test evidence
- [ ] No open P0 or P1 bugs
- [ ] Code review completed by at least one maintainer
- [ ] All automated tests passing
- [ ] Test coverage ≥80% (or maintained from previous release)
- [ ] No linting errors or warnings
- [ ] No security vulnerabilities (Snyk, npm audit)

### ✅ Configuration

- [ ] All configuration keys documented in .env.example
- [ ] Config validation passing (`scripts/config/check.sh`)
- [ ] No hardcoded secrets or credentials
- [ ] Environment-specific configs separated
- [ ] Configuration migration guide provided (if changes)

### ✅ Testing

- [ ] **Unit Tests:** All passing
- [ ] **Integration Tests:** All passing (smoke tests)
- [ ] **Security Tests:** All passing (24/24 sanity checks)
- [ ] **Performance Tests:** All endpoints within budget (p95 < thresholds)
- [ ] **Accessibility Tests:** All a11y tests passing
- [ ] **Manual Testing:** Key user flows tested in staging
- [ ] **Regression Testing:** No regressions introduced

### ✅ Security

- [ ] Security sanity checks passing (tokens, RBAC, webhooks, headers)
- [ ] No high or critical CVEs in dependencies
- [ ] Secrets rotated (if applicable)
- [ ] OWASP Top 10 considerations reviewed
- [ ] Rate limiting tested
- [ ] CORS configured correctly
- [ ] Input validation in place

### ✅ Performance

- [ ] Performance smoke tests passing
- [ ] p95 latencies within budget:
  - `/auth/login`: < 120ms
  - `/v1/leads`: < 200ms
  - `/scheduler/next`: < 100ms
- [ ] No memory leaks detected
- [ ] Database query performance acceptable
- [ ] Frontend bundle sizes within limits

### ✅ Documentation

- [ ] CHANGELOG.md updated with release notes
- [ ] README.md updated (if applicable)
- [ ] API documentation updated (if API changes)
- [ ] Migration guide provided (if breaking changes)
- [ ] RUNBOOK.md deployment steps verified
- [ ] Rollback procedures documented

### ✅ Infrastructure

- [ ] Database migrations tested (up and down)
- [ ] Infrastructure as Code (IaC) updated
- [ ] Monitoring and alerting configured
- [ ] Log aggregation working
- [ ] Health check endpoints responding
- [ ] Auto-scaling configured (if applicable)

### ✅ Observability

- [ ] Metrics instrumented for key operations
- [ ] Error tracking configured (Sentry, Rollbar, etc.)
- [ ] Logging added for debug/audit trails
- [ ] Dashboards created for key metrics
- [ ] Alerts configured for critical failures

### ✅ Compliance

- [ ] GDPR compliance reviewed (if handling EU data)
- [ ] Data retention policies enforced
- [ ] Audit logs enabled for sensitive operations
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] License compliance verified

---

## Quality Gates

The following automated gates **MUST** pass before a release can be cut:

### Gate 1: Configuration Validation

**Command:** `./scripts/config/check.sh .env.example`

**Checks:**
- All required config keys present
- No duplicate keys
- Secrets not exposed in examples
- Valid formats (URLs, emails, numbers)

**Exit Criteria:** ✅ All checks passing

---

### Gate 2: Smoke Tests

**Command:** `cd crm && npm test` and `cd ops-console && npm test`

**Checks:**
- Unit tests for components
- Integration tests for API routes
- Accessibility tests (focus, tab order, labels)

**Exit Criteria:** ✅ All test suites passing, 0 failures

---

### Gate 3: Security Sanity Checks

**Command:** `./scripts/security/sanity.sh`

**Checks:**
- Access token validation (valid/expired/wrong audience)
- Cross-realm isolation (CRM ↔ Ops)
- Webhook signature validation
- Nginx security headers (HSTS, CSP, X-Frame-Options, etc.)

**Exit Criteria:** ✅ 24/24 tests passing, 0 errors

---

### Gate 4: Performance Smoke Tests

**Command:** `python3 tools/perf/smoke_stub.py`

**Checks:**
- p50/p95 latencies for 3 endpoints
- 100 requests per endpoint
- Error rate = 0%
- All endpoints within performance budgets

**Exit Criteria:** ✅ All endpoints within budget, zero errors

---

### Gate 5: Build SPAs

**Commands:**
- `cd crm && npm run build`
- `cd ops-console && npm run build`

**Checks:**
- TypeScript compilation successful
- Vite build successful
- No warnings or errors
- Assets generated in `dist/`

**Exit Criteria:** ✅ Both SPAs build successfully

---

### Gate 6: Artifact Generation

**Automated by:** `scripts/release/cut.sh`

**Generates:**
- SPA build archives (`.zip` files)
- Build logs
- Test coverage reports
- Release manifest
- CHANGELOG.md entry

**Exit Criteria:** ✅ All artifacts generated and archived

---

## Artifact Requirements

Each release **MUST** generate the following artifacts in `artifacts/release/vX.Y.Z/`:

### Required Artifacts

1. **CRM SPA Build**
   - `crm-spa-vX.Y.Z.zip` - Deployable build artifacts

2. **Ops Console SPA Build**
   - `ops-console-spa-vX.Y.Z.zip` - Deployable build artifacts

3. **Build Logs**
   - `crm-build.log` - CRM build output
   - `ops-build.log` - Ops Console build output

4. **Test Reports**
   - `crm-coverage-vX.Y.Z.zip` - Code coverage report (if available)
   - `ops-console-coverage-vX.Y.Z.zip` - Code coverage report (if available)

5. **Release Manifest**
   - `MANIFEST.txt` - Release metadata, git commit, file list, gate results

6. **CHANGELOG Entry**
   - Added to `CHANGELOG.md` at project root

### Artifact Retention

- **Latest 3 releases:** Keep all artifacts
- **Older releases:** Keep MANIFEST.txt and CHANGELOG.md only
- **Purge after:** 90 days (except major versions)

---

## Approval Process

### Who Can Approve Releases?

- **Patch releases (X.Y.Z):** Any 1 maintainer
- **Minor releases (X.Y.0):** Any 2 maintainers
- **Major releases (X.0.0):** All maintainers + product owner

### Approval Checklist

- [ ] All quality gates passed
- [ ] Release notes reviewed
- [ ] Rollback plan documented and tested
- [ ] Deployment runbook followed
- [ ] Stakeholders notified (if user-facing changes)

---

## Rollback Requirements

Every release **MUST** have a documented and tested rollback plan:

### Rollback Readiness

- [ ] Previous version available in artifact repository
- [ ] Database migrations are reversible
- [ ] Rollback procedure documented in RUNBOOK.md
- [ ] Rollback tested in staging environment
- [ ] Rollback can be executed in < 15 minutes
- [ ] Data backup taken before deployment

### Rollback Triggers

Rollback should be initiated if:
- Error rate > 5% for > 5 minutes
- p99 latency > 2x baseline for > 10 minutes
- Critical security vulnerability discovered
- Data corruption detected
- Critical feature completely broken

### Rollback Process

1. **Decision:** On-call engineer or release manager decides
2. **Communication:** Notify team via Slack/PagerDuty
3. **Execute:** Follow rollback procedure in RUNBOOK.md
4. **Verify:** Run smoke tests post-rollback
5. **Monitor:** Watch error rates and metrics for 30 minutes
6. **Post-Mortem:** Schedule incident review within 24 hours

---

## Post-Release Requirements

After deployment, the following steps **MUST** be completed:

### Immediate (0-1 hour)

- [ ] Smoke tests run in production
- [ ] Health checks passing
- [ ] Error rates normal (< 1%)
- [ ] Key user flows manually tested
- [ ] Monitoring dashboards reviewed

### Short-term (1-24 hours)

- [ ] No increase in error rates
- [ ] Performance metrics stable
- [ ] User feedback monitored
- [ ] Support tickets reviewed
- [ ] No rollback triggered

### Long-term (24-48 hours)

- [ ] Business metrics reviewed
- [ ] User analytics reviewed
- [ ] Performance trends analyzed
- [ ] Release retrospective scheduled

---

## Exceptions and Overrides

### Hotfix Releases

Critical security fixes or P0 bugs may bypass some gates with approval:

- **Allowed to skip:** Performance tests, full test coverage
- **NOT allowed to skip:** Security checks, config validation, build
- **Required approval:** 2 maintainers + incident commander

### Emergency Rollback

In case of critical production incident:

- Any on-call engineer can initiate rollback
- Full post-mortem required within 24 hours
- Process review required before next release

---

## Compliance Checklist

Before releasing to production, verify compliance with:

### Legal & Regulatory

- [ ] GDPR compliance (if handling EU data)
- [ ] CCPA compliance (if handling CA data)
- [ ] SOC 2 requirements met
- [ ] Data retention policies enforced

### Security & Privacy

- [ ] Secrets rotation completed (if needed)
- [ ] Access logs enabled
- [ ] Audit trail captured
- [ ] Encryption at rest and in transit

### Accessibility

- [ ] WCAG 2.1 Level AA standards met
- [ ] Keyboard navigation functional
- [ ] Screen reader compatible
- [ ] Color contrast ratios ≥ 4.5:1

---

## Release Metrics

Track the following metrics for each release:

- **Time to release:** From merge to production
- **Gate pass rate:** % of releases passing all gates first try
- **Rollback rate:** % of releases requiring rollback
- **Defect escape rate:** # of bugs found in production
- **MTTR (Mean Time To Recover):** Average rollback time

**Target SLIs:**
- Gate pass rate: ≥ 90%
- Rollback rate: < 5%
- MTTR: < 15 minutes

---

## Review and Updates

This policy should be reviewed and updated:

- **Quarterly:** Regular review by engineering team
- **After incidents:** Update based on lessons learned
- **Process changes:** Update when tooling or process changes

---

## Summary

**A release is production-ready when:**

1. ✅ All 6 quality gates pass
2. ✅ All artifacts generated and archived
3. ✅ CHANGELOG.md updated with release notes
4. ✅ Rollback plan documented and tested
5. ✅ Approval obtained from required stakeholders

**Use this checklist before every release to ensure quality and reliability.**

---

**Last Updated:** 2025-11-02
**Version:** 1.0
**Maintained By:** Release Engineering Team
