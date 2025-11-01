#!/usr/bin/env python3
"""
SIEM Log Export Script

Rolls application logs into timestamped gzip archives for SIEM ingestion.

Features:
- Roll logs into time-based archives (hourly/daily)
- Compress with gzip
- Preserve JSON Lines format
- Export to artifacts/logs/ directory
- Support for multiple log sources

Usage:
    # Export all logs
    python scripts/observability/export_logs.py

    # Export specific service logs
    python scripts/observability/export_logs.py --service crm_api

    # Export with custom time range
    python scripts/observability/export_logs.py --hours 24

    # Watch and export continuously
    python scripts/observability/export_logs.py --watch --interval 3600
"""

import argparse
import gzip
import json
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional


REPO_ROOT = Path(__file__).parent.parent.parent
LOGS_DIR = REPO_ROOT / "logs"
EXPORT_DIR = REPO_ROOT / "artifacts" / "logs"

# Log files to export
LOG_FILES = {
    "crm_api": LOGS_DIR / "crm_api.jsonl",
    "ops_api": LOGS_DIR / "ops_api.jsonl",
    "celery": LOGS_DIR / "celery.jsonl",
    "nginx": LOGS_DIR / "nginx.jsonl",
}


class LogExporter:
    """Export and archive logs for SIEM"""

    def __init__(self, export_dir: Path):
        self.export_dir = export_dir
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def filter_logs_by_time(self, log_file: Path, hours: Optional[int] = None) -> List[str]:
        """
        Filter log entries by time.

        Args:
            log_file: Path to log file
            hours: Number of hours to include (None = all)

        Returns:
            List of log lines
        """
        if not log_file.exists():
            return []

        # Calculate cutoff time
        if hours:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        else:
            cutoff = None

        filtered_lines = []

        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse JSON to get timestamp
                try:
                    log_entry = json.loads(line)
                    timestamp_str = log_entry.get("@timestamp")

                    if timestamp_str and cutoff:
                        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                        # Skip if older than cutoff
                        if timestamp < cutoff:
                            continue

                    filtered_lines.append(line)

                except json.JSONDecodeError:
                    # Include non-JSON lines as-is
                    filtered_lines.append(line)

        return filtered_lines

    def export_service(self, service_name: str, log_file: Path, hours: Optional[int] = None) -> Optional[Path]:
        """
        Export logs for a service.

        Args:
            service_name: Service name
            log_file: Path to log file
            hours: Hours to include (None = all)

        Returns:
            Path to exported file or None
        """
        print(f"📦 Exporting {service_name} logs...")

        # Filter logs
        log_lines = self.filter_logs_by_time(log_file, hours)

        if not log_lines:
            print(f"   ⚠️  No logs found for {service_name}")
            return None

        # Create export filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        filename = f"{service_name}-{timestamp}.jsonl.gz"

        # Create service export directory
        service_export_dir = self.export_dir / service_name
        service_export_dir.mkdir(parents=True, exist_ok=True)

        export_path = service_export_dir / filename

        # Write gzipped logs
        with gzip.open(export_path, 'wt', encoding='utf-8') as f:
            for line in log_lines:
                f.write(line + '\n')

        print(f"   ✅ Exported {len(log_lines)} log entries")
        print(f"   💾 Saved to {export_path}")

        # Print file size
        size_kb = export_path.stat().st_size / 1024
        print(f"   📊 Size: {size_kb:.2f} KB (compressed)")

        return export_path

    def export_all(self, services: dict, hours: Optional[int] = None) -> dict:
        """
        Export logs for all services.

        Args:
            services: Dictionary of service_name -> log_file
            hours: Hours to include (None = all)

        Returns:
            Dictionary of service_name -> export_path
        """
        print(f"\n{'='*60}")
        print(f"Log Export")
        print(f"{'='*60}\n")

        if hours:
            print(f"⏱️  Exporting last {hours} hours of logs\n")
        else:
            print(f"⏱️  Exporting all logs\n")

        results = {}

        for service_name, log_file in services.items():
            export_path = self.export_service(service_name, log_file, hours)
            results[service_name] = export_path
            print()

        return results

    def rotate_old_exports(self, service_name: str, keep_count: int = 10):
        """
        Delete old exports, keeping only recent ones.

        Args:
            service_name: Service name
            keep_count: Number of recent exports to keep
        """
        service_export_dir = self.export_dir / service_name

        if not service_export_dir.exists():
            return

        # Get all export files
        export_files = sorted(service_export_dir.glob("*.jsonl.gz"), reverse=True)

        # Delete old exports
        if len(export_files) > keep_count:
            old_exports = export_files[keep_count:]

            print(f"🗑️  Rotating old {service_name} exports...")

            for old_file in old_exports:
                print(f"   Deleting {old_file.name}")
                old_file.unlink()

            print(f"   ✅ Kept {keep_count} most recent exports\n")

    def list_exports(self):
        """List all exported log files"""
        print(f"\n{'='*60}")
        print(f"Exported Logs")
        print(f"{'='*60}\n")

        for service_dir in sorted(self.export_dir.iterdir()):
            if service_dir.is_dir():
                print(f"📁 {service_dir.name}/")

                export_files = sorted(service_dir.glob("*.jsonl.gz"), reverse=True)

                for export_file in export_files[:5]:  # Show last 5
                    size_kb = export_file.stat().st_size / 1024
                    print(f"   • {export_file.name} ({size_kb:.2f} KB)")

                if len(export_files) > 5:
                    print(f"   ... and {len(export_files) - 5} more")

                print()

    def watch_and_export(self, services: dict, interval: int, hours: int):
        """
        Watch logs and export at intervals.

        Args:
            services: Dictionary of service_name -> log_file
            interval: Export interval in seconds
            hours: Hours of logs to include
        """
        print(f"👀 Watching logs for export...")
        print(f"⏱️  Export interval: {interval} seconds")
        print(f"📊 Including last {hours} hours of logs")
        print(f"Press Ctrl+C to stop\n")

        try:
            iteration = 0
            while True:
                iteration += 1
                print(f"{'='*60}")
                print(f"Export iteration #{iteration}")
                print(f"{'='*60}")

                self.export_all(services, hours)

                # Rotate old exports
                for service_name in services.keys():
                    self.rotate_old_exports(service_name, keep_count=10)

                print(f"⏱️  Sleeping for {interval} seconds...\n")
                time.sleep(interval)

        except KeyboardInterrupt:
            print(f"\n\n⏹️  Stopped watching logs")


def create_manifest(export_dir: Path):
    """Create manifest of all exported logs"""
    manifest_path = export_dir / "manifest.json"

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "exports": {}
    }

    for service_dir in sorted(export_dir.iterdir()):
        if service_dir.is_dir():
            service_name = service_dir.name
            export_files = sorted(service_dir.glob("*.jsonl.gz"))

            manifest["exports"][service_name] = [
                {
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "created_at": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
                }
                for f in export_files
            ]

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"📋 Created manifest: {manifest_path}\n")


def main():
    parser = argparse.ArgumentParser(description="SIEM Log Export")
    parser.add_argument("--service", choices=list(LOG_FILES.keys()),
                        help="Export specific service only")
    parser.add_argument("--hours", type=int,
                        help="Export last N hours of logs (default: all)")
    parser.add_argument("--watch", action="store_true",
                        help="Continuously watch and export")
    parser.add_argument("--interval", type=int, default=3600,
                        help="Export interval in seconds (default: 3600)")
    parser.add_argument("--list", action="store_true",
                        help="List all exported logs")
    parser.add_argument("--rotate", action="store_true",
                        help="Rotate old exports")
    parser.add_argument("--export-dir", type=Path, default=EXPORT_DIR,
                        help="Export directory")

    args = parser.parse_args()

    # Create exporter
    exporter = LogExporter(args.export_dir)

    # List mode
    if args.list:
        exporter.list_exports()
        return 0

    # Rotate mode
    if args.rotate:
        for service_name in LOG_FILES.keys():
            exporter.rotate_old_exports(service_name, keep_count=10)
        return 0

    # Determine services to export
    if args.service:
        services = {args.service: LOG_FILES[args.service]}
    else:
        services = LOG_FILES

    # Export
    if args.watch:
        exporter.watch_and_export(services, args.interval, args.hours or 1)
    else:
        exporter.export_all(services, args.hours)

        # Create manifest
        create_manifest(args.export_dir)

    print(f"{'='*60}")
    print(f"✅ Export complete")
    print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
