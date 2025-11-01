#!/usr/bin/env python3
"""
SBOM (Software Bill of Materials) Generator

Generates CycloneDX-like JSON SBOMs for RiverCityClean services.

Features:
- Python dependency detection (via import scanning)
- Node.js dependency detection (via package.json)
- CycloneDX 1.5 JSON format
- SHA-256 checksums
- License information

Usage:
    # Generate SBOM for a single service
    python tools/sbom/generate.py --service crm_api

    # Generate SBOMs for all services
    python tools/sbom/generate.py --all

    # Validate existing SBOMs
    python tools/sbom/generate.py --validate
"""

import argparse
import json
import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional
import ast


REPO_ROOT = Path(__file__).parent.parent.parent
SBOM_DIR = REPO_ROOT / "sbom"

# Service configurations
SERVICES = {
    "crm_api": {
        "type": "python",
        "path": REPO_ROOT / "crm_api",
        "description": "CRM API Backend Service",
        "entry_points": ["app/main.py"]
    },
    "ops_api": {
        "type": "python",
        "path": REPO_ROOT / "ops_api",
        "description": "Operations API Backend Service",
        "entry_points": ["app/main.py"]
    },
    "crm": {
        "type": "nodejs",
        "path": REPO_ROOT / "crm",
        "description": "CRM Frontend Application",
        "package_json": "package.json"
    },
    "ops-console": {
        "type": "nodejs",
        "path": REPO_ROOT / "ops-console",
        "description": "Operations Console Frontend",
        "package_json": "package.json"
    }
}

# Known Python standard library modules (partial list)
STDLIB_MODULES = {
    "os", "sys", "re", "json", "time", "datetime", "pathlib", "typing",
    "collections", "itertools", "functools", "hashlib", "uuid", "logging",
    "argparse", "configparser", "enum", "dataclasses", "abc", "ast",
    "base64", "secrets", "hmac", "urllib", "http", "email", "xml"
}

# Known licenses for common packages
KNOWN_LICENSES = {
    # Python packages
    "fastapi": "MIT",
    "uvicorn": "BSD-3-Clause",
    "pydantic": "MIT",
    "sqlalchemy": "MIT",
    "alembic": "MIT",
    "redis": "MIT",
    "celery": "BSD-3-Clause",
    "structlog": "Apache-2.0",
    "pytest": "MIT",
    "psycopg2": "LGPL-3.0",
    "python-jose": "MIT",
    "passlib": "BSD-3-Clause",
    "bcrypt": "Apache-2.0",
    "cryptography": "Apache-2.0 OR BSD-3-Clause",

    # Node.js packages
    "react": "MIT",
    "react-dom": "MIT",
    "react-router-dom": "MIT",
    "axios": "MIT",
    "vite": "MIT",
    "typescript": "Apache-2.0",
    "tailwindcss": "MIT",
    "autoprefixer": "MIT",
    "postcss": "MIT",
    "vitest": "MIT",
    "@vitejs/plugin-react": "MIT",
    "@types/react": "MIT",
    "@types/react-dom": "MIT",
    "@testing-library/react": "MIT",
    "@testing-library/jest-dom": "MIT",
    "jsdom": "MIT"
}


class PythonDependencyScanner:
    """Scan Python source code for dependencies"""

    def __init__(self, service_path: Path):
        self.service_path = service_path
        self.dependencies: Set[str] = set()

    def scan(self) -> Set[str]:
        """Scan all Python files for imports"""
        python_files = list(self.service_path.rglob("*.py"))

        for py_file in python_files:
            # Skip test files and migration files
            if "test" in str(py_file) or "alembic" in str(py_file):
                continue

            self._scan_file(py_file)

        # Filter out stdlib modules
        external_deps = {dep for dep in self.dependencies if dep not in STDLIB_MODULES}

        return external_deps

    def _scan_file(self, filepath: Path):
        """Scan a single Python file for imports"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(filepath))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Get top-level package name
                        package = alias.name.split('.')[0]
                        self.dependencies.add(package)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Get top-level package name
                        package = node.module.split('.')[0]
                        self.dependencies.add(package)

        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"   ⚠️  Warning: Could not parse {filepath}: {e}")


class NodeJsDependencyScanner:
    """Scan Node.js package.json for dependencies"""

    def __init__(self, service_path: Path, package_json: str = "package.json"):
        self.service_path = service_path
        self.package_json = service_path / package_json

    def scan(self) -> Dict[str, str]:
        """Read dependencies from package.json"""
        if not self.package_json.exists():
            return {}

        with open(self.package_json, "r") as f:
            data = json.load(f)

        dependencies = {}

        # Runtime dependencies
        for name, version in data.get("dependencies", {}).items():
            dependencies[name] = self._normalize_version(version)

        # Dev dependencies (included in SBOM for completeness)
        for name, version in data.get("devDependencies", {}).items():
            dependencies[name] = self._normalize_version(version)

        return dependencies

    @staticmethod
    def _normalize_version(version: str) -> str:
        """Normalize npm version string"""
        # Remove ^ and ~ prefixes
        return version.lstrip("^~")


class SBOMGenerator:
    """Generate CycloneDX-like SBOM"""

    def __init__(self, service_name: str, service_config: Dict):
        self.service_name = service_name
        self.config = service_config
        self.service_path = service_config["path"]
        self.service_type = service_config["type"]

    def generate(self) -> Dict:
        """Generate SBOM for service"""
        print(f"\n{'='*60}")
        print(f"Generating SBOM for: {self.service_name}")
        print(f"Type: {self.service_type}")
        print(f"Path: {self.service_path}")
        print(f"{'='*60}\n")

        if self.service_type == "python":
            components = self._generate_python_components()
        elif self.service_type == "nodejs":
            components = self._generate_nodejs_components()
        else:
            raise ValueError(f"Unknown service type: {self.service_type}")

        # Build SBOM structure (CycloneDX 1.5)
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{self._generate_uuid()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "component": {
                    "type": "application",
                    "name": self.service_name,
                    "version": "1.0.0",
                    "description": self.config.get("description", ""),
                    "bom-ref": f"pkg:generic/{self.service_name}@1.0.0"
                },
                "tools": [
                    {
                        "name": "RiverCityClean SBOM Generator",
                        "version": "1.0.0",
                        "vendor": "RiverCityClean"
                    }
                ]
            },
            "components": components
        }

        print(f"✅ Generated SBOM with {len(components)} components\n")

        return sbom

    def _generate_python_components(self) -> List[Dict]:
        """Generate components for Python service"""
        scanner = PythonDependencyScanner(self.service_path)
        dependencies = scanner.scan()

        components = []

        for dep in sorted(dependencies):
            component = {
                "type": "library",
                "name": dep,
                "version": "unknown",  # Version detection would require pip freeze
                "purl": f"pkg:pypi/{dep}",
                "bom-ref": f"pkg:pypi/{dep}@unknown"
            }

            # Add license if known
            if dep in KNOWN_LICENSES:
                component["licenses"] = [
                    {"license": {"id": KNOWN_LICENSES[dep]}}
                ]

            components.append(component)
            print(f"   📦 {dep} (license: {KNOWN_LICENSES.get(dep, 'UNKNOWN')})")

        return components

    def _generate_nodejs_components(self) -> List[Dict]:
        """Generate components for Node.js service"""
        scanner = NodeJsDependencyScanner(self.service_path, self.config.get("package_json", "package.json"))
        dependencies = scanner.scan()

        components = []

        for name, version in sorted(dependencies.items()):
            component = {
                "type": "library",
                "name": name,
                "version": version,
                "purl": f"pkg:npm/{name}@{version}",
                "bom-ref": f"pkg:npm/{name}@{version}"
            }

            # Add license if known
            if name in KNOWN_LICENSES:
                component["licenses"] = [
                    {"license": {"id": KNOWN_LICENSES[name]}}
                ]

            components.append(component)
            print(f"   📦 {name}@{version} (license: {KNOWN_LICENSES.get(name, 'UNKNOWN')})")

        return components

    @staticmethod
    def _generate_uuid() -> str:
        """Generate a deterministic UUID for SBOM"""
        import uuid
        return str(uuid.uuid4())


def save_sbom(service_name: str, sbom: Dict):
    """Save SBOM to file"""
    service_sbom_dir = SBOM_DIR / service_name
    service_sbom_dir.mkdir(parents=True, exist_ok=True)

    sbom_file = service_sbom_dir / "sbom.json"

    with open(sbom_file, "w") as f:
        json.dump(sbom, f, indent=2)

    print(f"💾 Saved SBOM: {sbom_file}")

    # Generate SHA-256 checksum
    generate_checksums(service_name)


def generate_checksums(service_name: str):
    """Generate SHA-256 checksums for SBOM"""
    service_sbom_dir = SBOM_DIR / service_name
    sbom_file = service_sbom_dir / "sbom.json"
    checksum_file = service_sbom_dir / "SHA256SUMS"

    if not sbom_file.exists():
        print(f"   ⚠️  SBOM file not found: {sbom_file}")
        return

    # Calculate SHA-256
    sha256 = hashlib.sha256()
    with open(sbom_file, "rb") as f:
        sha256.update(f.read())

    checksum = sha256.hexdigest()

    # Write checksum file (format: <hash>  <filename>)
    with open(checksum_file, "w") as f:
        f.write(f"{checksum}  sbom.json\n")

    print(f"🔐 Generated checksum: {checksum_file}")
    print(f"   SHA256: {checksum}\n")


def validate_sboms() -> bool:
    """Validate all existing SBOMs"""
    print(f"\n{'='*60}")
    print("Validating SBOMs")
    print(f"{'='*60}\n")

    all_valid = True

    for service_name in SERVICES.keys():
        service_sbom_dir = SBOM_DIR / service_name
        sbom_file = service_sbom_dir / "sbom.json"
        checksum_file = service_sbom_dir / "SHA256SUMS"

        print(f"Validating {service_name}...")

        # Check SBOM exists
        if not sbom_file.exists():
            print(f"   ❌ SBOM missing: {sbom_file}")
            all_valid = False
            continue

        # Check checksum file exists
        if not checksum_file.exists():
            print(f"   ❌ Checksum file missing: {checksum_file}")
            all_valid = False
            continue

        # Validate checksum
        with open(checksum_file, "r") as f:
            expected_checksum = f.read().strip().split()[0]

        sha256 = hashlib.sha256()
        with open(sbom_file, "rb") as f:
            sha256.update(f.read())
        actual_checksum = sha256.hexdigest()

        if expected_checksum != actual_checksum:
            print(f"   ❌ Checksum mismatch!")
            print(f"      Expected: {expected_checksum}")
            print(f"      Actual:   {actual_checksum}")
            all_valid = False
            continue

        # Validate SBOM structure
        try:
            with open(sbom_file, "r") as f:
                sbom = json.load(f)

            # Check required fields
            if sbom.get("bomFormat") != "CycloneDX":
                print(f"   ❌ Invalid bomFormat: {sbom.get('bomFormat')}")
                all_valid = False
                continue

            if "components" not in sbom:
                print(f"   ❌ Missing components")
                all_valid = False
                continue

            component_count = len(sbom["components"])
            print(f"   ✅ Valid SBOM ({component_count} components, checksum OK)")

        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON: {e}")
            all_valid = False

    print()
    if all_valid:
        print("✅ All SBOMs valid")
    else:
        print("❌ Some SBOMs invalid or missing")

    return all_valid


def main():
    parser = argparse.ArgumentParser(description="SBOM Generator")
    parser.add_argument("--service", choices=list(SERVICES.keys()),
                        help="Service to generate SBOM for")
    parser.add_argument("--all", action="store_true",
                        help="Generate SBOMs for all services")
    parser.add_argument("--validate", action="store_true",
                        help="Validate existing SBOMs")

    args = parser.parse_args()

    # Ensure SBOM directory exists
    SBOM_DIR.mkdir(parents=True, exist_ok=True)

    # Validation mode
    if args.validate:
        valid = validate_sboms()
        return 0 if valid else 1

    # Generation mode
    if args.all:
        services_to_generate = list(SERVICES.keys())
    elif args.service:
        services_to_generate = [args.service]
    else:
        parser.print_help()
        return 1

    # Generate SBOMs
    for service_name in services_to_generate:
        try:
            config = SERVICES[service_name]
            generator = SBOMGenerator(service_name, config)
            sbom = generator.generate()
            save_sbom(service_name, sbom)
        except Exception as e:
            print(f"\n❌ Error generating SBOM for {service_name}: {e}")
            import traceback
            traceback.print_exc()
            return 1

    print(f"{'='*60}")
    print("✅ SBOM Generation Complete")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
