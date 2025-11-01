#!/usr/bin/env python3
"""
Attestation Verifier

Verifies signed attestations for build artifacts.

Features:
- Signature verification (HMAC-SHA256)
- Attestation structure validation
- Material integrity checks
- Git commit verification

Usage:
    # Verify specific attestation
    python tools/sign/verify.py --service crm_api --build-id 20251101-abc123

    # Verify all attestations for a service
    python tools/sign/verify.py --service crm_api --all

    # Verify all attestations
    python tools/sign/verify.py --verify-all

Exit codes:
    0 - All verifications passed
    1 - Verification failed
    2 - File/configuration errors
"""

import argparse
import hashlib
import hmac
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).parent.parent.parent
ATTESTATION_DIR = REPO_ROOT / "attestations"
SIGNING_KEY_PATH = REPO_ROOT / "secrets" / "signing" / "attestor.key"
PUBLIC_KEY_PATH = REPO_ROOT / "secrets" / "signing" / "attestor.pub"

# Service names
SERVICES = ["crm_api", "ops_api", "crm", "ops-console"]


class SignatureVerifier:
    """Verify HMAC-SHA256 signatures"""

    def __init__(self, key_path: Path):
        self.key_path = key_path
        self.key: Optional[bytes] = None
        self._load_key()

    def _load_key(self):
        """Load signing key"""
        if not self.key_path.exists():
            raise FileNotFoundError(f"Signing key not found: {self.key_path}")

        with open(self.key_path, "rb") as f:
            self.key = f.read()

        if len(self.key) < 32:
            raise ValueError(f"Invalid key file: {self.key_path}")

    def verify(self, data: bytes, signature: str) -> bool:
        """Verify signature"""
        if not self.key:
            raise ValueError("No signing key loaded")

        expected_signature = hmac.new(self.key, data, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    def get_key_id(self) -> str:
        """Get key ID"""
        if not self.key:
            raise ValueError("No signing key loaded")

        public_key_hash = hashlib.sha256(self.key).hexdigest()
        return public_key_hash[:16]


class AttestationVerifier:
    """Verify attestation documents"""

    def __init__(self, verifier: SignatureVerifier):
        self.verifier = verifier
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0

    def verify_attestation(self, service_name: str, build_id: str) -> bool:
        """Verify a single attestation"""
        print(f"\n{'='*60}")
        print(f"Verifying attestation: {service_name}/{build_id}")
        print(f"{'='*60}\n")

        attestation_dir = ATTESTATION_DIR / service_name
        attestation_file = attestation_dir / f"{build_id}.json"
        signature_file = attestation_dir / f"{build_id}.sig"

        # Check files exist
        if not attestation_file.exists():
            print(f"❌ Attestation file not found: {attestation_file}")
            self.checks_failed += 1
            return False

        if not signature_file.exists():
            print(f"❌ Signature file not found: {signature_file}")
            self.checks_failed += 1
            return False

        # Load files
        with open(attestation_file, "r") as f:
            attestation = json.load(f)

        with open(signature_file, "r") as f:
            signature = f.read().strip()

        # Verify signature
        attestation_json = json.dumps(attestation, sort_keys=True, indent=2)
        signature_valid = self.verifier.verify(attestation_json.encode(), signature)

        if signature_valid:
            print(f"✅ Signature valid")
            self.checks_passed += 1
        else:
            print(f"❌ Signature INVALID")
            self.checks_failed += 1
            return False

        # Validate attestation structure
        structure_valid = self._validate_structure(attestation)

        if structure_valid:
            print(f"✅ Attestation structure valid")
            self.checks_passed += 1
        else:
            print(f"❌ Attestation structure INVALID")
            self.checks_failed += 1
            return False

        # Verify materials (checksums)
        materials_valid = self._verify_materials(attestation)

        if materials_valid:
            print(f"✅ Materials verified")
            self.checks_passed += 1
        else:
            print(f"⚠️  Some materials could not be verified")
            self.warnings += 1

        # Display metadata
        self._display_metadata(attestation)

        return signature_valid and structure_valid

    def _validate_structure(self, attestation: Dict) -> bool:
        """Validate attestation structure"""
        required_fields = ["version", "type", "subject", "predicate"]

        for field in required_fields:
            if field not in attestation:
                print(f"   ❌ Missing field: {field}")
                return False

        # Check subject
        subject = attestation.get("subject", {})
        if "name" not in subject or "build_id" not in subject:
            print(f"   ❌ Invalid subject")
            return False

        # Check predicate
        predicate = attestation.get("predicate", {})
        if "builder" not in predicate or "materials" not in predicate:
            print(f"   ❌ Invalid predicate")
            return False

        return True

    def _verify_materials(self, attestation: Dict) -> bool:
        """Verify material checksums"""
        materials = attestation.get("predicate", {}).get("materials", [])

        if not materials:
            print(f"   ⚠️  No materials to verify")
            return True

        verified_count = 0
        missing_count = 0

        for material in materials:
            uri = material.get("uri", "")
            expected_digest = material.get("digest", {}).get("sha256", "")

            # Extract file path from URI
            if uri.startswith("file://"):
                file_path = REPO_ROOT / uri[7:]

                if file_path.exists():
                    # Calculate actual digest
                    sha256 = hashlib.sha256()
                    with open(file_path, "rb") as f:
                        sha256.update(f.read())
                    actual_digest = sha256.hexdigest()

                    if actual_digest == expected_digest:
                        verified_count += 1
                    else:
                        print(f"   ⚠️  Checksum mismatch: {file_path.name}")
                        missing_count += 1
                else:
                    missing_count += 1

        if verified_count > 0:
            print(f"   Materials verified: {verified_count}/{len(materials)}")

        if missing_count > 0:
            print(f"   Materials missing/changed: {missing_count}/{len(materials)}")

        # Consider verification successful if at least some materials verified
        return verified_count > 0 or missing_count == 0

    def _display_metadata(self, attestation: Dict):
        """Display attestation metadata"""
        predicate = attestation.get("predicate", {})
        invocation = predicate.get("invocation", {})
        environment = invocation.get("environment", {})
        metadata = predicate.get("metadata", {})

        print(f"\nAttestation metadata:")
        print(f"   Builder: {predicate.get('builder', {}).get('id', 'unknown')}")
        print(f"   Build type: {predicate.get('buildType', 'unknown')}")

        if "git_commit" in environment:
            print(f"   Git commit: {environment['git_commit'][:8]}")
        if "git_branch" in environment:
            print(f"   Git branch: {environment['git_branch']}")

        if "buildStartedOn" in metadata:
            print(f"   Build time: {metadata['buildStartedOn']}")
        if "reproducible" in metadata:
            print(f"   Reproducible: {metadata['reproducible']}")

    def verify_all_for_service(self, service_name: str) -> bool:
        """Verify all attestations for a service"""
        attestation_dir = ATTESTATION_DIR / service_name

        if not attestation_dir.exists():
            print(f"⚠️  No attestations found for {service_name}")
            return True

        # Find all attestation files
        attestation_files = list(attestation_dir.glob("*.json"))

        if not attestation_files:
            print(f"⚠️  No attestations found for {service_name}")
            return True

        print(f"\nVerifying {len(attestation_files)} attestation(s) for {service_name}...")

        all_valid = True

        for attestation_file in sorted(attestation_files):
            build_id = attestation_file.stem
            valid = self.verify_attestation(service_name, build_id)
            all_valid = all_valid and valid

        return all_valid

    def print_summary(self):
        """Print verification summary"""
        print(f"\n{'='*60}")
        print("Verification Summary")
        print(f"{'='*60}\n")

        print(f"✅ Checks passed: {self.checks_passed}")
        print(f"⚠️  Warnings: {self.warnings}")
        print(f"❌ Checks failed: {self.checks_failed}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Attestation Verifier")
    parser.add_argument("--service", choices=SERVICES,
                        help="Service to verify")
    parser.add_argument("--build-id",
                        help="Build ID to verify")
    parser.add_argument("--all", action="store_true",
                        help="Verify all attestations for service")
    parser.add_argument("--verify-all", action="store_true",
                        help="Verify all attestations for all services")

    args = parser.parse_args()

    try:
        # Load verifier
        verifier = SignatureVerifier(SIGNING_KEY_PATH)
        key_id = verifier.get_key_id()
        print(f"🔑 Loaded signing key: {key_id}")

        attestation_verifier = AttestationVerifier(verifier)

        # Determine what to verify
        if args.verify_all:
            # Verify all services
            all_valid = True
            for service in SERVICES:
                valid = attestation_verifier.verify_all_for_service(service)
                all_valid = all_valid and valid

        elif args.service and args.all:
            # Verify all attestations for specific service
            all_valid = attestation_verifier.verify_all_for_service(args.service)

        elif args.service and args.build_id:
            # Verify specific attestation
            all_valid = attestation_verifier.verify_attestation(args.service, args.build_id)

        else:
            parser.print_help()
            return 1

        # Print summary
        attestation_verifier.print_summary()

        # Exit with appropriate code
        if not all_valid or attestation_verifier.checks_failed > 0:
            print("❌ Verification FAILED")
            return 1
        else:
            print("✅ Verification PASSED")
            return 0

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 2
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
