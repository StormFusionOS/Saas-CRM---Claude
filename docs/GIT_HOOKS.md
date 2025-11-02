# Git Hooks Documentation

This document describes the Git hooks available for this project and how to install them.

## Available Hooks

### Pre-Push Hook

The pre-push hook runs comprehensive quality gates before pushing code to the remote repository. This ensures all code meets quality standards before it reaches the shared repository.

**What it does:**
- ✅ Configuration validation
- ✅ Secrets scanning
- ✅ TypeScript type checking (both SPAs)
- ✅ Unit tests (both SPAs)
- ✅ Security sanity checks
- ✅ Performance smoke tests
- ✅ Build validation (both SPAs)

**Benefits:**
- Prevents pushing broken code
- Catches issues early in the development cycle
- Enforces quality standards automatically
- Reduces CI/CD failures
- Saves reviewer time

## Installation

### Option 1: Manual Installation (Recommended)

Copy the pre-push hook to your `.git/hooks/` directory:

```bash
# From project root
cp hooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push
```

### Option 2: Symlink (Advanced)

Create a symlink instead of copying (changes to hook file will auto-update):

```bash
# From project root
ln -sf ../../hooks/pre-push .git/hooks/pre-push
```

### Verification

Test that the hook is installed correctly:

```bash
# This should show your pre-push hook
ls -la .git/hooks/pre-push

# Test the hook directly
.git/hooks/pre-push
```

## Hook Details

### Pre-Push Hook

**Location:** `hooks/pre-push`
**Triggers:** Before `git push` operations
**Exit Code:** 0 (allow push) or 1 (block push)

#### Hook Behavior

The pre-push hook:
1. Runs all quality gates via `scripts/prepush.sh`
2. Displays a comprehensive status matrix
3. Blocks push if any gate fails (exit 1)
4. Allows push if all gates pass (exit 0)

#### Hook Output Example

When all gates pass:
```
═══════════════════════════════════════════════════════════════════════════════
                          PRE-PUSH QUALITY GATE MATRIX
═══════════════════════════════════════════════════════════════════════════════

Gate                                     Status       Duration
-------------------------------------------------------------------------------
Configuration Validation                 ✓ PASS       2s
Secrets Scan                             ⊘ SKIP       --
TypeScript (CRM)                         ✓ PASS       3s
TypeScript (Ops)                         ✓ PASS       2s
Unit Tests (CRM)                         ✓ PASS       5s
Unit Tests (Ops)                         ✓ PASS       4s
Security Sanity Checks                   ✓ PASS       1s
Performance Smoke Tests                  ✓ PASS       1s
Build CRM SPA                            ✓ PASS       4s
Build Ops Console SPA                    ✓ PASS       4s
-------------------------------------------------------------------------------
Summary:                                 8 passed, 0 failed, 2 skipped
Total Duration:                          26s

═══════════════════════════════════════════════════════════════════════════════
                         ✓ ALL QUALITY GATES PASSED
═══════════════════════════════════════════════════════════════════════════════

Your code is ready to push!
```

When gates fail:
```
═══════════════════════════════════════════════════════════════════════════════
                         ✗ QUALITY GATES FAILED
═══════════════════════════════════════════════════════════════════════════════

2 gate(s) failed. Please fix the issues before pushing.
```

## Bypassing Hooks

### Temporary Bypass (Use with Caution)

If you need to bypass the pre-push hook for a specific push:

```bash
git push --no-verify
```

**⚠️ Warning:** Only use `--no-verify` in exceptional circumstances:
- Emergency hotfixes (with team approval)
- CI/CD pipeline context (automated pushes)
- When hook is broken and needs fixing

**Never bypass hooks for:**
- Regular development work
- "Saving time" on routine pushes
- Avoiding fixing legitimate issues

### Permanent Disable (Not Recommended)

To disable the hook permanently:

```bash
rm .git/hooks/pre-push
```

## Customization

### Skip Certain Gates

You can customize `scripts/prepush.sh` behavior:

```bash
# Skip tests (faster, but less thorough)
./scripts/prepush.sh --skip-tests

# Skip builds (not recommended)
./scripts/prepush.sh --skip-build

# Run all gates even if one fails
./scripts/prepush.sh --no-fail-fast

# Quiet mode (only show final matrix)
./scripts/prepush.sh --quiet
```

### Modify Hook Behavior

Edit `.git/hooks/pre-push` to customize hook behavior:

```bash
#!/bin/bash

# Example: Run prepush with custom flags
./scripts/prepush.sh --skip-tests --quiet

# Example: Only run during business hours
current_hour=$(date +%H)
if [[ $current_hour -ge 9 && $current_hour -le 17 ]]; then
  ./scripts/prepush.sh
else
  echo "After hours - skipping quality gates"
  exit 0
fi
```

## Troubleshooting

### Hook Not Running

**Problem:** Hook doesn't execute on `git push`

**Solutions:**
1. Verify hook exists: `ls -la .git/hooks/pre-push`
2. Check executable permissions: `chmod +x .git/hooks/pre-push`
3. Ensure no syntax errors: `bash -n .git/hooks/pre-push`
4. Test manually: `.git/hooks/pre-push`

### Hook Always Fails

**Problem:** Hook fails even with clean code

**Solutions:**
1. Run prepush script directly: `./scripts/prepush.sh`
2. Check for environment issues (Node.js, Python, dependencies)
3. Review gate output for specific failures
4. Ensure all dependencies installed: `npm install` in both SPA directories

### Hook Too Slow

**Problem:** Hook takes too long to run

**Solutions:**
1. Use `--skip-tests` for quick iterations (run full tests before final push)
2. Use `--skip-build` during rapid development (build before final push)
3. Consider using `--quiet` to reduce output overhead
4. Run specific gates manually instead of via hook

### False Positives

**Problem:** Hook fails but code is valid

**Solutions:**
1. Check if quality standards changed (review POLICY.md)
2. Verify your local environment matches CI/CD
3. Clear build artifacts: `rm -rf crm/dist ops-console/dist`
4. Clear node_modules and reinstall: `rm -rf */node_modules && npm install`
5. Report issue to team if reproducible

## Best Practices

### Development Workflow

**Recommended workflow with hooks:**

1. **During Development:**
   ```bash
   # Make changes
   git add .
   git commit -m "feat: Add new feature"

   # Run quick validation (skip tests/builds)
   ./scripts/prepush.sh --skip-tests --skip-build
   ```

2. **Before Pushing:**
   ```bash
   # Run full validation
   ./scripts/prepush.sh

   # If all green, push
   git push
   ```

3. **Pre-Push Hook Runs Automatically:**
   - Hook executes on `git push`
   - Blocks push if gates fail
   - Allows push if gates pass

### Team Standards

**When to run full gates:**
- Before creating pull request
- Before pushing to shared branches
- After merging main/master into your branch
- After significant refactoring
- Before marking PR as ready for review

**When skip flags are acceptable:**
- Local development iterations
- WIP commits on feature branches
- After running full gates successfully once
- When debugging non-code issues

## Additional Resources

- **Prepush Script:** `scripts/prepush.sh`
- **Quality Policy:** `POLICY.md`
- **Release Process:** `scripts/release/cut.sh`
- **Security Checks:** `scripts/security/sanity.sh`
- **Config Validation:** `scripts/config/check.sh`

## Hook Template

Here's the complete pre-push hook template:

```bash
#!/bin/bash
#
# Pre-push hook for RiverCityClean SaaS CRM
# Runs comprehensive quality gates before allowing push
#
# Installation:
#   cp hooks/pre-push .git/hooks/pre-push
#   chmod +x .git/hooks/pre-push
#
# Bypass (use with caution):
#   git push --no-verify
#

set -e

# Get the root directory of the repository
REPO_ROOT="$(git rev-parse --show-toplevel)"

# Change to repo root
cd "$REPO_ROOT"

# Run the prepush script
echo "Running pre-push quality gates..."
./scripts/prepush.sh

# Exit code from prepush.sh determines if push is allowed
exit $?
```

## FAQ

**Q: Can I commit without running the hook?**
A: Yes, the hook only runs on `git push`, not on `git commit`. Commits are always allowed.

**Q: Will the hook run on every branch?**
A: Yes, the pre-push hook runs for all branches. Consider branch-specific logic in the hook if needed.

**Q: How long does the hook take?**
A: Typically 20-40 seconds with all gates. Use `--skip-tests` for ~10 seconds during development.

**Q: What if CI/CD passes but hook fails?**
A: Your local environment may differ. Ensure dependencies are up to date and environment matches CI/CD.

**Q: Can hooks be shared with the team?**
A: Hooks in `.git/hooks/` are local only. Share via `hooks/` directory in repository (requires manual installation).

**Q: Do hooks work with Git GUIs?**
A: Yes, most Git GUIs respect hooks. If not, they typically have an option to enable them.

---

For questions or issues with Git hooks, consult your team lead or refer to the Git documentation.
