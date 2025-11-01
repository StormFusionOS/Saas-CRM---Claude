# ==============================================================================
# ACCESS CONTROL POLICY (OPA-Style)
# ==============================================================================
# This file defines attribute-based access control (ABAC) policies for the
# RiverCityClean SaaS monorepo.
#
# Policy Structure:
# - Default deny (explicit allow required)
# - Separation of Duties (SoD): CRM and Ops roles cannot be combined
# - Environment scoping: production access requires approval
# - Data domain restrictions
# - Break-glass override with dual approval
#
# ==============================================================================

package rivercityclean.access

# ==============================================================================
# DEFAULT DENY
# ==============================================================================

default allow = false

# ==============================================================================
# ROLE DEFINITIONS
# ==============================================================================

# CRM Roles
crm_roles = ["SALES", "SALES_MANAGER"]

# Ops Roles
ops_roles = ["SEO_ENGINEER", "DEVOPS"]

# Universal Role
owner_role = "OWNER"

# ==============================================================================
# SEPARATION OF DUTIES (SoD)
# ==============================================================================

# Check if user has roles from both CRM and Ops (forbidden except OWNER)
has_crm_role {
    some role
    role = input.user.roles[_]
    role == crm_roles[_]
}

has_ops_role {
    some role
    role = input.user.roles[_]
    role == ops_roles[_]
}

is_owner {
    some role
    role = input.user.roles[_]
    role == owner_role
}

# SoD violation: has both CRM and Ops roles (unless OWNER)
sod_violation {
    has_crm_role
    has_ops_role
    not is_owner
}

# ==============================================================================
# ENVIRONMENT SCOPING
# ==============================================================================

# Environment hierarchy
environment_levels = {
    "development": 1,
    "staging": 2,
    "production": 3
}

# Check if user's environment clearance allows access
environment_allowed {
    # User environment level
    user_level := environment_levels[input.user.environment]

    # Resource environment level
    resource_level := environment_levels[input.resource.environment]

    # User must have equal or higher clearance
    user_level >= resource_level
}

# Production access requires explicit approval (unless OWNER)
production_access_requires_approval {
    input.resource.environment == "production"
    not is_owner
    not input.user.break_glass_approved
}

# ==============================================================================
# DATA DOMAIN RESTRICTIONS
# ==============================================================================

# CRM data domains
crm_data_domains = ["customer_data", "lead_data", "sales_data"]

# Ops data domains
ops_data_domains = ["infrastructure", "monitoring", "security"]

# Check if user can access data domain
data_domain_allowed {
    # CRM users can only access CRM domains
    has_crm_role
    input.resource.data_domain == crm_data_domains[_]
}

data_domain_allowed {
    # Ops users can only access Ops domains
    has_ops_role
    input.resource.data_domain == ops_data_domains[_]
}

data_domain_allowed {
    # OWNER can access all domains
    is_owner
}

# ==============================================================================
# DEPARTMENT RESTRICTIONS
# ==============================================================================

# User can access resources from their own department or public resources
department_allowed {
    input.user.department == input.resource.department
}

department_allowed {
    input.resource.department == "public"
}

department_allowed {
    # OWNER bypasses department restrictions
    is_owner
}

# ==============================================================================
# BREAK-GLASS OVERRIDE
# ==============================================================================

# Break-glass access requires dual approval
break_glass_valid {
    input.user.break_glass_approved
    count(input.user.break_glass_approvers) >= 2

    # Check approval is not expired
    time.now_ns() < input.user.break_glass_expires_at
}

# ==============================================================================
# MAIN ALLOW RULES
# ==============================================================================

# Allow if OWNER role (universal access)
allow {
    is_owner
    not sod_violation
}

# Allow if all conditions met (non-OWNER)
allow {
    not is_owner
    not sod_violation
    environment_allowed
    not production_access_requires_approval
    data_domain_allowed
    department_allowed
}

# Allow if break-glass is active and valid
allow {
    break_glass_valid
    not sod_violation
}

# ==============================================================================
# DENY REASONS (for debugging/auditing)
# ==============================================================================

deny_reason = "Separation of Duties violation: user has both CRM and Ops roles" {
    sod_violation
}

deny_reason = "Environment clearance insufficient" {
    not environment_allowed
}

deny_reason = "Production access requires approval" {
    production_access_requires_approval
}

deny_reason = "Data domain not allowed for user role" {
    not data_domain_allowed
}

deny_reason = "Department mismatch" {
    not department_allowed
}

deny_reason = "Default deny: no matching allow rule" {
    not allow
}
