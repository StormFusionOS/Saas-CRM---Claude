# Supply Chain Security Guide

**Version**: 1.0
**Last Updated**: 2025-11-01
**Owner**: Security Team

## Overview

This document describes the supply chain security implementation for RiverCityClean, including SBOM generation, license policy enforcement, artifact signing, and provenance attestation.

## Components

### 1. SBOM Generation

**Tool**: `tools/sbom/generate.py`

Generates Software Bill of Materials (SBOM) in CycloneDX 1.5 JSON format for all services.

**Features**:
- Python dependency detection via import scanning
- Node.js dependency detection from package.json
- SHA-256 checksums for verification
- License information extraction

**Usage**:
```bash
# Generate SBOMs for all services
python tools/sbom/generate.py --all

# Generate for specific service
python tools/sbom/generate.py --service crm_api

# Validate existing SBOMs
python tools/sbom/generate.py --validate
```

**Output**:
- `sbom/<service>/sbom.json` - SBOM in CycloneDX format
- `sbom/<service>/SHA256SUMS` - Checksum file

### 2. License Policy

**Tool**: `tools/sbom/license_check.py`
**Policy**: `tools/sbom/allowlist.json`

Enforces license compliance by checking all dependencies against an approved license allowlist.

**Approved Licenses** (see allowlist.json):
- MIT
- Apache-2.0
- BSD-2-Clause, BSD-3-Clause
- ISC
- Other permissive licenses

**Denied Licenses**:
- GPL-2.0, GPL-3.0 (strong copyleft)
- AGPL-3.0 (viral license)
- SSPL-1.0 (server-side public license)
- Proprietary

**Usage**:
```bash
# Check all services
python tools/sbom/license_check.py

# Check specific service
python tools/sbom/license_check.py --service crm_api

# Strict mode (fail on unknown licenses)
python tools/sbom/license_check.py --strict
```

**Exit Codes**:
- 0: All licenses approved
- 1: License violations found
- 2: Configuration/file errors

### 3. Attestation Signing

**Tool**: `tools/sign/attest.py`

Creates cryptographically signed attestations with build provenance metadata.

**Attestation Contents**:
- Build ID and timestamp
- Git commit, branch, and remote
- Source file checksums
- Dependency checksums (from SBOM)
- Builder information
- HMAC-SHA256 signature

**Usage**:
```bash
# Generate signing key (first time)
python tools/sign/attest.py --generate-key

# Generate attestations for all services
python tools/sign/attest.py --all

# Generate for specific service with custom build ID
python tools/sign/attest.py --service crm_api --build-id 20251101-abc123
```

**Output**:
- `attestations/<service>/<build-id>.json` - Attestation document
- `attestations/<service>/<build-id>.sig` - HMAC signature

### 4. Attestation Verification

**Tool**: `tools/sign/verify.py`

Verifies signed attestations to ensure artifact integrity and authenticity.

**Verification Checks**:
- Signature validation (HMAC-SHA256)
- Attestation structure validation
- Material checksums verification
- Git commit verification

**Usage**:
```bash
# Verify all attestations
python tools/sign/verify.py --verify-all

# Verify specific attestation
python tools/sign/verify.py --service crm_api --build-id 20251101-abc123

# Verify all attestations for a service
python tools/sign/verify.py --service crm_api --all
```

**Exit Codes**:
- 0: All verifications passed
- 1: Verification failed
- 2: File/configuration errors

## Makefile Targets

Convenient make targets for supply chain operations:

```bash
# Run complete supply chain pipeline
make supply-chain

# Individual steps
make supply-chain-sbom       # Generate SBOMs
make supply-chain-license    # Check licenses
make supply-chain-attest     # Generate attestations
make supply-chain-verify     # Verify attestations

# Additional utilities
make supply-chain-validate          # Validate SBOMs only
make supply-chain-license-strict    # Strict license checking
```

## CI/CD Integration

### GitHub Actions Workflow

**File**: `.github/workflows/supply_chain.yml`

Automatically runs supply chain security gates on:
- Push to main/master branches
- Pull requests
- Manual workflow dispatch

**Jobs**:
1. **Generate SBOMs** - Creates SBOMs for all services
2. **License Check** - Validates licenses against policy
3. **Generate Attestations** - Signs build artifacts
4. **Verify Attestations** - Verifies signatures
5. **Supply Chain Report** - Generates summary report

**Failure Conditions**:
- SBOM generation fails
- Non-approved license detected
- Attestation signing fails
- Signature verification fails

### Workflow Artifacts

Artifacts are retained for 90 days:
- **sboms/** - Generated SBOMs with checksums
- **attestations/** - Signed attestations and signatures

## Security Best Practices

### 1. Key Management

**Development**:
- Keys generated locally with `attest.py --generate-key`
- Keys excluded from git via `.gitignore`

**Production**:
- Store keys in secure key management service (AWS Secrets Manager, HashiCorp Vault)
- Load as environment variables in CI/CD
- Rotate keys every 90 days
- Never commit keys to version control

### 2. SBOM Maintenance

**On Dependency Updates**:
1. Regenerate SBOMs: `make supply-chain-sbom`
2. Check licenses: `make supply-chain-license`
3. Review changes in pull request
4. Commit updated SBOMs to version control

**Dependency Drift Detection**:
- CI checks for SBOM changes in pull requests
- Security team reviews new dependencies
- Approved dependencies updated in allowlist

### 3. Attestation Lifecycle

**Generation**:
- Attestations generated after each build
- Build ID includes timestamp and git commit
- Attestations stored with build artifacts

**Verification**:
- Verify before deployment to production
- Check signatures match expected key
- Validate material checksums
- Confirm git commit matches source

**Retention**:
- Keep attestations for audit trail (90+ days)
- Archive with corresponding build artifacts
- Store in immutable artifact repository

## Reproducible Builds

See `docs/build/reproducible.md` for detailed guidance on creating reproducible builds.

**Key Points**:
- Use `SOURCE_DATE_EPOCH` for deterministic timestamps
- Pin exact dependency versions
- Sort file lists before processing
- Use Docker for consistent build environments

## Compliance Mapping

### SOC 2 Type II

| Control | Implementation |
|---------|----------------|
| CC7.2 - System Monitoring | SBOM generation and license checking |
| CC8.1 - Change Management | Attestation signing and verification |
| CC6.6 - Logical Access | Signing key management |

### ISO 27001

| Control | Implementation |
|---------|----------------|
| A.12.1.4 - Development Separation | Supply chain gates in CI/CD |
| A.14.1.2 - Security in Development | SBOM and license policy |
| A.14.2.8 - System Security Testing | Attestation verification |

### NIST CSF 2.0

| Function | Category | Implementation |
|----------|----------|----------------|
| Identify | PR.DS-6 | SBOM generation |
| Protect | PR.DS-2 | License policy enforcement |
| Detect | DE.CM-3 | Attestation verification |

## Troubleshooting

### SBOM Generation Issues

**Problem**: Dependencies not detected
**Solution**: Ensure code uses standard imports (Python) or package.json (Node.js)

**Problem**: License shown as UNKNOWN
**Solution**: Add license mapping to `tools/sbom/generate.py` in `KNOWN_LICENSES` dict

### License Check Failures

**Problem**: Non-approved license detected
**Solutions**:
1. Replace dependency with approved alternative
2. Request security team approval
3. Update `tools/sbom/allowlist.json` (requires approval)

### Attestation Verification Failures

**Problem**: Signature invalid
**Causes**:
- Attestation file modified after signing
- Wrong signing key used
- Signature file corrupted

**Solution**: Regenerate attestation with correct key

**Problem**: Material checksum mismatch
**Causes**:
- Source files changed after attestation
- SBOM regenerated with different checksums
- Files not committed to git

**Solution**: Regenerate attestations after source changes

## Integration Examples

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: supply-chain-check
      name: Supply Chain Security Check
      entry: make supply-chain
      language: system
      pass_filenames: false
      always_run: false
      files: \.(py|js|ts|jsx|tsx|json)$
```

### Pre-deployment Verification

```bash
#!/bin/bash
# verify-before-deploy.sh

set -euo pipefail

echo "Verifying attestations before deployment..."

# Verify attestations
python tools/sign/verify.py --verify-all

# Check license compliance
python tools/sbom/license_check.py --strict

echo "✅ All supply chain checks passed - safe to deploy"
```

### Docker Build with Attestation

```dockerfile
# Build stage with attestation
FROM python:3.11 AS builder

WORKDIR /build
COPY . .

# Generate SBOM
RUN python tools/sbom/generate.py --service crm_api

# Check licenses
RUN python tools/sbom/license_check.py --service crm_api

# Generate attestation
ARG BUILD_ID
RUN python tools/sign/attest.py --service crm_api --build-id ${BUILD_ID}

# Copy attestation to output
RUN cp attestations/crm_api/${BUILD_ID}.json /build/attestation.json
```

## References

- [CycloneDX SBOM Standard](https://cyclonedx.org/)
- [SLSA Framework](https://slsa.dev/)
- [in-toto Attestation Format](https://in-toto.io/)
- [SPDX License List](https://spdx.org/licenses/)
- [Reproducible Builds](https://reproducible-builds.org/)

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-01 | 1.0 | Initial supply chain security implementation |

