# Reproducible Builds Guide

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Build & Release Team

## Purpose

This guide documents practices and requirements for creating reproducible builds of RiverCityClean services. Reproducible builds ensure that given the same source code and build environment, identical binaries are produced every time.

## Why Reproducible Builds?

**Security Benefits**:
- Verify that distributed binaries match source code
- Detect tampering or backdoors in build pipeline
- Enable independent verification by third parties
- Build trust with customers and auditors

**Operational Benefits**:
- Simplify debugging and troubleshooting
- Enable precise rollback to previous builds
- Facilitate compliance and auditing
- Support supply chain security initiatives

## Services Overview

RiverCityClean consists of four services:

| Service | Type | Build Tool | Output |
|---------|------|------------|--------|
| crm_api | Python | setuptools | Python package |
| ops_api | Python | setuptools | Python package |
| crm | Node.js | Vite | Static assets (dist/) |
| ops-console | Node.js | Vite | Static assets (dist/) |

---

## Python Services (crm_api, ops_api)

### Build Environment

**Required Tools**:
- Python 3.11+ (exact version should be pinned)
- pip 23.0+
- virtualenv or venv

**Environment Variables**:
```bash
# Ensure consistent locale
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Disable randomization
export PYTHONHASHSEED=0

# Consistent timezone
export TZ=UTC
```

### Deterministic Python Builds

#### 1. Pin All Dependencies

Create `requirements.txt` with exact versions (no ranges):

```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
# ... etc
```

**Generate with**:
```bash
pip freeze > requirements.txt
```

#### 2. Use SOURCE_DATE_EPOCH

Set `SOURCE_DATE_EPOCH` to git commit timestamp:

```bash
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
```

This ensures:
- Consistent file modification times in packages
- Reproducible .pyc bytecode files
- Deterministic archive timestamps

#### 3. Python Wheel Compilation

When building Python wheels, use these flags:

```bash
# Install dependencies deterministically
pip install --no-cache-dir --require-hashes -r requirements.txt

# Build wheel with deterministic settings
python -m build --wheel \
    --config-setting="--global-option=--build-timestamp=${SOURCE_DATE_EPOCH}"
```

**Key Options**:
- `--no-cache-dir`: Prevent pip cache influence
- `--require-hashes`: Enforce integrity checks
- `--build-timestamp`: Set consistent timestamps

#### 4. Bytecode Compilation

Ensure deterministic .pyc files:

```bash
# Compile with deterministic timestamp
python -m compileall \
    -b \
    -f \
    -q \
    --invalidation-mode=checked-hash \
    app/
```

### Python Build Script Example

```bash
#!/usr/bin/env bash
# build-python-service.sh

set -euo pipefail

SERVICE_NAME="crm_api"
SOURCE_DIR="/path/to/${SERVICE_NAME}"

# Set reproducible environment
export PYTHONHASHSEED=0
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export TZ=UTC
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

echo "Building ${SERVICE_NAME} with SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}"

# Create clean virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies deterministically
pip install --no-cache-dir --upgrade pip==23.3.1
pip install --no-cache-dir -r requirements.txt

# Compile bytecode deterministically
python -m compileall -b -f -q app/

# Calculate checksums
find app -type f -name "*.py" -o -name "*.pyc" | sort | xargs sha256sum > checksums.txt

echo "Build complete. Checksum: $(sha256sum checksums.txt)"
```

---

## Node.js Services (crm, ops-console)

### Build Environment

**Required Tools**:
- Node.js 20.x (exact version should be pinned)
- npm 10.x or pnpm 8.x

**Environment Variables**:
```bash
# Consistent locale
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

# Consistent timezone
export TZ=UTC

# Node environment
export NODE_ENV=production

# Disable telemetry
export NEXT_TELEMETRY_DISABLED=1
```

### Deterministic Node.js Builds

#### 1. Lock File Management

**Use `package-lock.json` (npm) or `pnpm-lock.yaml` (pnpm)**:

```bash
# Generate/update lock file
npm install --package-lock-only

# Or with pnpm
pnpm install --frozen-lockfile
```

**Commit lock files**:
- Always commit lock files to version control
- Never use `npm install` without lock file in CI
- Use `npm ci` for reproducible installs

#### 2. Set SOURCE_DATE_EPOCH

```bash
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
```

#### 3. Vite Build Configuration

Configure Vite for reproducibility in `vite.config.ts`:

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // Disable minification randomization
    minify: 'terser',
    terserOptions: {
      compress: {
        // Deterministic compression
        passes: 2,
      },
      mangle: {
        // Consistent name mangling
        safari10: false,
      },
      format: {
        // Consistent formatting
        comments: false,
      },
    },
    // Consistent chunk names
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]',
        // Deterministic chunk splitting
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          utils: ['axios'],
        },
      },
    },
    // Disable source maps in production (optional)
    sourcemap: false,
  },
})
```

#### 4. Deterministic npm Scripts

In `package.json`:

```json
{
  "scripts": {
    "build": "tsc && vite build",
    "build:reproducible": "SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct) npm run build"
  }
}
```

### Node.js Build Script Example

```bash
#!/usr/bin/env bash
# build-nodejs-service.sh

set -euo pipefail

SERVICE_NAME="crm"
SOURCE_DIR="/path/to/${SERVICE_NAME}"

# Set reproducible environment
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export TZ=UTC
export NODE_ENV=production
export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

echo "Building ${SERVICE_NAME} with SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}"

# Clean previous build
rm -rf dist node_modules

# Install dependencies from lock file (no updates)
npm ci --prefer-offline --no-audit

# Build
npm run build

# Calculate checksums
find dist -type f | sort | xargs sha256sum > dist/checksums.txt

echo "Build complete. Checksum: $(sha256sum dist/checksums.txt)"
```

---

## Checksum Verification

### Generating Checksums

After each build, generate SHA-256 checksums:

```bash
# For Python services
find app -type f \( -name "*.py" -o -name "*.pyc" \) | sort | xargs sha256sum > build-checksums.txt

# For Node.js services
find dist -type f | sort | xargs sha256sum > dist/SHA256SUMS
```

### Comparing Builds

To verify reproducibility:

```bash
#!/usr/bin/env bash
# compare-builds.sh

BUILD1_CHECKSUMS="$1"
BUILD2_CHECKSUMS="$2"

if diff -u "${BUILD1_CHECKSUMS}" "${BUILD2_CHECKSUMS}"; then
    echo "✅ Builds are identical (reproducible)"
    exit 0
else
    echo "❌ Builds differ (not reproducible)"
    echo "Differences:"
    diff -u "${BUILD1_CHECKSUMS}" "${BUILD2_CHECKSUMS}" | head -20
    exit 1
fi
```

### CI Integration

Include checksum verification in CI:

```yaml
# .github/workflows/verify-reproducibility.yml
- name: Build twice and compare
  run: |
    # First build
    make build-crm
    cp dist/SHA256SUMS dist/SHA256SUMS.build1

    # Clean and second build
    make clean
    make build-crm
    cp dist/SHA256SUMS dist/SHA256SUMS.build2

    # Compare
    diff dist/SHA256SUMS.build1 dist/SHA256SUMS.build2
```

---

## Common Reproducibility Issues

### Issue 1: Timestamps

**Problem**: Build includes current timestamps
**Solution**: Use `SOURCE_DATE_EPOCH` from git commit

### Issue 2: Randomization

**Problem**: Build tools use random seeds
**Solution**:
- Python: Set `PYTHONHASHSEED=0`
- Node.js: Use deterministic minification settings

### Issue 3: File Ordering

**Problem**: File system iteration order is non-deterministic
**Solution**: Always sort file lists before processing

```bash
# Bad
find . -name "*.py" | xargs sha256sum

# Good
find . -name "*.py" | sort | xargs sha256sum
```

### Issue 4: Dependency Versions

**Problem**: Dependencies updated between builds
**Solution**: Use lock files and pin exact versions

### Issue 5: Build Environment

**Problem**: Different build environments produce different results
**Solution**: Use Docker for consistent build environment

---

## Docker for Reproducible Builds

### Python Service Dockerfile

```dockerfile
# Dockerfile.crm_api
FROM python:3.11.6-slim-bookworm AS builder

# Set reproducible environment
ENV PYTHONHASHSEED=0 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TZ=UTC \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Copy dependency specifications
COPY requirements.txt .

# Install dependencies
RUN pip install --require-hashes -r requirements.txt

# Copy source code
COPY app/ app/

# Set build timestamp from git commit
ARG SOURCE_DATE_EPOCH
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}

# Compile bytecode
RUN python -m compileall -b -f -q app/

# Generate checksums
RUN find app -type f | sort | xargs sha256sum > checksums.txt

# Production image
FROM python:3.11.6-slim-bookworm

WORKDIR /app
COPY --from=builder /build /app

CMD ["python", "-m", "app.main"]
```

### Node.js Service Dockerfile

```dockerfile
# Dockerfile.crm
FROM node:20.10.0-alpine AS builder

# Set reproducible environment
ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    TZ=UTC \
    NODE_ENV=production

WORKDIR /build

# Copy dependency specifications
COPY package.json package-lock.json ./

# Install dependencies from lock file
RUN npm ci --prefer-offline --no-audit

# Copy source code
COPY . .

# Set build timestamp from git commit
ARG SOURCE_DATE_EPOCH
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}

# Build
RUN npm run build

# Generate checksums
RUN find dist -type f | sort | xargs sha256sum > dist/SHA256SUMS

# Production image
FROM nginx:alpine
COPY --from=builder /build/dist /usr/share/nginx/html
```

### Building with Docker

```bash
# Get git commit timestamp
SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)

# Build with timestamp
docker build \
    --build-arg SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH} \
    -t crm_api:reproducible \
    -f Dockerfile.crm_api \
    .
```

---

## Verification Workflow

### Daily Verification

Run daily builds and compare checksums:

```bash
#!/usr/bin/env bash
# daily-reproducibility-check.sh

SERVICES=("crm_api" "ops_api" "crm" "ops-console")

for service in "${SERVICES[@]}"; do
    echo "Checking reproducibility for ${service}..."

    # Build twice
    make "build-${service}"
    CHECKSUM1=$(cat "checksums/${service}.txt")

    make "clean-${service}"
    make "build-${service}"
    CHECKSUM2=$(cat "checksums/${service}.txt")

    # Compare
    if [ "${CHECKSUM1}" == "${CHECKSUM2}" ]; then
        echo "✅ ${service} is reproducible"
    else
        echo "❌ ${service} is NOT reproducible"
        exit 1
    fi
done

echo "✅ All services are reproducible"
```

### Integration with Supply Chain

Reproducible builds integrate with supply chain security:

1. **SBOM Generation**: Generated after each build
2. **Attestation Signing**: Attestation includes build checksums
3. **License Checking**: Verified before build
4. **Verification**: CI verifies reproducibility

---

## Best Practices

### DO ✅

- Always use `SOURCE_DATE_EPOCH` for timestamps
- Pin exact dependency versions in lock files
- Sort file lists before processing
- Use consistent build environments (Docker)
- Test reproducibility in CI
- Document build environment requirements
- Include checksums in attestations

### DON'T ❌

- Don't use current date/time in builds
- Don't allow floating dependency versions
- Don't rely on file system ordering
- Don't skip lock file commits
- Don't use random seeds without fixing them
- Don't ignore non-reproducible warnings

---

## Compliance & Auditing

### SOC 2 Controls

- **CC7.2**: System monitoring (build verification)
- **CC8.1**: Change management (reproducible releases)

### ISO 27001 Controls

- **A.12.1.4**: Separation of development and production environments
- **A.14.2.8**: System security testing (build verification)

### NIST CSF

- **PR.DS-6**: Integrity checking mechanisms
- **DE.CM-3**: Detection processes tested

---

## Troubleshooting

### Problem: Builds are not reproducible

**Diagnosis**:
```bash
# Compare two builds
diff -u build1/checksums.txt build2/checksums.txt

# Check for timestamp differences
stat build1/file.py build2/file.py
```

**Solutions**:
1. Verify `SOURCE_DATE_EPOCH` is set
2. Check for randomization (PYTHONHASHSEED, etc.)
3. Ensure dependency versions are locked
4. Verify file ordering in scripts

### Problem: Checksums don't match after git clone

**Cause**: Different line endings (CRLF vs LF)

**Solution**:
```bash
# Configure git to use LF
git config --global core.autocrlf input
```

### Problem: Docker builds are not reproducible

**Solutions**:
1. Pin base image to exact digest
2. Use `--build-arg SOURCE_DATE_EPOCH`
3. Disable layer caching for verification builds

---

## References

- [Reproducible Builds Project](https://reproducible-builds.org/)
- [Python Wheel Documentation](https://wheel.readthedocs.io/)
- [Vite Build Options](https://vitejs.dev/config/build-options.html)
- [SOURCE_DATE_EPOCH Specification](https://reproducible-builds.org/specs/source-date-epoch/)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial documentation |

