"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Policy Engine - OPA-Style Policy Evaluator

This module provides a Python-based policy evaluator that interprets
OPA-style Rego policies for RBAC/ABAC decisions.

Features:
- Deny-by-default
- Separation of Duties (SoD) enforcement
- Environment scoping
- Data domain restrictions
- Department-based access control
- Break-glass override with dual approval

Usage:
    from policy.policy_engine import PolicyEngine

    engine = PolicyEngine()

    decision = engine.evaluate(
        user={
            "roles": ["SALES"],
            "department": "sales",
            "environment": "development"
        },
        resource={
            "environment": "production",
            "data_domain": "customer_data",
            "department": "sales"
        }
    )

    if decision.allowed:
        # Grant access
    else:
        # Deny access, log reason
        print(decision.deny_reason)
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import time


# Role definitions
CRM_ROLES = {"SALES", "SALES_MANAGER"}
OPS_ROLES = {"SEO_ENGINEER", "DEVOPS"}
OWNER_ROLE = "OWNER"

# Data domain definitions
CRM_DATA_DOMAINS = {"customer_data", "lead_data", "sales_data"}
OPS_DATA_DOMAINS = {"infrastructure", "monitoring", "security"}

# Environment hierarchy
ENVIRONMENT_LEVELS = {
    "development": 1,
    "staging": 2,
    "production": 3
}


@dataclass
class PolicyDecision:
    """Result of a policy evaluation"""
    allowed: bool
    deny_reason: Optional[str] = None
    evaluated_at: float = None

    def __post_init__(self):
        if self.evaluated_at is None:
            self.evaluated_at = time.time()


class PolicyEngine:
    """
    ABAC Policy Engine

    Evaluates access control policies based on user and resource attributes.
    Implements deny-by-default with explicit allow rules.
    """

    def __init__(self):
        self.default_allow = False  # Deny by default

    def evaluate(
        self,
        user: Dict[str, Any],
        resource: Dict[str, Any],
        action: str = "access"
    ) -> PolicyDecision:
        """
        Evaluate if user can access resource

        Args:
            user: User attributes (roles, department, environment, etc.)
            resource: Resource attributes (environment, data_domain, department)
            action: Action being performed (default: "access")

        Returns:
            PolicyDecision with allow/deny and reason
        """
        # Check Separation of Duties
        if self._has_sod_violation(user):
            return PolicyDecision(
                allowed=False,
                deny_reason="Separation of Duties violation: user has both CRM and Ops roles"
            )

        # Check if user is OWNER (universal access, but still enforce SoD)
        if self._is_owner(user):
            return PolicyDecision(allowed=True)

        # Check break-glass override
        if self._is_break_glass_valid(user):
            return PolicyDecision(allowed=True)

        # Environment scoping
        if not self._is_environment_allowed(user, resource):
            return PolicyDecision(
                allowed=False,
                deny_reason=f"Environment clearance insufficient: user '{user.get('environment')}' cannot access '{resource.get('environment')}'"
            )

        # Production access requires approval (unless OWNER or break-glass)
        if self._production_requires_approval(user, resource):
            return PolicyDecision(
                allowed=False,
                deny_reason="Production access requires break-glass approval"
            )

        # Data domain restrictions
        if not self._is_data_domain_allowed(user, resource):
            user_roles = user.get("roles", [])
            return PolicyDecision(
                allowed=False,
                deny_reason=f"Data domain not allowed: roles {user_roles} cannot access '{resource.get('data_domain')}'"
            )

        # Department restrictions
        if not self._is_department_allowed(user, resource):
            return PolicyDecision(
                allowed=False,
                deny_reason=f"Department mismatch: user '{user.get('department')}' cannot access '{resource.get('department')}' resource"
            )

        # All checks passed
        return PolicyDecision(allowed=True)

    def _has_crm_role(self, user: Dict[str, Any]) -> bool:
        """Check if user has any CRM role"""
        user_roles = set(user.get("roles", []))
        return bool(user_roles & CRM_ROLES)

    def _has_ops_role(self, user: Dict[str, Any]) -> bool:
        """Check if user has any Ops role"""
        user_roles = set(user.get("roles", []))
        return bool(user_roles & OPS_ROLES)

    def _is_owner(self, user: Dict[str, Any]) -> bool:
        """Check if user has OWNER role"""
        return OWNER_ROLE in user.get("roles", [])

    def _has_sod_violation(self, user: Dict[str, Any]) -> bool:
        """
        Check Separation of Duties violation

        User cannot have both CRM and Ops roles (unless OWNER).
        OWNER role is allowed to have both for break-glass scenarios.
        """
        if self._is_owner(user):
            return False  # OWNER can have both

        return self._has_crm_role(user) and self._has_ops_role(user)

    def _is_environment_allowed(
        self,
        user: Dict[str, Any],
        resource: Dict[str, Any]
    ) -> bool:
        """
        Check if user's environment clearance allows access

        Users can only access resources in their environment level or below.
        Example: staging user can access development and staging, but not production.
        """
        user_env = user.get("environment", "development")
        resource_env = resource.get("environment", "development")

        user_level = ENVIRONMENT_LEVELS.get(user_env, 1)
        resource_level = ENVIRONMENT_LEVELS.get(resource_env, 1)

        return user_level >= resource_level

    def _production_requires_approval(
        self,
        user: Dict[str, Any],
        resource: Dict[str, Any]
    ) -> bool:
        """
        Check if production access requires approval

        Production resources require break-glass approval (unless OWNER).
        """
        if self._is_owner(user):
            return False  # OWNER doesn't need approval

        if resource.get("environment") == "production":
            return not user.get("break_glass_approved", False)

        return False

    def _is_data_domain_allowed(
        self,
        user: Dict[str, Any],
        resource: Dict[str, Any]
    ) -> bool:
        """
        Check if user can access data domain

        CRM users can only access CRM data domains.
        Ops users can only access Ops data domains.
        OWNER can access all domains.
        """
        if self._is_owner(user):
            return True

        resource_domain = resource.get("data_domain")
        if not resource_domain:
            return True  # No domain restriction

        # Check CRM roles
        if self._has_crm_role(user):
            return resource_domain in CRM_DATA_DOMAINS

        # Check Ops roles
        if self._has_ops_role(user):
            return resource_domain in OPS_DATA_DOMAINS

        return False

    def _is_department_allowed(
        self,
        user: Dict[str, Any],
        resource: Dict[str, Any]
    ) -> bool:
        """
        Check if user can access resource from department

        Users can access their own department or public resources.
        OWNER can access all departments.
        """
        if self._is_owner(user):
            return True

        resource_dept = resource.get("department")
        if not resource_dept or resource_dept == "public":
            return True  # Public resources

        user_dept = user.get("department")
        return user_dept == resource_dept

    def _is_break_glass_valid(self, user: Dict[str, Any]) -> bool:
        """
        Check if break-glass override is valid

        Requires:
        - break_glass_approved flag
        - At least 2 approvers
        - Not expired
        """
        if not user.get("break_glass_approved"):
            return False

        # Check dual approval
        approvers = user.get("break_glass_approvers", [])
        if len(approvers) < 2:
            return False

        # Check expiration
        expires_at = user.get("break_glass_expires_at", 0)
        now = time.time()
        if now >= expires_at:
            return False

        return True


# Convenience functions

def check_access(
    user: Dict[str, Any],
    resource: Dict[str, Any],
    action: str = "access"
) -> PolicyDecision:
    """
    Convenience function to check access

    Usage:
        from policy.policy_engine import check_access

        decision = check_access(
            user={"roles": ["SALES"], "department": "sales"},
            resource={"data_domain": "customer_data", "department": "sales"}
        )
    """
    engine = PolicyEngine()
    return engine.evaluate(user, resource, action)


def enforce_sod(roles: List[str]) -> None:
    """
    Enforce Separation of Duties on a role list

    Raises:
        ValueError: If SoD violation detected
    """
    roles_set = set(roles)

    # Check if user has both CRM and Ops roles
    has_crm = bool(roles_set & CRM_ROLES)
    has_ops = bool(roles_set & OPS_ROLES)

    if has_crm and has_ops and OWNER_ROLE not in roles_set:
        raise ValueError(
            "Separation of Duties violation: cannot combine CRM and Ops roles without OWNER"
        )
