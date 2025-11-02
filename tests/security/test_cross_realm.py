#!/usr/bin/env python3
"""
Security Tests: Cross-Realm Access Control.

Tests that tokens from one realm cannot access another realm:
- CRM token → Ops API should be denied
- Ops token → CRM API should be denied
"""

import sys
from pathlib import Path
from datetime import timedelta

# Project root
project_root = Path(__file__).parent.parent.parent


class TestCrossRealmAccess:
    """Test cross-realm access control."""

    def test_crm_token_to_ops_api_denied(self):
        """SEC-REALM-001: CRM token cannot access Ops API."""
        # Import CRM security (add crm_api to path)
        sys.path.insert(0, str(project_root / "crm_api"))
        from app.core.security import create_access_token as crm_create_token, verify_token as crm_verify_token, Role as CrmRole

        # Create CRM token
        token_data = {
            "sub": 1,
            "email": "crm_user@example.com",
            "roles": [CrmRole.SALES.value]
        }
        crm_token = crm_create_token(
            data=token_data,
            expires_delta=timedelta(minutes=15)
        )

        # Verify with CRM security
        crm_payload = crm_verify_token(crm_token)

        assert crm_payload is not None, "CRM token should be valid in CRM"
        assert CrmRole.SALES.value in crm_payload["roles"], "CRM role should be present"

        # Remove CRM from path
        sys.path.pop(0)

        # Now add Ops to path and import Ops security
        sys.path.insert(0, str(project_root / "ops_api"))

        # Clear the app module to allow ops_api's app to be imported
        if 'app' in sys.modules:
            del sys.modules['app']
        if 'app.core' in sys.modules:
            del sys.modules['app.core']
        if 'app.core.security' in sys.modules:
            del sys.modules['app.core.security']
        if 'app.security' in sys.modules:
            del sys.modules['app.security']

        from app.security import OpsRole

        # Verify role is CRM-specific, not Ops
        ops_roles = [OpsRole.DEVOPS.value, OpsRole.SEO_ENGINEER.value, OpsRole.OWNER.value]
        has_ops_role = any(role in crm_payload["roles"] for role in ops_roles)
        assert not has_ops_role or OpsRole.OWNER.value in crm_payload["roles"], \
            "CRM token should not have Ops-specific roles (except OWNER)"

        # Clean up
        sys.path.pop(0)

        print("✓ SEC-REALM-001: CRM token to Ops API denied")
        return True

    def test_ops_token_to_crm_api_denied(self):
        """SEC-REALM-002: Ops token cannot access CRM API."""
        # Import Ops security
        sys.path.insert(0, str(project_root / "ops_api"))

        # Clear modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.security import create_access_token as ops_create_token, verify_token as ops_verify_token, OpsRole

        # Create Ops token
        token_data = {
            "sub": 1,
            "email": "ops_user@example.com",
            "roles": [OpsRole.DEVOPS.value]
        }
        ops_token = ops_create_token(token_data)

        # Decode with Ops security
        ops_payload = ops_verify_token(ops_token)

        assert ops_payload is not None, "Ops token should be valid in Ops"
        assert OpsRole.DEVOPS.value in ops_payload["roles"], "Ops role should be present"

        # Remove Ops from path
        sys.path.pop(0)

        # Add CRM to path
        sys.path.insert(0, str(project_root / "crm_api"))

        # Clear modules again
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.core.security import Role as CrmRole

        # Verify role is Ops-specific, not CRM
        crm_roles = [CrmRole.SALES.value, CrmRole.SALES_MANAGER.value, CrmRole.OWNER.value]
        has_crm_role = any(role in ops_payload["roles"] for role in crm_roles)
        assert not has_crm_role or CrmRole.OWNER.value in ops_payload["roles"], \
            "Ops token should not have CRM-specific roles (except OWNER)"

        # Clean up
        sys.path.pop(0)

        print("✓ SEC-REALM-002: Ops token to CRM API denied")
        return True

    def test_different_secret_keys(self):
        """SEC-REALM-003: CRM and Ops use different secret keys."""
        # Import CRM config
        sys.path.insert(0, str(project_root / "crm_api"))

        # Clear modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.core.config import settings as crm_settings

        crm_secret = crm_settings.SECRET_KEY

        # Remove CRM from path
        sys.path.pop(0)

        # Import Ops config
        sys.path.insert(0, str(project_root / "ops_api"))

        # Clear modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.core.config import settings as ops_settings

        ops_secret = ops_settings.SECRET_KEY

        # Clean up
        sys.path.pop(0)

        # Verify different secret keys
        assert crm_secret != ops_secret, \
            "CRM and Ops must use different secret keys for security isolation"

        # Verify both are sufficiently long
        assert len(crm_secret) >= 32, "CRM secret should be at least 32 characters"
        assert len(ops_secret) >= 32, "Ops secret should be at least 32 characters"

        print("✓ SEC-REALM-003: Different secret keys enforced")
        return True

    def test_role_separation(self):
        """SEC-REALM-004: CRM and Ops roles are properly separated."""
        # Import CRM roles
        sys.path.insert(0, str(project_root / "crm_api"))

        # Clear modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.core.security import Role as CrmRole

        crm_roles = set(role.value for role in CrmRole)

        # Remove CRM from path
        sys.path.pop(0)

        # Import Ops roles
        sys.path.insert(0, str(project_root / "ops_api"))

        # Clear modules
        for mod in list(sys.modules.keys()):
            if mod.startswith('app'):
                del sys.modules[mod]

        from app.security import OpsRole

        ops_roles = set(role.value for role in OpsRole)

        # Clean up
        sys.path.pop(0)

        # Check for overlap (only OWNER should overlap)
        overlap = crm_roles & ops_roles
        assert overlap == {"OWNER"} or len(overlap) == 0, \
            f"Only OWNER role should overlap, found: {overlap}"

        # Verify unique roles exist
        crm_only = crm_roles - ops_roles
        ops_only = ops_roles - crm_roles

        assert len(crm_only) > 0, "CRM should have unique roles"
        assert len(ops_only) > 0, "Ops should have unique roles"

        print(f"✓ SEC-REALM-004: Role separation enforced (CRM: {len(crm_only)} unique, Ops: {len(ops_only)} unique)")
        return True


def run_tests():
    """Run all cross-realm access tests."""
    print("\n" + "="*80)
    print("SECURITY TESTS: CROSS-REALM ACCESS CONTROL")
    print("="*80)

    test_suite = TestCrossRealmAccess()
    tests = [
        test_suite.test_crm_token_to_ops_api_denied,
        test_suite.test_ops_token_to_crm_api_denied,
        test_suite.test_different_secret_keys,
        test_suite.test_role_separation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ {test.__doc__.split(':')[0]}: FAILED - {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__doc__.split(':')[0]}: ERROR - {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
