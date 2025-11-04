#!/usr/bin/env python3
"""
Test script to trigger SEO Meta Optimizer job
This will create test data visible in the governance dashboard
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.jobs.seo_meta_job import run_seo_meta_optimization


async def main():
    """Run SEO Meta Optimizer job to create test data."""

    print("=" * 70)
    print("SEO META OPTIMIZER - TEST RUN")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Analyze 2 WordPress pages (mock data)")
    print("  2. Generate optimized meta tags using AI")
    print("  3. Create change log entries (status: pending)")
    print("  4. Create task log entry")
    print()
    print("Results will be visible in the governance dashboard at:")
    print("  http://localhost:5174/governance")
    print()
    print("Starting job...")
    print("-" * 70)
    print()

    # Run the job
    result = await run_seo_meta_optimization(
        limit=2,  # Analyze 2 pages
        triggered_by="manual_test_script"
    )

    print()
    print("-" * 70)
    print("JOB COMPLETED!")
    print("=" * 70)
    print()
    print(f"Job ID: {result['job_id']}")
    print(f"Status: {result['status']}")
    print(f"Pages Processed: {result.get('pages_processed', 0)}")
    print(f"Changes Generated: {result.get('changes_generated', 0)}")
    print(f"Errors: {result.get('errors_count', 0)}")
    print()

    if result['status'] == 'completed' and result.get('changes_generated', 0) > 0:
        print("✓ SUCCESS! Change log entries created.")
        print()
        print("View results in dashboard:")
        print("  → Review Queue Widget: http://localhost:5174/governance")
        print("  → Full Review Queue: http://localhost:5174/governance/review-queue")
        print()
        print("The dashboard auto-refreshes every 30 seconds, or refresh manually.")
    elif result['status'] == 'failed':
        print(f"✗ FAILED: {result.get('error', 'Unknown error')}")
    else:
        print("✓ Job completed but no changes generated.")

    print()
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
