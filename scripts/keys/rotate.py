#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
JWKS Key Rotation Script

Rotates JWT signing keys with grace period support.

Features:
- Generates new kid (key ID)
- Updates JWKS with new key
- Maintains old keys during grace period
- Updates .env placeholders
- Validates rotation

Usage:
    # Normal rotation (90 day interval)
    python scripts/keys/rotate.py

    # Emergency rotation (immediate invalidation)
    python scripts/keys/rotate.py --emergency

    # Custom grace period
    python scripts/keys/rotate.py --grace-period 24  # hours
"""

import argparse
import json
import secrets
import base64
import time
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta


SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent
KEYS_DIR = REPO_ROOT / "secrets" / "keys"
ENV_EXAMPLE = REPO_ROOT / ".env.example"

DEFAULT_GRACE_PERIOD_HOURS = 72  # 3 days
ROTATION_INTERVAL_DAYS = 90


def generate_kid() -> str:
    """Generate a new key ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = secrets.token_hex(4)
    return f"key-{timestamp}-{random_suffix}"


def generate_secret_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key"""
    return secrets.token_urlsafe(length)


def load_jwks(tenant: str) -> dict:
    """Load JWKS for a tenant"""
    jwks_file = KEYS_DIR / f"{tenant}_jwks.json"
    if not jwks_file.exists():
        return {"keys": []}

    with open(jwks_file, "r") as f:
        return json.load(f)


def save_jwks(tenant: str, jwks: dict):
    """Save JWKS for a tenant"""
    jwks_file = KEYS_DIR / f"{tenant}_jwks.json"
    with open(jwks_file, "w") as f:
        json.dump(jwks, f, indent=2)


def rotate_keys(tenant: str, grace_period_hours: int, emergency: bool = False):
    """Rotate keys for a tenant"""
    print(f"\n{'='*60}")
    print(f"Rotating keys for tenant: {tenant.upper()}")
    print(f"{'='*60}\n")

    # Load current JWKS
    jwks = load_jwks(tenant)
    current_keys = jwks.get("keys", [])

    # Generate new key
    new_kid = generate_kid()
    new_secret = generate_secret_key()

    new_key = {
        "kty": "oct",
        "use": "sig",
        "kid": new_kid,
        "alg": "HS256",
        "k": base64.urlsafe_b64encode(new_secret.encode()).decode().rstrip("="),
        "created_at": time.time(),
        "expires_at": time.time() + (grace_period_hours * 3600) if not emergency else time.time()
    }

    print(f"✅ New key generated: {new_kid}")

    # Handle grace period
    now = time.time()
    valid_keys = []

    if emergency:
        print(f"⚠️  EMERGENCY ROTATION: All old keys invalidated immediately")
    else:
        # Keep keys within grace period
        for key in current_keys:
            expires_at = key.get("expires_at", 0)
            if expires_at > now:
                valid_keys.append(key)
                remaining_hours = (expires_at - now) / 3600
                print(f"   Keeping key {key['kid']} (expires in {remaining_hours:.1f}h)")
            else:
                print(f"   Removing expired key {key['kid']}")

    # Add new key
    valid_keys.insert(0, new_key)  # New key first in list

    # Update JWKS
    jwks["keys"] = valid_keys
    save_jwks(tenant, jwks)

    print(f"\n✅ JWKS updated with {len(valid_keys)} active key(s)")
    print(f"   Primary (new) key: {new_kid}")
    print(f"   Grace period: {grace_period_hours}h")

    # Update .env.example
    update_env_example(tenant, new_kid, new_secret)

    return new_kid, new_secret


def update_env_example(tenant: str, kid: str, secret: str):
    """Update .env.example with new key placeholders"""
    env_var_prefix = tenant.upper()

    print(f"\n📝 Updating .env.example...")

    # Read current .env.example
    if not ENV_EXAMPLE.exists():
        print(f"   ⚠️  .env.example not found, skipping")
        return

    with open(ENV_EXAMPLE, "r") as f:
        lines = f.readlines()

    # Update relevant lines
    updated_lines = []
    updated = False

    for line in lines:
        if f"{env_var_prefix}_JWT_SECRET=" in line:
            updated_lines.append(f"{env_var_prefix}_JWT_SECRET=<REPLACE-WITH-ROTATED-SECRET>  # kid: {kid}\n")
            updated = True
        elif f"{env_var_prefix}_JWT_KID=" in line:
            updated_lines.append(f"{env_var_prefix}_JWT_KID={kid}\n")
            updated = True
        else:
            updated_lines.append(line)

    if updated:
        with open(ENV_EXAMPLE, "w") as f:
            f.writelines(updated_lines)
        print(f"   ✅ Updated {env_var_prefix}_JWT_SECRET and {env_var_prefix}_JWT_KID")
    else:
        print(f"   ℹ️  No matching environment variables found")


def validate_rotation(tenant: str):
    """Validate that rotation was successful"""
    print(f"\n🔍 Validating rotation for {tenant}...")

    jwks = load_jwks(tenant)
    keys = jwks.get("keys", [])

    if not keys:
        print(f"   ❌ No keys found in JWKS")
        return False

    primary_key = keys[0]
    print(f"   ✅ Primary key: {primary_key['kid']}")
    print(f"   ✅ Total active keys: {len(keys)}")

    # Check expiration
    now = time.time()
    for i, key in enumerate(keys):
        expires_at = key.get("expires_at", float('inf'))
        if expires_at > now:
            remaining = (expires_at - now) / 3600
            print(f"   ✅ Key {i+1} valid for {remaining:.1f}h more")
        else:
            print(f"   ⚠️  Key {i+1} expired")

    return True


def main():
    parser = argparse.ArgumentParser(description="JWKS Key Rotation")
    parser.add_argument("--tenant", choices=["crm", "ops", "all"], default="all",
                        help="Tenant to rotate keys for")
    parser.add_argument("--grace-period", type=int, default=DEFAULT_GRACE_PERIOD_HOURS,
                        help=f"Grace period in hours (default: {DEFAULT_GRACE_PERIOD_HOURS})")
    parser.add_argument("--emergency", action="store_true",
                        help="Emergency rotation (invalidate old keys immediately)")
    parser.add_argument("--validate", action="store_true",
                        help="Validate rotation only (no changes)")

    args = parser.parse_args()

    # Ensure keys directory exists
    KEYS_DIR.mkdir(parents=True, exist_ok=True)

    # Validation mode
    if args.validate:
        tenants = ["crm", "ops"] if args.tenant == "all" else [args.tenant]
        for tenant in tenants:
            validate_rotation(tenant)
        return 0

    # Rotation mode
    if args.emergency:
        print("\n⚠️  WARNING: Emergency rotation will invalidate all old keys immediately!")
        confirm = input("   Type 'CONFIRM' to proceed: ")
        if confirm != "CONFIRM":
            print("   Cancelled")
            return 1

    tenants = ["crm", "ops"] if args.tenant == "all" else [args.tenant]

    for tenant in tenants:
        try:
            rotate_keys(tenant, args.grace_period, args.emergency)
            validate_rotation(tenant)
        except Exception as e:
            print(f"\n❌ Error rotating keys for {tenant}: {e}")
            return 1

    print(f"\n{'='*60}")
    print("✅ Key Rotation Complete")
    print(f"{'='*60}")
    print(f"\n📋 Next Steps:")
    print(f"   1. Update production .env files with new JWT_SECRET values")
    print(f"   2. Restart API services to use new keys")
    print(f"   3. Monitor for token validation errors")
    print(f"   4. Old keys will expire after grace period ({args.grace_period}h)")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
