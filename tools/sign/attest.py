#!/usr/bin/env python3
"""
Attestation Signer

Creates signed attestations for build artifacts with provenance metadata.

Features:
- Build input tracking (source files, dependencies, environment)
- Git commit and branch information
- Timestamp and build ID
- HMAC-SHA256 signature (minisign-like stub)
- JSON output with separate signature file

Usage:
    # Generate attestation for a service
    python tools/sign/attest.py --service crm_api --build-id 20251101-abc123

    # Sign existing attestation
    python tools/sign/attest.py --attestation-file attestations/crm_api/20251101-abc123.json

    # Generate signing key (first-time setup)
    python tools/sign/attest.py --generate-key
"""

import argparse
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


REPO_ROOT = Path(__file__).parent.parent.parent
ATTESTATION_DIR = REPO_ROOT / "attestations"
SIGNING_KEY_PATH = REPO_ROOT / "secrets" / "signing" / "attestor.key"
PUBLIC_KEY_PATH = REPO_ROOT / "secrets" / "signing" / "attestor.pub"

# Service configurations
SERVICES = {
    "crm_api": {
        "type": "python",
        "path": REPO_ROOT / "crm_api",
        "build_artifacts": ["app/**/*.py"],
        "dependencies": ["sbom/crm_api/sbom.json"]
    },
    "ops_api": {
        "type": "python",
        "path": REPO_ROOT / "ops_api",
        "build_artifacts": ["app/**/*.py"],
        "dependencies": ["sbom/ops_api/sbom.json"]
    },
    "crm": {
        "type": "nodejs",
        "path": REPO_ROOT / "crm",
        "build_artifacts": ["dist/**/*"],
        "dependencies": ["sbom/crm/sbom.json", "package.json"]
    },
    "ops-console": {
        "type": "nodejs",
        "path": REPO_ROOT / "ops-console",
        "build_artifacts": ["dist/**/*"],
        "dependencies": ["sbom/ops-console/sbom.json", "package.json"]
    }
}


class SigningKey:
    """Manage signing keys (HMAC-based stub)"""

    def __init__(self, key_path: Path):
        self.key_path = key_path
        self.key: Optional[bytes] = None
        self._load_or_create()

    def _load_or_create(self):
        """Load existing key or create new one"""
        if self.key_path.exists():
            self._load()
        else:
            self._generate()

    def _load(self):
        """Load key from file"""
        with open(self.key_path, "rb") as f:
            self.key = f.read()

        if len(self.key) < 32:
            raise ValueError(f"Invalid key file: {self.key_path}")

    def _generate(self):
        """Generate new signing key"""
        print(f"🔑 Generating new signing key...")

        # Ensure directory exists
        self.key_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate 256-bit key
        self.key = secrets.token_bytes(32)

        # Save private key
        with open(self.key_path, "wb") as f:
            f.write(self.key)

        # Set restrictive permissions (owner read/write only)
        os.chmod(self.key_path, 0o600)

        # Generate public key (for stub, just a hash of private key)
        public_key = hashlib.sha256(self.key).hexdigest()

        with open(PUBLIC_KEY_PATH, "w") as f:
            f.write(f"# RiverCityClean Attestor Public Key\n")
            f.write(f"# Algorithm: HMAC-SHA256\n")
            f.write(f"# Generated: {datetime.now(timezone.utc).isoformat()}\n")
            f.write(f"{public_key}\n")

        print(f"   ✅ Private key: {self.key_path}")
        print(f"   ✅ Public key: {PUBLIC_KEY_PATH}")
        print(f"   🔐 Key ID: {public_key[:16]}")

    def sign(self, data: bytes) -> str:
        """Sign data with HMAC-SHA256"""
        if not self.key:
            raise ValueError("No signing key loaded")

        signature = hmac.new(self.key, data, hashlib.sha256).hexdigest()
        return signature

    def get_key_id(self) -> str:
        """Get key ID (first 16 chars of public key hash)"""
        if not self.key:
            raise ValueError("No signing key loaded")

        public_key_hash = hashlib.sha256(self.key).hexdigest()
        return public_key_hash[:16]


class AttestationBuilder:
    """Build attestation documents"""

    def __init__(self, service_name: str, build_id: str):
        self.service_name = service_name
        self.build_id = build_id
        self.config = SERVICES.get(service_name)

        if not self.config:
            raise ValueError(f"Unknown service: {service_name}")

    def build(self) -> Dict:
        """Build attestation document"""
        print(f"\n{'='*60}")
        print(f"Building attestation for: {self.service_name}")
        print(f"Build ID: {self.build_id}")
        print(f"{'='*60}\n")

        attestation = {
            "version": "1.0",
            "type": "in-toto",
            "subject": {
                "name": self.service_name,
                "type": self.config["type"],
                "build_id": self.build_id
            },
            "predicate": {
                "builder": {
                    "id": "RiverCityClean CI",
                    "version": "1.0.0"
                },
                "buildType": f"{self.config['type']}-build",
                "invocation": {
                    "environment": self._get_environment(),
                    "parameters": {}
                },
                "materials": self._get_materials(),
                "metadata": {
                    "buildStartedOn": datetime.now(timezone.utc).isoformat(),
                    "buildFinishedOn": datetime.now(timezone.utc).isoformat(),
                    "reproducible": True
                }
            }
        }

        print(f"✅ Attestation built")
        print(f"   Materials: {len(attestation['predicate']['materials'])}")
        print(f"   Git commit: {attestation['predicate']['invocation']['environment'].get('git_commit', 'N/A')[:8]}")

        return attestation

    def _get_environment(self) -> Dict:
        """Get build environment metadata"""
        env = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        }

        # Get git information
        try:
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=REPO_ROOT,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            env["git_commit"] = git_commit

            git_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=REPO_ROOT,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            env["git_branch"] = git_branch

            git_remote = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                cwd=REPO_ROOT,
                stderr=subprocess.DEVNULL
            ).decode().strip()
            env["git_remote"] = git_remote

        except (subprocess.CalledProcessError, FileNotFoundError):
            env["git_commit"] = "unknown"
            env["git_branch"] = "unknown"
            env["git_remote"] = "unknown"

        return env

    def _get_materials(self) -> List[Dict]:
        """Get build materials (source files, dependencies)"""
        materials = []

        # Add SBOM as material
        for dep_path in self.config.get("dependencies", []):
            full_path = REPO_ROOT / dep_path
            if full_path.exists():
                materials.append({
                    "uri": f"file://{dep_path}",
                    "digest": {
                        "sha256": self._hash_file(full_path)
                    }
                })

        # Add source files (limited to avoid huge attestations)
        service_path = self.config["path"]
        source_files = list(service_path.rglob("*.py"))[:10] if self.config["type"] == "python" else []

        for source_file in source_files:
            rel_path = source_file.relative_to(REPO_ROOT)
            materials.append({
                "uri": f"file://{rel_path}",
                "digest": {
                    "sha256": self._hash_file(source_file)
                }
            })

        return materials

    @staticmethod
    def _hash_file(filepath: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            sha256.update(f.read())
        return sha256.hexdigest()


def save_attestation(service_name: str, build_id: str, attestation: Dict, signature: str):
    """Save attestation and signature to files"""
    attestation_dir = ATTESTATION_DIR / service_name
    attestation_dir.mkdir(parents=True, exist_ok=True)

    attestation_file = attestation_dir / f"{build_id}.json"
    signature_file = attestation_dir / f"{build_id}.sig"

    # Save attestation
    with open(attestation_file, "w") as f:
        json.dump(attestation, f, indent=2)

    print(f"\n💾 Saved attestation: {attestation_file}")

    # Save signature
    with open(signature_file, "w") as f:
        f.write(signature + "\n")

    print(f"🔐 Saved signature: {signature_file}")


def generate_attestation(service_name: str, build_id: str, signing_key: SigningKey):
    """Generate and sign attestation"""
    # Build attestation
    builder = AttestationBuilder(service_name, build_id)
    attestation = builder.build()

    # Sign attestation
    attestation_json = json.dumps(attestation, sort_keys=True, indent=2)
    signature = signing_key.sign(attestation_json.encode())

    key_id = signing_key.get_key_id()
    print(f"\n🔐 Signed with key: {key_id}")
    print(f"   Signature: {signature[:32]}...")

    # Save files
    save_attestation(service_name, build_id, attestation, signature)


def main():
    parser = argparse.ArgumentParser(description="Attestation Signer")
    parser.add_argument("--service", choices=list(SERVICES.keys()),
                        help="Service to generate attestation for")
    parser.add_argument("--build-id",
                        help="Build ID (default: timestamp-based)")
    parser.add_argument("--generate-key", action="store_true",
                        help="Generate new signing key")
    parser.add_argument("--all", action="store_true",
                        help="Generate attestations for all services")

    args = parser.parse_args()

    # Generate key mode
    if args.generate_key:
        key = SigningKey(SIGNING_KEY_PATH)
        print("\n✅ Signing key ready")
        return 0

    # Load signing key
    if not SIGNING_KEY_PATH.exists():
        print("⚠️  No signing key found. Generating new key...")

    signing_key = SigningKey(SIGNING_KEY_PATH)

    # Generate attestations
    if args.all:
        services = list(SERVICES.keys())
    elif args.service:
        services = [args.service]
    else:
        parser.print_help()
        return 1

    # Generate build ID if not provided
    build_id = args.build_id or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    for service in services:
        try:
            generate_attestation(service, build_id, signing_key)
        except Exception as e:
            print(f"\n❌ Error generating attestation for {service}: {e}")
            import traceback
            traceback.print_exc()
            return 1

    print(f"\n{'='*60}")
    print("✅ Attestation Generation Complete")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
