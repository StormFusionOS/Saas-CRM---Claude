# Pre-Push Quality Gate System

## Overview

The pre-push quality gate system ensures all code meets quality standards before being pushed to the remote repository. It runs comprehensive validation checks across configuration, types, tests, security, performance, and builds.

## Quick Start

### Run All Gates

```bash
./scripts/prepush.sh
```

### Skip Tests (Faster Development Iteration)

```bash
./scripts/prepush.sh --skip-tests
```

### Skip Builds (Quick Validation)

```bash
./scripts/prepush.sh --skip-tests --skip-build
```

### Quiet Mode (Matrix Only)

```bash
./scripts/prepush.sh --quiet
```

## Quality Gates

The prepush script runs **10 quality gates** in sequence:

| # | Gate | Description | Exit on Fail |
|---|------|-------------|--------------|
| 1 | **Configuration Validation** | Validates `.env.example` configuration | Yes |
| 2 | **Secrets Scan** | Scans for hardcoded secrets (included in config check) | Skipped |
| 3 | **TypeScript (CRM)** | Type checks CRM SPA | Yes |
| 4 | **TypeScript (Ops)** | Type checks Ops Console SPA | Yes |
| 5 | **Unit Tests (CRM)** | Runs CRM SPA unit tests | Yes |
| 6 | **Unit Tests (Ops)** | Runs Ops Console SPA unit tests | Yes |
| 7 | **Security Sanity Checks** | Runs 24 security tests | Yes |
| 8 | **Performance Smoke Tests** | Validates endpoint performance budgets | Yes |
| 9 | **Build CRM SPA** | Compiles and bundles CRM SPA | Yes |
| 10 | **Build Ops Console SPA** | Compiles and bundles Ops Console SPA | Yes |

## Output

### Success (All Gates Pass)

```
═══════════════════════════════════════════════════════════════════════════════
                          PRE-PUSH QUALITY GATE MATRIX
═══════════════════════════════════════════════════════════════════════════════

Gate                                     Status       Duration
-------------------------------------------------------------------------------
Configuration Validation                 ✓ PASS       2s
Secrets Scan                             ⊘ SKIP       --
TypeScript (CRM)                         ✓ PASS       3s
TypeScript (Ops)                         ✓ PASS       3s
Unit Tests (CRM)                         ✓ PASS       5s
Unit Tests (Ops)                         ✓ PASS       4s
Security Sanity Checks                   ✓ PASS       1s
Performance Smoke Tests                  ✓ PASS       1s
Build CRM SPA                            ✓ PASS       4s
Build Ops Console SPA                    ✓ PASS       4s
-------------------------------------------------------------------------------
Summary:                                 8 passed, 0 failed, 2 skipped
Total Duration:                          27s

═══════════════════════════════════════════════════════════════════════════════
                         ✓ ALL QUALITY GATES PASSED
═══════════════════════════════════════════════════════════════════════════════

Your code is ready to push!

Recommended Git Commands:

# Push to remote:
  git push -u origin your-branch-name

All quality gates passed. Your code meets the Definition of Done.
```

### Failure (Gate Fails)

```
═══════════════════════════════════════════════════════════════════════════════
                         ✗ QUALITY GATES FAILED
═══════════════════════════════════════════════════════════════════════════════

2 gate(s) failed. Please fix the issues before pushing.

Next Steps:
  1. Review the failed gate output above
  2. Fix the identified issues
  3. Run ./scripts/prepush.sh again
  4. Once all gates pass, push your code
```

## Options

### `--no-fail-fast`

Continue running all gates even if one fails. Useful for seeing all failures at once.

```bash
./scripts/prepush.sh --no-fail-fast
```

### `--skip-tests`

Skip unit test execution. Tests take 5-10 seconds combined.

```bash
./scripts/prepush.sh --skip-tests
```

**When to use:**
- Rapid development iterations
- After running tests successfully once
- When debugging non-test-related issues

**When NOT to use:**
- Before creating a pull request
- Before final push to shared branches
- After changing application logic

### `--skip-build`

Skip build validation. Builds take 8-10 seconds combined.

```bash
./scripts/prepush.sh --skip-build
```

**When to use:**
- Early development stages
- After successful build verification
- When only documentation changed

**When NOT to use:**
- Before pushing to production branches
- After changing TypeScript/React code
- Before creating pull requests

### `--quiet` / `-q`

Minimal output, only show final matrix.

```bash
./scripts/prepush.sh --quiet
```

## Integration with Git Hooks

### Manual Installation

The pre-push hook template is available in `hooks/pre-push`. Install it manually:

```bash
# Copy hook to .git/hooks/
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

### Automatic Execution

Once installed, the hook runs automatically before every `git push`:

```bash
git push origin feature-branch
# → Pre-push hook runs automatically
# → Push blocked if gates fail
# → Push allowed if gates pass
```

### Bypass Hook (Emergency Only)

```bash
git push --no-verify
```

**⚠️ Warning:** Only bypass hooks for:
- Emergency hotfixes (with team approval)
- CI/CD automated pushes
- When hook is broken and needs fixing

See [docs/GIT_HOOKS.md](../docs/GIT_HOOKS.md) for full documentation.

## Gate Details

### Gate 1: Configuration Validation

**Command:** `scripts/config/check.sh .env.example`

**Validates:**
- Environment variable presence
- Placeholder detection
- Secret patterns

**Typical Duration:** 1-2 seconds

---

### Gate 3-4: TypeScript Type Checking

**Command:** `npx tsc --noEmit`

**Validates:**
- TypeScript syntax
- Type correctness
- Import/export resolution

**Typical Duration:** 3-4 seconds per SPA

**Common Failures:**
- Type mismatches
- Missing imports
- Incompatible library versions

---

### Gate 5-6: Unit Tests

**Command:** `npm test -- --run`

**Validates:**
- Component rendering
- Business logic
- Utility functions

**Typical Duration:** 4-6 seconds per SPA

**Common Failures:**
- Test assertions failing
- Mock data issues
- Component rendering errors

---

### Gate 7: Security Sanity Checks

**Command:** `scripts/security/sanity.sh`

**Validates:**
- Token validation (5 tests)
- Cross-realm access control (4 tests)
- Webhook signature validation (7 tests)
- Nginx security configuration (8 tests)

**Total:** 24 tests

**Typical Duration:** 1-2 seconds

---

### Gate 8: Performance Smoke Tests

**Command:** `python3 tools/perf/smoke_stub.py`

**Validates:**
- Endpoint latency budgets
- Error rate (must be 0%)
- Retry policies
- Rate limiting

**Typical Duration:** 1 second (stub mode)

---

### Gate 9-10: Build Validation

**Command:** `npm run build`

**Validates:**
- TypeScript compilation (production mode)
- Vite bundling
- Asset optimization
- Bundle size

**Typical Duration:** 4-5 seconds per SPA

**Common Failures:**
- TypeScript errors (stricter in build mode)
- Missing dependencies
- Import path issues
- Build configuration errors

## Troubleshooting

### All Gates Pass Locally but Fail in CI/CD

**Causes:**
- Different Node.js versions
- Missing dependencies
- Environment variable differences

**Solutions:**
1. Check Node.js version: `node --version`
2. Reinstall dependencies: `rm -rf */node_modules && npm install`
3. Clear build artifacts: `rm -rf */dist`
4. Check CI/CD logs for specific errors

### Performance Gate Intermittently Fails

**Causes:**
- System under load
- Network latency
- Database connection issues

**Solutions:**
1. Run gate in isolation: `python3 tools/perf/smoke_stub.py`
2. Check system resources: `top` or `htop`
3. Restart services if needed

### Build Gate Fails with "Cannot find module"

**Causes:**
- Missing npm dependencies
- Incorrect import paths
- TypeScript configuration issues

**Solutions:**
1. Install dependencies: `cd crm && npm install`
2. Check import paths for typos
3. Verify `tsconfig.json` includes/excludes

### Hook Not Running

**Causes:**
- Hook not installed
- Hook not executable
- Wrong hook path

**Solutions:**
1. Verify hook exists: `ls -la .git/hooks/pre-push`
2. Make executable: `chmod +x .git/hooks/pre-push`
3. Test manually: `.git/hooks/pre-push`

See [docs/GIT_HOOKS.md](../docs/GIT_HOOKS.md) for more troubleshooting.

## Performance Benchmarks

**Full Run (All Gates):**
- With Tests + Builds: 25-35 seconds
- Skip Tests: 15-20 seconds
- Skip Tests + Builds: 5-10 seconds

**Individual Gate Benchmarks:**
- Config Validation: 1-2s
- TypeScript Check: 3-4s (per SPA)
- Unit Tests: 4-6s (per SPA)
- Security Checks: 1-2s
- Performance Tests: 1s
- Build: 4-5s (per SPA)

## Best Practices

### Development Workflow

1. **During Active Development:**
   ```bash
   # Make changes
   git add .
   git commit -m "feat: Add feature"

   # Quick validation
   ./scripts/prepush.sh --skip-tests --skip-build
   ```

2. **Before Push:**
   ```bash
   # Full validation
   ./scripts/prepush.sh

   # If green, push
   git push
   ```

3. **Hook Auto-Runs:**
   - Pre-push hook executes automatically
   - Blocks push if fails
   - Allows push if passes

### When to Run Full Gates

- ✅ Before creating pull request
- ✅ Before pushing to shared branches
- ✅ After significant refactoring
- ✅ After dependency updates
- ✅ After merging main/master

### When Skip Flags Are OK

- ✅ Local development iterations
- ✅ WIP commits on feature branches
- ✅ After full validation succeeded once
- ✅ Documentation-only changes

## Related Documentation

- **Release Management:** `scripts/release/cut.sh`
- **Quality Policy:** `POLICY.md`
- **Git Hooks:** `docs/GIT_HOOKS.md`
- **Security Checks:** `scripts/security/sanity.sh`
- **Config Validation:** `scripts/config/check.sh`
- **Performance Tests:** `tools/perf/smoke_stub.py`

## Exit Codes

- **0** - All gates passed, safe to push
- **1** - One or more gates failed, push blocked

## Examples

### Standard Workflow

```bash
# Develop features
vim crm/src/components/NewFeature.tsx

# Commit changes
git add .
git commit -m "feat: Add new feature"

# Validate before push
./scripts/prepush.sh

# Push if green
git push origin feature/new-feature
```

### Fast Iteration

```bash
# Quick validation during development
./scripts/prepush.sh --skip-tests --skip-build --quiet

# Full validation before push
./scripts/prepush.sh
```

### Debug Failed Gate

```bash
# Run with fail-fast disabled to see all failures
./scripts/prepush.sh --no-fail-fast

# Fix issues

# Re-run specific gate
cd crm && npm test

# Re-run full prepush
./scripts/prepush.sh
```

## FAQ

**Q: Do I have to run this before every push?**
A: If you install the Git hook, it runs automatically. Otherwise, run manually before pushing to shared branches.

**Q: Can I skip certain gates?**
A: Yes, use `--skip-tests` and/or `--skip-build` flags, but run full validation before final push.

**Q: What if I'm in a hurry?**
A: Use `--skip-tests --skip-build` for ~10 second validation, but run full gates before PR/merge.

**Q: How does this relate to CI/CD?**
A: This catches issues locally before pushing. CI/CD runs similar checks in the cloud after push.

**Q: What if prepush passes but CI/CD fails?**
A: Your local environment may differ. Ensure dependencies are synced and check CI/CD logs.

---

**For issues or questions, consult your team lead or refer to POLICY.md**
