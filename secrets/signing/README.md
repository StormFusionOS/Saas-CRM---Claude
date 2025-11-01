# Signing Keys

This directory contains signing keys for attestation generation.

## Setup

Generate signing keys before first use:

```bash
python tools/sign/attest.py --generate-key
```

This will create:
- `attestor.key` - Private signing key (keep secret, not committed to git)
- `attestor.pub` - Public key hash (can be shared)

## Production Usage

In production, keys should be:
1. Generated once and securely stored (e.g., AWS Secrets Manager, HashiCorp Vault)
2. Loaded as environment variables in CI/CD
3. Never committed to version control
4. Rotated regularly (every 90 days recommended)

## CI Configuration

For GitHub Actions:

```yaml
- name: Set up signing key
  env:
    SIGNING_KEY: ${{ secrets.ATTESTOR_KEY }}
  run: |
    mkdir -p secrets/signing
    echo "$SIGNING_KEY" > secrets/signing/attestor.key
    chmod 600 secrets/signing/attestor.key
```

## Key Rotation

To rotate signing keys:

1. Generate new key: `python tools/sign/attest.py --generate-key`
2. Update CI secrets with new key
3. Re-sign recent attestations with new key
4. Archive old key securely (for verification of old attestations)

## Security Notes

- The `.gitignore` file excludes `secrets/` directory from version control
- Private key file has 600 permissions (owner read/write only)
- Never share the private key via email, Slack, or other channels
- Use secure key management systems in production
