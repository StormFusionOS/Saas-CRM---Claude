#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
OpenAPI Spec Generator

Generates OpenAPI/Swagger specifications from FastAPI applications.

Usage:
    python scripts/api/generate_openapi.py --service crm
    python scripts/api/generate_openapi.py --service ops
    python scripts/api/generate_openapi.py --all
"""

import argparse
import json
import sys
from pathlib import Path
import yaml


def generate_crm_openapi():
    """Generate OpenAPI spec for CRM API."""
    try:
        # Import the FastAPI app
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "crm_api"))
        from app.main import create_app

        app = create_app()
        openapi_schema = app.openapi()

        # Enhance with additional metadata
        openapi_schema["info"]["description"] = """
        CRM API for RiverCityClean SaaS platform.

        This API provides endpoints for:
        - Authentication and authorization
        - Lead management
        - Contact management
        - Webhook integrations (Facebook, Twilio, Google)
        - Scheduled tasks

        **Base URL**: `/api/v1`

        **Authentication**: Bearer token (JWT)

        **Rate Limiting**: 100 requests per minute per client
        """

        openapi_schema["info"]["contact"] = {
            "name": "RiverCityClean API Support",
            "email": "api@rivercityclean.com"
        }

        openapi_schema["info"]["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }

        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.rivercityclean.com",
                "description": "Production server"
            }
        ]

        return openapi_schema

    except Exception as e:
        print(f"Error generating CRM OpenAPI spec: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_ops_openapi():
    """Generate OpenAPI spec for Ops Console API."""
    try:
        # Import the FastAPI app
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ops_api"))
        from app.main import create_app

        app = create_app()
        openapi_schema = app.openapi()

        # Enhance with additional metadata
        openapi_schema["info"]["description"] = """
        Operations Console API for RiverCityClean SaaS platform.

        This API provides endpoints for:
        - System health monitoring
        - Service status checks
        - Alert management
        - Database health
        - Admin operations

        **Base URL**: `/api/ops`

        **Authentication**: Bearer token (JWT) with ops role

        **Rate Limiting**: 100 requests per minute per client
        """

        openapi_schema["info"]["contact"] = {
            "name": "RiverCityClean API Support",
            "email": "api@rivercityclean.com"
        }

        openapi_schema["info"]["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }

        openapi_schema["servers"] = [
            {
                "url": "http://localhost:8001",
                "description": "Development server"
            },
            {
                "url": "https://ops.rivercityclean.com",
                "description": "Production server"
            }
        ]

        return openapi_schema

    except Exception as e:
        print(f"Error generating Ops OpenAPI spec: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_spec(spec, output_path: Path, format: str = "yaml"):
    """Save OpenAPI spec to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "yaml":
        with open(output_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
    else:  # json
        with open(output_path, 'w') as f:
            json.dump(spec, f, indent=2)

    print(f"✓ Generated OpenAPI spec: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate OpenAPI specifications from FastAPI apps'
    )
    parser.add_argument(
        '--service',
        choices=['crm', 'ops'],
        help='Service to generate spec for'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate specs for all services'
    )
    parser.add_argument(
        '--format',
        choices=['yaml', 'json'],
        default='yaml',
        help='Output format (default: yaml)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='docs/api',
        help='Output directory (default: docs/api)'
    )

    args = parser.parse_args()

    if not args.service and not args.all:
        parser.error('Either --service or --all must be specified')

    output_dir = Path(args.output_dir)
    extension = 'yaml' if args.format == 'yaml' else 'json'

    print("="*80)
    print("OpenAPI Spec Generation")
    print("="*80)

    success_count = 0
    total_count = 0

    # Generate CRM spec
    if args.service == 'crm' or args.all:
        total_count += 1
        print(f"\n[1/{'2' if args.all else '1'}] Generating CRM API spec...")
        crm_spec = generate_crm_openapi()
        if crm_spec:
            save_spec(crm_spec, output_dir / f"crm.{extension}", args.format)
            success_count += 1
        else:
            print("✗ Failed to generate CRM API spec")

    # Generate Ops spec
    if args.service == 'ops' or args.all:
        total_count += 1
        print(f"\n[{'2' if args.all else '1'}/{'2' if args.all else '1'}] Generating Ops Console API spec...")
        ops_spec = generate_ops_openapi()
        if ops_spec:
            save_spec(ops_spec, output_dir / f"ops.{extension}", args.format)
            success_count += 1
        else:
            print("✗ Failed to generate Ops Console API spec")

    print("\n" + "="*80)
    print(f"Summary: {success_count}/{total_count} specs generated successfully")
    print("="*80)

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())
