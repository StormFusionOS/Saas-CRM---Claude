# Release Calendar

This document defines the release schedule, process, and policies for the RiverCityClean SaaS Platform.

## Release Schedule

### Regular Release Cadence

| Release Type | Frequency | Day/Time | Release Window | Code Freeze |
|--------------|-----------|----------|----------------|-------------|
| **Major Release** | Quarterly | 2nd Tuesday, 8:00 AM UTC | 4 hours | T-5 days |
| **Minor Release** | Bi-weekly | Tuesday, 8:00 AM UTC | 2 hours | T-2 days |
| **Patch Release** | As needed | Tuesday/Thursday, 8:00 AM UTC | 1 hour | T-1 day |
| **Hotfix Release** | Emergency | Anytime (on-call approval) | 30 min | None |

### 2025 Release Calendar

#### Q1 2025

| Release | Version | Type | Code Freeze | Release Date | Release Manager | Notes |
|---------|---------|------|-------------|--------------|-----------------|-------|
| 2025.1.0 | v1.0.0 | Major | 2025-01-06 | 2025-01-14 | @release-manager | Q1 Major Release |
| 2025.1.1 | v1.0.1 | Minor | 2025-01-26 | 2025-01-28 | @release-manager | |
| 2025.1.2 | v1.0.2 | Minor | 2025-02-09 | 2025-02-11 | @release-manager | |
| 2025.1.3 | v1.0.3 | Minor | 2025-02-23 | 2025-02-25 | @release-manager | |
| 2025.1.4 | v1.0.4 | Minor | 2025-03-09 | 2025-03-11 | @release-manager | |
| 2025.1.5 | v1.0.5 | Minor | 2025-03-23 | 2025-03-25 | @release-manager | |

#### Q2 2025

| Release | Version | Type | Code Freeze | Release Date | Release Manager | Notes |
|---------|---------|------|-------------|--------------|-----------------|-------|
| 2025.2.0 | v1.1.0 | Major | 2025-04-03 | 2025-04-08 | @release-manager | Q2 Major Release |
| 2025.2.1 | v1.1.1 | Minor | 2025-04-20 | 2025-04-22 | @release-manager | |
| 2025.2.2 | v1.1.2 | Minor | 2025-05-04 | 2025-05-06 | @release-manager | |
| 2025.2.3 | v1.1.3 | Minor | 2025-05-18 | 2025-05-20 | @release-manager | |
| 2025.2.4 | v1.1.4 | Minor | 2025-06-01 | 2025-06-03 | @release-manager | |
| 2025.2.5 | v1.1.5 | Minor | 2025-06-15 | 2025-06-17 | @release-manager | |

#### Q3 2025

| Release | Version | Type | Code Freeze | Release Date | Release Manager | Notes |
|---------|---------|------|-------------|--------------|-----------------|-------|
| 2025.3.0 | v1.2.0 | Major | 2025-07-03 | 2025-07-08 | @release-manager | Q3 Major Release |
| 2025.3.1 | v1.2.1 | Minor | 2025-07-20 | 2025-07-22 | @release-manager | |
| 2025.3.2 | v1.2.2 | Minor | 2025-08-03 | 2025-08-05 | @release-manager | |
| 2025.3.3 | v1.2.3 | Minor | 2025-08-17 | 2025-08-19 | @release-manager | |
| 2025.3.4 | v1.2.4 | Minor | 2025-08-31 | 2025-09-02 | @release-manager | |
| 2025.3.5 | v1.2.5 | Minor | 2025-09-14 | 2025-09-16 | @release-manager | |

#### Q4 2025

| Release | Version | Type | Code Freeze | Release Date | Release Manager | Notes |
|---------|---------|------|-------------|--------------|-----------------|-------|
| 2025.4.0 | v1.3.0 | Major | 2025-10-02 | 2025-10-07 | @release-manager | Q4 Major Release |
| 2025.4.1 | v1.3.1 | Minor | 2025-10-19 | 2025-10-21 | @release-manager | |
| 2025.4.2 | v1.3.2 | Minor | 2025-11-02 | 2025-11-04 | @release-manager | |
| 2025.4.3 | v1.3.3 | Minor | 2025-11-16 | 2025-11-18 | @release-manager | |
| 2025.4.4 | v1.3.4 | Minor | 2025-11-30 | 2025-12-02 | @release-manager | |
| 2025.4.5 | v1.3.5 | Minor | 2025-12-14 | 2025-12-16 | @release-manager | Final 2025 Release |

**Holiday Freeze:** December 17, 2025 - January 5, 2026 (No releases except emergency hotfixes)

---

## Release Process

### Phase 1: Planning (T-14 days for Major, T-7 for Minor)

- [ ] Release manager creates release tracking issue
- [ ] Product team finalizes feature list and priorities
- [ ] Engineering team reviews technical readiness
- [ ] QA team plans test scenarios
- [ ] Documentation team schedules doc updates
- [ ] Security team schedules security review

### Phase 2: Development (T-14 to Code Freeze)

- [ ] Features merged to `develop` branch
- [ ] All PRs follow change control process (see PR template)
- [ ] Policy gates enforced on all merges
- [ ] Continuous integration and testing
- [ ] Documentation updates in progress

### Phase 3: Code Freeze (T-5 days Major, T-2 Minor, T-1 Patch)

- [ ] Code freeze announced to team
- [ ] Release branch created: `release/vX.Y.Z`
- [ ] Only bug fixes allowed (approved by release manager)
- [ ] Feature freeze enforced
- [ ] Dependency updates frozen
- [ ] Infrastructure changes frozen

### Phase 4: Testing & Validation (Code Freeze to T-1)

- [ ] Full regression testing in staging environment
- [ ] Performance testing and budget verification
- [ ] Security scanning (SBOM, vulnerabilities, DLP)
- [ ] Load testing at expected production scale
- [ ] DR drill conducted (for major releases)
- [ ] Documentation review completed
- [ ] Release notes drafted

### Phase 5: Release Preparation (T-1 day)

- [ ] Final smoke tests in staging
- [ ] Release notes finalized and reviewed
- [ ] Rollback plan documented and validated
- [ ] Database migration scripts reviewed (if applicable)
- [ ] Monitoring dashboards prepared
- [ ] On-call team notified and briefed
- [ ] Customer communications prepared (for major releases)

### Phase 6: Release Deployment (Release Day)

**Time: 8:00 AM UTC (unless otherwise scheduled)**

- [ ] Pre-deployment checklist completed
- [ ] Tag release in Git: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Run release script: `python scripts/release/cut_release.py vX.Y.Z`
- [ ] Deploy to production (blue-green deployment)
- [ ] Run database migrations (if applicable)
- [ ] Smoke tests in production
- [ ] Monitor error rates, latency, and key metrics
- [ ] Gradual traffic rollout (0% → 25% → 50% → 100%)

**Release Window:**
- Major: 4 hours (8:00 AM - 12:00 PM UTC)
- Minor: 2 hours (8:00 AM - 10:00 AM UTC)
- Patch: 1 hour (8:00 AM - 9:00 AM UTC)

### Phase 7: Post-Release Validation (T+0 to T+24 hours)

- [ ] **T+15 min:** Immediate smoke tests and health checks
- [ ] **T+1 hour:** Error rate and latency within acceptable range
- [ ] **T+4 hours:** User-reported issues reviewed
- [ ] **T+24 hours:** Full metrics review and retrospective scheduled

### Phase 8: Retrospective (T+48 hours)

- [ ] Release retrospective meeting held
- [ ] Success metrics reviewed
- [ ] Issues and incidents documented
- [ ] Process improvements identified
- [ ] Lessons learned recorded

---

## Release Versioning

We follow **Semantic Versioning 2.0.0** (https://semver.org/):

```
MAJOR.MINOR.PATCH
```

- **MAJOR** (X.0.0): Incompatible API changes, breaking changes
- **MINOR** (x.Y.0): New features, backward-compatible
- **PATCH** (x.y.Z): Bug fixes, backward-compatible

### Version Increment Rules

| Change Type | Version Bump | Example | Frequency |
|-------------|-------------|---------|-----------|
| Breaking API change | MAJOR | 1.0.0 → 2.0.0 | Quarterly |
| New feature | MINOR | 1.2.0 → 1.3.0 | Bi-weekly |
| Bug fix | PATCH | 1.2.3 → 1.2.4 | As needed |
| Security fix | PATCH | 1.2.3 → 1.2.4 | Immediate |

---

## Release Criteria

### Merge to `main` Requirements (Policy Gates)

All merges to `main` must pass:

1. ✅ **All tests passing** - No failures or errors
2. ✅ **Code coverage ≥85% backend / ≥80% frontend**
3. ✅ **SBOM present** - Valid SBOM with all components
4. ✅ **License compliance** - No violations or unknown licenses
5. ✅ **Performance budgets met** - p95 latency within budget
6. ✅ **No critical/high vulnerabilities** - Security scan clean
7. ✅ **Required approvals** - Based on PR risk level

**Enforcement:** Policy gates enforced via `tools/policy/opa_stub.py`

### Release Readiness Checklist

Before cutting a release:

- [ ] All policy gates passing for release branch
- [ ] No open P0 or P1 bugs
- [ ] Release notes complete and accurate
- [ ] Database migrations tested and backward-compatible
- [ ] Performance testing completed (load tests, benchmarks)
- [ ] Security review completed (for major releases)
- [ ] Documentation updated and published
- [ ] Rollback plan documented and tested
- [ ] Customer-facing changes communicated

---

## Hotfix Process

### When to Use Hotfix

Hotfixes bypass the normal release schedule for **critical production issues**:

- Production outage or degradation (P0)
- Security vulnerability actively exploited (P0)
- Data loss or corruption (P0)
- Payment processing failure (P0)

### Hotfix Procedure

1. **Create hotfix branch** from `main`: `git checkout -b hotfix/vX.Y.Z main`
2. **Implement minimal fix** - Only changes necessary to resolve issue
3. **Test thoroughly** - Unit tests, integration tests, manual verification
4. **Fast-track review** - On-call approval (2 reviewers minimum)
5. **Policy gates** - All gates must still pass (no exemptions without CTO approval)
6. **Deploy immediately** - Follow expedited deployment process
7. **Monitor closely** - Watch for regressions or side effects
8. **Backport to develop** - Merge hotfix changes to `develop` branch
9. **Post-incident review** - Document root cause and prevention

**Approval Required:** On-call engineer + SRE lead (or CTO for production outage)

---

## Rollback Procedures

### Rollback Triggers

Rollback initiated if:

- Error rate > 5% for more than 5 minutes
- P95 latency > 2x budget for more than 10 minutes
- Critical functionality broken (login, payment, data access)
- Data corruption detected
- Security vulnerability introduced

### Rollback Process

1. **Declare rollback** - Release manager or on-call engineer
2. **Stop traffic to new version** - Route 100% to previous version
3. **Revert database migrations** (if applicable)
4. **Verify rollback success** - Smoke tests, error rates, latency
5. **Communicate status** - Internal team + customers (if needed)
6. **Root cause analysis** - Why did the release fail?
7. **Fix forward** - Plan next release with fixes

**RTO:** Rollback completed within 15 minutes of decision

---

## Release Approval Matrix

| Release Type | Approvals Required | Who Can Approve |
|--------------|-------------------|-----------------|
| **Major Release** | 3 approvals | CTO + 2 of (Platform Lead, SRE Lead, Security Lead) |
| **Minor Release** | 2 approvals | Release Manager + (Platform Lead or SRE Lead) |
| **Patch Release** | 2 approvals | Release Manager + Code Owner |
| **Hotfix Release** | 2 approvals | On-Call Engineer + (SRE Lead or CTO) |

---

## Communication Plan

### Internal Communications

| Audience | Timing | Channel | Content |
|----------|--------|---------|---------|
| Engineering Team | Code Freeze (T-5/2/1) | Slack #engineering | Code freeze announcement, release scope |
| Engineering Team | Release Day (T-0) | Slack #engineering | Deployment status updates |
| SRE/On-Call | T-1 day | Slack #oncall | Release briefing, rollback plan |
| All Staff | Post-Release (T+4 hours) | Email, Slack #general | Release notes, new features |

### External Communications

| Audience | Timing | Channel | Content |
|----------|--------|---------|---------|
| Customers | T-1 day (Major only) | Email, Status Page | Scheduled maintenance window |
| Customers | Release Day | Status Page | Deployment in progress |
| Customers | T+4 hours | Email, Blog, Changelog | Release notes, new features |
| Partners | T-1 day (API changes) | Email, API docs | API changes, migration guide |

---

## Metrics & Success Criteria

### Release Metrics

Track for each release:

- **Deployment Time:** Time from deploy start to 100% traffic
- **Rollback Count:** Number of releases rolled back
- **Bug Escape Rate:** Bugs found in production vs. staging
- **MTTR (Mean Time To Recover):** Average time to recover from incidents
- **Release Frequency:** Actual vs. scheduled release cadence
- **Policy Gate Pass Rate:** % of PRs passing policy gates on first attempt

### Success Criteria

- **Deployment Success:** 95% of releases deploy successfully without rollback
- **Deployment Time:** 90% of releases complete within scheduled window
- **Bug Escape Rate:** < 5 bugs per release escape to production
- **MTTR:** < 2 hours for P1 incidents, < 15 minutes for rollback
- **Policy Compliance:** 100% of merges pass policy gates

---

## Tools & Automation

| Tool | Purpose | Location |
|------|---------|----------|
| **Release Script** | Version bumping, changelog generation | `scripts/release/cut_release.py` |
| **Policy Gate** | Enforce merge requirements | `tools/policy/opa_stub.py` |
| **Performance Testing** | Budget verification | `scripts/perf/check_budgets.py` |
| **Security Scanning** | SBOM, DLP, vulnerability scan | `tools/sbom/`, `tools/dlp/` |
| **DR Validation** | Backup/restore verification | `scripts/dr/drill.py` |

---

## Changelog Template

See `scripts/release/cut_release.py` for automatic changelog generation.

**Manual Changelog Format:**

```markdown
# [vX.Y.Z] - YYYY-MM-DD

## Added
- New feature descriptions

## Changed
- Changes to existing functionality

## Fixed
- Bug fixes

## Security
- Security fixes and improvements

## Deprecated
- Features being phased out

## Removed
- Features removed in this release
```

---

## Emergency Contacts

| Role | Primary | Backup | Contact |
|------|---------|--------|---------|
| **Release Manager** | @release-manager | @platform-lead | Slack #oncall |
| **CTO** | @cto | @platform-lead | Slack #incidents |
| **SRE Lead** | @sre-lead | @sre-oncall | PagerDuty |
| **Security Lead** | @security-lead | @security-team | Slack #security |

**Escalation Path:** Release Manager → SRE Lead → CTO

---

**Document Owner:** Release Manager
**Last Updated:** 2025-11-02
**Next Review:** 2026-02-01 (Quarterly)
