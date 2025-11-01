#!/usr/bin/env python3
"""
Detection Engine

Executes YAML detection rules against log files to identify security events.

Features:
- Load YAML detection rules
- Parse JSON Lines logs
- Execute detection logic (thresholds, conditions)
- Generate alerts
- Run test cases

Usage:
    # Run all detections on log file
    python scripts/observability/detect.py --log logs/crm_api.jsonl

    # Run specific detection
    python scripts/observability/detect.py --log logs/crm_api.jsonl --rule detections/brute_force.yaml

    # Test detection rules
    python scripts/observability/detect.py --test

    # Generate sample malicious logs for testing
    python scripts/observability/detect.py --generate-sample
"""

import argparse
import json
import sys
import yaml
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any


REPO_ROOT = Path(__file__).parent.parent.parent
DETECTIONS_DIR = REPO_ROOT / "detections"
LOGS_DIR = REPO_ROOT / "logs"


class DetectionRule:
    """Detection rule loaded from YAML"""

    def __init__(self, rule_path: Path):
        self.rule_path = rule_path

        with open(rule_path, 'r') as f:
            self.rule = yaml.safe_load(f)

        self.id = self.rule.get("id")
        self.name = self.rule.get("name")
        self.description = self.rule.get("description")
        self.severity = self.rule.get("severity")
        self.detection = self.rule.get("detection", {})
        self.alert = self.rule.get("alert", {})
        self.exclude = self.rule.get("exclude", [])

    def __repr__(self):
        return f"<DetectionRule {self.id}: {self.name}>"


class DetectionEngine:
    """Execute detection rules against logs"""

    def __init__(self):
        self.rules: List[DetectionRule] = []
        self.alerts: List[Dict] = []

    def load_rules(self, rules_dir: Path):
        """Load all detection rules from directory"""
        print(f"📋 Loading detection rules from {rules_dir}")

        for rule_file in sorted(rules_dir.glob("*.yaml")):
            try:
                rule = DetectionRule(rule_file)
                self.rules.append(rule)
                print(f"   ✅ Loaded: {rule.name} ({rule.id})")
            except Exception as e:
                print(f"   ❌ Failed to load {rule_file.name}: {e}")

        print(f"\n✅ Loaded {len(self.rules)} detection rule(s)\n")

    def load_logs(self, log_file: Path) -> List[Dict]:
        """Load JSON Lines log file"""
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return []

        logs = []

        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    log_entry = json.loads(line)
                    logs.append(log_entry)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Line {line_num}: Invalid JSON - {e}")

        print(f"📄 Loaded {len(logs)} log entries from {log_file.name}\n")

        return logs

    def get_nested_value(self, obj: Dict, field_path: str) -> Any:
        """Get nested field value using dot notation"""
        # First, try direct key (for flat dot-notation keys like "event.action")
        if field_path in obj:
            return obj[field_path]

        # Then try nested traversal (for nested objects like {"event": {"action": "..."}})
        parts = field_path.split('.')
        value = obj

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        return value

    def check_condition(self, log_entry: Dict, condition: Dict) -> bool:
        """Check if log entry matches a condition"""
        field = condition.get("field")
        operator = condition.get("operator")
        expected = condition.get("value")

        # Get actual value from log
        actual = self.get_nested_value(log_entry, field)

        # Apply operator
        if operator == "equals":
            return actual == expected
        elif operator == "in":
            if isinstance(expected, list):
                return actual in expected
            return False
        elif operator == "contains":
            if isinstance(actual, str) and isinstance(expected, str):
                return expected in actual
            if isinstance(expected, list):
                return any(exp in str(actual) for exp in expected)
            return False
        elif operator == "gt":
            return actual > expected if actual is not None else False
        elif operator == "gte":
            return actual >= expected if actual is not None else False
        elif operator == "lt":
            return actual < expected if actual is not None else False
        elif operator == "lte":
            return actual <= expected if actual is not None else False
        else:
            return False

    def should_exclude(self, log_entry: Dict, exclude_conditions: List[Dict]) -> bool:
        """Check if log entry should be excluded"""
        for exclude_cond in exclude_conditions:
            if self.check_condition(log_entry, exclude_cond):
                return True
        return False

    def execute_rule(self, rule: DetectionRule, logs: List[Dict]) -> List[Dict]:
        """
        Execute detection rule against logs.

        Returns:
            List of alerts
        """
        print(f"🔍 Executing rule: {rule.name}")

        detection = rule.detection
        conditions = detection.get("condition", [])
        threshold = detection.get("threshold", {})
        group_by = detection.get("group_by", [])
        timeframe_str = detection.get("timeframe", "1h")

        # Parse timeframe
        timeframe_seconds = self.parse_timeframe(timeframe_str)

        # Filter logs that match all conditions
        matching_logs = []

        for log_entry in logs:
            # Check exclude conditions
            if self.should_exclude(log_entry, rule.exclude):
                continue

            # Check all conditions
            all_match = True
            for condition in conditions:
                if not self.check_condition(log_entry, condition):
                    all_match = False
                    break

            if all_match:
                matching_logs.append(log_entry)

        print(f"   📊 {len(matching_logs)} logs matched conditions")

        # Group by specified fields
        if group_by:
            grouped = defaultdict(list)

            for log_entry in matching_logs:
                # Create group key
                group_values = []
                for field in group_by:
                    value = self.get_nested_value(log_entry, field)
                    group_values.append(str(value) if value is not None else "null")

                group_key = tuple(group_values)
                grouped[group_key].append(log_entry)

            print(f"   📊 Grouped into {len(grouped)} group(s)")

        else:
            # No grouping - treat all as one group
            grouped = {("all",): matching_logs}

        # Check threshold for each group
        alerts = []

        threshold_count = threshold.get("count", 1)
        threshold_operator = threshold.get("operator", "gte")

        for group_key, group_logs in grouped.items():
            # Apply timeframe filter
            if timeframe_seconds:
                group_logs = self.filter_by_timeframe(group_logs, timeframe_seconds)

            count = len(group_logs)

            # Check threshold
            triggered = False

            if threshold_operator == "gte":
                triggered = count >= threshold_count
            elif threshold_operator == "gt":
                triggered = count > threshold_count
            elif threshold_operator == "eq":
                triggered = count == threshold_count
            elif threshold_operator == "lt":
                triggered = count < threshold_count
            elif threshold_operator == "lte":
                triggered = count <= threshold_count

            if triggered:
                # Create alert
                alert = {
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "triggered_at": datetime.now(timezone.utc).isoformat(),
                    "group_by": dict(zip(group_by, group_key)),
                    "count": count,
                    "threshold": threshold_count,
                    "matching_logs": group_logs[:10],  # Include up to 10 sample logs
                    "alert_config": rule.alert
                }

                alerts.append(alert)

                print(f"   🚨 ALERT: {rule.name} - {count} events from {group_key}")

        return alerts

    def parse_timeframe(self, timeframe_str: str) -> int:
        """Parse timeframe string to seconds (e.g., '5m' -> 300)"""
        if not timeframe_str:
            return 0

        unit = timeframe_str[-1]
        value = int(timeframe_str[:-1])

        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        else:
            return 0

    def filter_by_timeframe(self, logs: List[Dict], timeframe_seconds: int) -> List[Dict]:
        """Filter logs to include only those within timeframe"""
        if not timeframe_seconds:
            return logs

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeframe_seconds)

        filtered = []

        for log_entry in logs:
            timestamp_str = log_entry.get("@timestamp")

            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

                    if timestamp >= cutoff:
                        filtered.append(log_entry)
                except ValueError:
                    # Skip if timestamp can't be parsed
                    pass

        return filtered

    def run_detection(self, logs: List[Dict]) -> List[Dict]:
        """Run all detection rules against logs"""
        all_alerts = []

        print(f"{'='*70}")
        print(f"Running Detections")
        print(f"{'='*70}\n")

        for rule in self.rules:
            alerts = self.execute_rule(rule, logs)
            all_alerts.extend(alerts)
            print()

        return all_alerts

    def print_alerts(self, alerts: List[Dict]):
        """Print alerts in readable format"""
        if not alerts:
            print(f"✅ No alerts triggered\n")
            return

        print(f"{'='*70}")
        print(f"🚨 Alerts ({len(alerts)})")
        print(f"{'='*70}\n")

        for alert in alerts:
            severity_emoji = {"low": "ℹ️", "medium": "⚠️", "high": "🔴", "critical": "🚨"}
            emoji = severity_emoji.get(alert["severity"], "🔔")

            print(f"{emoji} {alert['rule_name']} ({alert['severity'].upper()})")
            print(f"   Rule ID: {alert['rule_id']}")
            print(f"   Count: {alert['count']} (threshold: {alert['threshold']})")

            if alert.get("group_by"):
                print(f"   Group: {alert['group_by']}")

            print(f"   Triggered: {alert['triggered_at']}")
            print()

    def test_rule(self, rule: DetectionRule) -> bool:
        """Test detection rule using built-in test cases"""
        print(f"\n{'='*70}")
        print(f"Testing Rule: {rule.name}")
        print(f"{'='*70}\n")

        test_cases = rule.rule.get("test_cases", [])

        if not test_cases:
            print(f"⚠️  No test cases defined for {rule.name}\n")
            return True

        all_passed = True

        for test_case in test_cases:
            test_name = test_case.get("name")
            test_input = test_case.get("input", [])
            expected_result = test_case.get("expected", False)

            print(f"Running test: {test_name}")

            # Execute rule on test input
            alerts = self.execute_rule(rule, test_input)

            # Check result
            actual_result = len(alerts) > 0

            if actual_result == expected_result:
                print(f"   ✅ PASS\n")
            else:
                print(f"   ❌ FAIL")
                print(f"      Expected: {expected_result}")
                print(f"      Actual: {actual_result}\n")
                all_passed = False

        return all_passed


def generate_sample_logs():
    """Generate sample logs for testing detections"""
    print(f"\n{'='*70}")
    print(f"Generating Sample Logs")
    print(f"{'='*70}\n")

    sample_file = LOGS_DIR / "sample_malicious.jsonl"
    sample_file.parent.mkdir(parents=True, exist_ok=True)

    # Generate brute force attack logs
    brute_force_logs = []
    base_time = datetime.now(timezone.utc)

    for i in range(8):
        log_entry = {
            "@timestamp": (base_time + timedelta(seconds=i * 30)).isoformat(),
            "log.level": "WARNING",
            "message": "Login failed",
            "event.action": "auth.login.failure",
            "http.response.status_code": 401,
            "client.ip": "203.0.113.100",
            "user.name": "admin",
        }
        brute_force_logs.append(log_entry)

    # Generate excessive 403 logs
    excessive_403_logs = []

    for i in range(15):
        log_entry = {
            "@timestamp": (base_time + timedelta(minutes=5, seconds=i * 20)).isoformat(),
            "log.level": "WARNING",
            "message": "Forbidden access attempt",
            "event.action": "access.denied",
            "http.response.status_code": 403,
            "http.request.path": f"/admin/endpoint_{i}",
            "client.ip": "198.51.100.50",
            "user.id": "user_malicious",
        }
        excessive_403_logs.append(log_entry)

    # Write to file
    all_logs = brute_force_logs + excessive_403_logs

    with open(sample_file, 'w') as f:
        for log_entry in all_logs:
            f.write(json.dumps(log_entry) + '\n')

    print(f"✅ Generated {len(all_logs)} sample logs")
    print(f"   💾 Saved to {sample_file}")
    print(f"   📊 {len(brute_force_logs)} brute force events")
    print(f"   📊 {len(excessive_403_logs)} excessive 403 events\n")

    return sample_file


def main():
    parser = argparse.ArgumentParser(description="Detection Engine")
    parser.add_argument("--log", type=Path,
                        help="Log file to analyze")
    parser.add_argument("--rule", type=Path,
                        help="Specific detection rule to run")
    parser.add_argument("--test", action="store_true",
                        help="Test detection rules")
    parser.add_argument("--generate-sample", action="store_true",
                        help="Generate sample malicious logs")
    parser.add_argument("--detections-dir", type=Path, default=DETECTIONS_DIR,
                        help="Directory containing detection rules")

    args = parser.parse_args()

    # Create detection engine
    engine = DetectionEngine()

    # Generate sample logs mode
    if args.generate_sample:
        sample_file = generate_sample_logs()
        print(f"Run detections with: python {sys.argv[0]} --log {sample_file}\n")
        return 0

    # Load rules
    if args.rule:
        # Load single rule
        rule = DetectionRule(args.rule)
        engine.rules = [rule]
    else:
        # Load all rules
        engine.load_rules(args.detections_dir)

    # Test mode
    if args.test:
        print(f"\n{'='*70}")
        print(f"Testing Detection Rules")
        print(f"{'='*70}")

        all_passed = True

        for rule in engine.rules:
            passed = engine.test_rule(rule)
            all_passed = all_passed and passed

        if all_passed:
            print(f"\n✅ All tests passed\n")
            return 0
        else:
            print(f"\n❌ Some tests failed\n")
            return 1

    # Detection mode
    if not args.log:
        print(f"❌ Error: --log required for detection mode\n")
        parser.print_help()
        return 1

    # Load logs
    logs = engine.load_logs(args.log)

    if not logs:
        print(f"❌ No logs to analyze\n")
        return 1

    # Run detections
    alerts = engine.run_detection(logs)

    # Print alerts
    engine.print_alerts(alerts)

    # Exit code based on alerts
    if alerts:
        return 1  # Exit with error if alerts triggered
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
