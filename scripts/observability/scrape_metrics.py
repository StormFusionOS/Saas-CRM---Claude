#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Metrics Scraper

Scrapes Prometheus-style metrics from /metrics endpoints and saves snapshots.

Features:
- Scrape multiple service endpoints
- Save timestamped snapshots
- JSON and Prometheus text format export
- Local file storage

Usage:
    # Scrape all configured services
    python scripts/observability/scrape_metrics.py

    # Scrape specific service
    python scripts/observability/scrape_metrics.py --service crm_api

    # Continuous scraping (every 60 seconds)
    python scripts/observability/scrape_metrics.py --continuous --interval 60
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError


REPO_ROOT = Path(__file__).parent.parent.parent
METRICS_DIR = REPO_ROOT / "artifacts" / "metrics"

# Service endpoints
SERVICES = {
    "crm_api": "http://localhost:8000/metrics",
    "ops_api": "http://localhost:8001/metrics",
}


class MetricsScraper:
    """Scrape and store Prometheus metrics"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self, service_name: str, endpoint: str) -> Optional[str]:
        """
        Scrape metrics from endpoint.

        Args:
            service_name: Service name
            endpoint: Metrics endpoint URL

        Returns:
            Metrics text or None if failed
        """
        print(f"📊 Scraping {service_name} from {endpoint}")

        try:
            request = Request(endpoint)
            request.add_header("User-Agent", "MetricsScraper/1.0")

            with urlopen(request, timeout=10) as response:
                metrics_text = response.read().decode('utf-8')

            print(f"   ✅ Scraped {len(metrics_text)} bytes")
            return metrics_text

        except URLError as e:
            print(f"   ❌ Failed to scrape: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None

    def save_snapshot(self, service_name: str, metrics_text: str) -> Path:
        """
        Save metrics snapshot to file.

        Args:
            service_name: Service name
            metrics_text: Metrics in Prometheus text format

        Returns:
            Path to saved file
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"{service_name}-{timestamp}.txt"
        filepath = self.output_dir / service_name / filename

        # Create service directory
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Save metrics
        with open(filepath, "w") as f:
            f.write(metrics_text)

        print(f"   💾 Saved to {filepath}")

        return filepath

    def parse_metrics(self, metrics_text: str) -> List[Dict]:
        """
        Parse Prometheus text format to structured data.

        Args:
            metrics_text: Metrics in Prometheus text format

        Returns:
            List of metric dictionaries
        """
        metrics = []
        current_metric = None

        for line in metrics_text.split('\n'):
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # HELP line
            if line.startswith('# HELP'):
                parts = line.split(' ', 3)
                if len(parts) >= 4:
                    current_metric = {
                        "name": parts[2],
                        "help": parts[3],
                        "type": "untyped",
                        "samples": []
                    }

            # TYPE line
            elif line.startswith('# TYPE'):
                parts = line.split(' ', 3)
                if len(parts) >= 4 and current_metric:
                    current_metric["type"] = parts[3]

            # Sample line
            elif not line.startswith('#') and current_metric:
                # Parse: metric_name{labels} value
                if '{' in line:
                    metric_part, rest = line.split('{', 1)
                    labels_part, value_part = rest.rsplit('}', 1)

                    # Parse labels
                    labels = {}
                    for label in labels_part.split(','):
                        if '=' in label:
                            key, val = label.split('=', 1)
                            labels[key.strip()] = val.strip(' "')

                    value = float(value_part.strip())

                else:
                    metric_part, value_part = line.split(None, 1)
                    labels = {}
                    value = float(value_part)

                current_metric["samples"].append({
                    "labels": labels,
                    "value": value
                })

                # If this completes a metric, add to list
                if line and not line.startswith('#'):
                    # Check if next line is a different metric
                    metrics.append(current_metric)

        return metrics

    def save_json(self, service_name: str, metrics: List[Dict]) -> Path:
        """
        Save metrics as JSON.

        Args:
            service_name: Service name
            metrics: Parsed metrics

        Returns:
            Path to saved file
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"{service_name}-{timestamp}.json"
        filepath = self.output_dir / service_name / filename

        # Create service directory
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service_name,
            "metrics": metrics
        }

        # Save JSON
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)

        print(f"   💾 Saved JSON to {filepath}")

        return filepath

    def scrape_all(self, services: Dict[str, str]) -> Dict[str, Optional[str]]:
        """
        Scrape all configured services.

        Args:
            services: Dictionary of service_name -> endpoint

        Returns:
            Dictionary of service_name -> metrics_text
        """
        results = {}

        print(f"\n{'='*60}")
        print(f"Scraping metrics from {len(services)} service(s)")
        print(f"{'='*60}\n")

        for service_name, endpoint in services.items():
            metrics_text = self.scrape(service_name, endpoint)
            results[service_name] = metrics_text

            if metrics_text:
                # Save snapshot
                self.save_snapshot(service_name, metrics_text)

                # Parse and save as JSON
                metrics = self.parse_metrics(metrics_text)
                self.save_json(service_name, metrics)

            print()

        return results

    def continuous_scrape(self, services: Dict[str, str], interval: int):
        """
        Continuously scrape metrics at interval.

        Args:
            services: Dictionary of service_name -> endpoint
            interval: Scrape interval in seconds
        """
        print(f"🔄 Starting continuous scraping (interval: {interval}s)")
        print(f"Press Ctrl+C to stop\n")

        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"{'='*60}")
                print(f"Scrape iteration #{iteration}")
                print(f"{'='*60}")

                self.scrape_all(services)

                print(f"⏱️  Sleeping for {interval} seconds...\n")
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n⏹️  Stopped continuous scraping")


def list_snapshots(output_dir: Path):
    """List all saved snapshots"""
    print(f"\n{'='*60}")
    print(f"Metrics Snapshots")
    print(f"{'='*60}\n")

    for service_dir in sorted(output_dir.iterdir()):
        if service_dir.is_dir():
            print(f"📁 {service_dir.name}/")

            txt_files = sorted(service_dir.glob("*.txt"), reverse=True)
            json_files = sorted(service_dir.glob("*.json"), reverse=True)

            if txt_files:
                print(f"   Latest TXT: {txt_files[0].name}")
            if json_files:
                print(f"   Latest JSON: {json_files[0].name}")

            print(f"   Total: {len(txt_files)} TXT, {len(json_files)} JSON\n")


def main():
    parser = argparse.ArgumentParser(description="Metrics Scraper")
    parser.add_argument("--service", choices=list(SERVICES.keys()),
                        help="Scrape specific service only")
    parser.add_argument("--continuous", action="store_true",
                        help="Continuously scrape at interval")
    parser.add_argument("--interval", type=int, default=60,
                        help="Scrape interval in seconds (default: 60)")
    parser.add_argument("--list", action="store_true",
                        help="List all saved snapshots")
    parser.add_argument("--output-dir", type=Path, default=METRICS_DIR,
                        help="Output directory for snapshots")

    args = parser.parse_args()

    # Create scraper
    scraper = MetricsScraper(args.output_dir)

    # List mode
    if args.list:
        list_snapshots(args.output_dir)
        return 0

    # Determine services to scrape
    if args.service:
        services = {args.service: SERVICES[args.service]}
    else:
        services = SERVICES

    # Scrape
    if args.continuous:
        scraper.continuous_scrape(services, args.interval)
    else:
        scraper.scrape_all(services)

    print(f"{'='*60}")
    print(f"✅ Scraping complete")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
