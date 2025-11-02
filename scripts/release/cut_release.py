#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
Release Management Script

Automates the release process:
- Bumps version numbers in all relevant files
- Generates CHANGELOG.md entries from git commits
- Creates git tags
- Updates VERSION file
- Generates release notes

Usage:
    # Cut a new release (auto-detect version bump)
    python scripts/release/cut_release.py

    # Cut specific version
    python scripts/release/cut_release.py 1.2.3

    # Dry run (no changes)
    python scripts/release/cut_release.py --dry-run

    # Specify bump type
    python scripts/release/cut_release.py --bump major
    python scripts/release/cut_release.py --bump minor
    python scripts/release/cut_release.py --bump patch

    # Generate changelog only
    python scripts/release/cut_release.py --changelog-only

Version Format: MAJOR.MINOR.PATCH (Semantic Versioning 2.0.0)
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ==============================================================================
# Configuration
# ==============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
VERSION_FILE = PROJECT_ROOT / "VERSION"
CHANGELOG_FILE = PROJECT_ROOT / "CHANGELOG.md"
PACKAGE_JSON = PROJECT_ROOT / "frontend" / "package.json"
PYPROJECT_TOML = PROJECT_ROOT / "pyproject.toml"


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class Version:
    """Semantic version representation"""
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """Parse version string (e.g., '1.2.3' or 'v1.2.3')"""
        version_str = version_str.lstrip("v")
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3))
        )

    def bump(self, part: str) -> "Version":
        """Return new version with specified part bumped"""
        if part == "major":
            return Version(self.major + 1, 0, 0)
        elif part == "minor":
            return Version(self.major, self.minor + 1, 0)
        elif part == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        else:
            raise ValueError(f"Invalid bump part: {part}")


@dataclass
class Commit:
    """Git commit information"""
    hash: str
    type: str
    scope: str
    subject: str
    body: str
    breaking: bool = False


@dataclass
class ChangelogEntry:
    """Changelog section entry"""
    version: str
    date: str
    added: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    fixed: List[str] = field(default_factory=list)
    security: List[str] = field(default_factory=list)
    deprecated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    breaking: List[str] = field(default_factory=list)


# ==============================================================================
# Git Operations
# ==============================================================================

def run_command(cmd: List[str], cwd: Path = PROJECT_ROOT) -> str:
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}", file=sys.stderr)
        print(f"   Error: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_current_version() -> Version:
    """Get current version from VERSION file or git tags"""
    # Try VERSION file first
    if VERSION_FILE.exists():
        version_str = VERSION_FILE.read_text().strip()
        return Version.parse(version_str)

    # Fallback to latest git tag
    try:
        latest_tag = run_command(["git", "describe", "--tags", "--abbrev=0"])
        return Version.parse(latest_tag)
    except SystemExit:
        # No tags found, start at 0.1.0
        return Version(0, 1, 0)


def get_commits_since_last_tag() -> List[Commit]:
    """Get commits since last release tag"""
    try:
        last_tag = run_command(["git", "describe", "--tags", "--abbrev=0"])
        commit_range = f"{last_tag}..HEAD"
    except SystemExit:
        # No tags, get all commits
        commit_range = "HEAD"

    # Get commit log with format: hash|subject
    log_output = run_command([
        "git", "log", commit_range,
        "--format=%H|%s",
        "--no-merges"
    ])

    if not log_output:
        return []

    commits = []
    for line in log_output.split("\n"):
        if not line:
            continue

        hash_part, subject = line.split("|", 1)
        commit = parse_conventional_commit(hash_part, subject)
        commits.append(commit)

    return commits


def parse_conventional_commit(commit_hash: str, subject: str) -> Commit:
    """Parse commit message in Conventional Commits format"""
    # Pattern: type(scope): subject
    # or: type: subject
    pattern = r"^(\w+)(?:\(([^)]+)\))?:\s*(.+)$"
    match = re.match(pattern, subject)

    if match:
        commit_type = match.group(1)
        scope = match.group(2) or ""
        subject_text = match.group(3)
    else:
        # Not conventional format, default to "chore"
        commit_type = "chore"
        scope = ""
        subject_text = subject

    # Check for breaking change
    breaking = "BREAKING CHANGE" in subject or subject_text.startswith("!")

    return Commit(
        hash=commit_hash,
        type=commit_type,
        scope=scope,
        subject=subject_text,
        body="",
        breaking=breaking
    )


def create_git_tag(version: Version, dry_run: bool = False):
    """Create annotated git tag for release"""
    tag_name = f"v{version}"
    tag_message = f"Release {version}"

    if dry_run:
        print(f"[DRY RUN] Would create tag: {tag_name}")
        return

    run_command(["git", "tag", "-a", tag_name, "-m", tag_message])
    print(f"✅ Created git tag: {tag_name}")


# ==============================================================================
# Version Bumping
# ==============================================================================

def determine_bump_type(commits: List[Commit]) -> str:
    """Determine version bump type from commits"""
    has_breaking = any(c.breaking for c in commits)
    has_feat = any(c.type == "feat" for c in commits)
    has_fix = any(c.type == "fix" for c in commits)

    if has_breaking:
        return "major"
    elif has_feat:
        return "minor"
    elif has_fix:
        return "patch"
    else:
        # Default to patch for other changes
        return "patch"


def update_version_file(version: Version, dry_run: bool = False):
    """Update VERSION file"""
    if dry_run:
        print(f"[DRY RUN] Would update VERSION file to: {version}")
        return

    VERSION_FILE.write_text(f"{version}\n")
    print(f"✅ Updated VERSION file: {version}")


def update_package_json(version: Version, dry_run: bool = False):
    """Update frontend package.json version"""
    if not PACKAGE_JSON.exists():
        return

    if dry_run:
        print(f"[DRY RUN] Would update package.json to: {version}")
        return

    with PACKAGE_JSON.open() as f:
        package_data = json.load(f)

    package_data["version"] = str(version)

    with PACKAGE_JSON.open("w") as f:
        json.dump(package_data, f, indent=2)
        f.write("\n")

    print(f"✅ Updated package.json: {version}")


def update_pyproject_toml(version: Version, dry_run: bool = False):
    """Update Python pyproject.toml version"""
    if not PYPROJECT_TOML.exists():
        return

    if dry_run:
        print(f"[DRY RUN] Would update pyproject.toml to: {version}")
        return

    content = PYPROJECT_TOML.read_text()

    # Update version line
    new_content = re.sub(
        r'^version\s*=\s*"[^"]+"',
        f'version = "{version}"',
        content,
        flags=re.MULTILINE
    )

    PYPROJECT_TOML.write_text(new_content)
    print(f"✅ Updated pyproject.toml: {version}")


# ==============================================================================
# Changelog Generation
# ==============================================================================

def generate_changelog_entry(version: Version, commits: List[Commit]) -> ChangelogEntry:
    """Generate changelog entry from commits"""
    entry = ChangelogEntry(
        version=str(version),
        date=datetime.now().strftime("%Y-%m-%d")
    )

    for commit in commits:
        message = commit.subject

        # Categorize by commit type
        if commit.type == "feat":
            entry.added.append(message)
        elif commit.type == "fix":
            entry.fixed.append(message)
        elif commit.type == "security" or "security" in message.lower():
            entry.security.append(message)
        elif commit.type == "refactor" or commit.type == "perf":
            entry.changed.append(message)
        elif commit.type == "deprecate":
            entry.deprecated.append(message)
        elif "remove" in commit.type or "delete" in commit.type:
            entry.removed.append(message)

        # Track breaking changes separately
        if commit.breaking:
            entry.breaking.append(message)

    return entry


def format_changelog_entry(entry: ChangelogEntry) -> str:
    """Format changelog entry as markdown"""
    lines = [
        f"## [v{entry.version}] - {entry.date}",
        ""
    ]

    # Breaking changes first (most important)
    if entry.breaking:
        lines.append("### ⚠️ BREAKING CHANGES")
        lines.append("")
        for item in entry.breaking:
            lines.append(f"- {item}")
        lines.append("")

    # Added features
    if entry.added:
        lines.append("### Added")
        lines.append("")
        for item in entry.added:
            lines.append(f"- {item}")
        lines.append("")

    # Changed functionality
    if entry.changed:
        lines.append("### Changed")
        lines.append("")
        for item in entry.changed:
            lines.append(f"- {item}")
        lines.append("")

    # Fixed bugs
    if entry.fixed:
        lines.append("### Fixed")
        lines.append("")
        for item in entry.fixed:
            lines.append(f"- {item}")
        lines.append("")

    # Security fixes
    if entry.security:
        lines.append("### Security")
        lines.append("")
        for item in entry.security:
            lines.append(f"- {item}")
        lines.append("")

    # Deprecated features
    if entry.deprecated:
        lines.append("### Deprecated")
        lines.append("")
        for item in entry.deprecated:
            lines.append(f"- {item}")
        lines.append("")

    # Removed features
    if entry.removed:
        lines.append("### Removed")
        lines.append("")
        for item in entry.removed:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def update_changelog(entry: ChangelogEntry, dry_run: bool = False):
    """Update CHANGELOG.md with new entry"""
    entry_text = format_changelog_entry(entry)

    if dry_run:
        print(f"[DRY RUN] Would add to CHANGELOG.md:\n{entry_text}")
        return

    # Read existing changelog or create header
    if CHANGELOG_FILE.exists():
        existing_content = CHANGELOG_FILE.read_text()
    else:
        existing_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\nThe format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),\nand this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).\n\n"

    # Insert new entry after header
    lines = existing_content.split("\n")
    insert_index = 0

    # Find where to insert (after header, before first ## entry)
    for i, line in enumerate(lines):
        if line.startswith("## "):
            insert_index = i
            break

    if insert_index == 0:
        # No existing entries, append to end
        new_content = existing_content + "\n" + entry_text + "\n"
    else:
        # Insert before first entry
        new_content = "\n".join(lines[:insert_index]) + "\n" + entry_text + "\n\n" + "\n".join(lines[insert_index:])

    CHANGELOG_FILE.write_text(new_content)
    print(f"✅ Updated CHANGELOG.md with v{entry.version}")


# ==============================================================================
# Release Notes
# ==============================================================================

def generate_release_notes(version: Version, entry: ChangelogEntry) -> str:
    """Generate release notes for GitHub/communication"""
    lines = [
        f"# Release v{version}",
        "",
        f"**Release Date:** {entry.date}",
        "",
        "## Summary",
        "",
        f"This release includes {len(entry.added)} new features, {len(entry.fixed)} bug fixes, and {len(entry.security)} security improvements.",
        ""
    ]

    # Add changelog content
    lines.append(format_changelog_entry(entry))

    return "\n".join(lines)


# ==============================================================================
# Main Release Process
# ==============================================================================

def cut_release(
    version: Optional[Version] = None,
    bump_type: Optional[str] = None,
    dry_run: bool = False,
    changelog_only: bool = False
):
    """Execute release process"""

    print("=" * 70)
    print("Release Management Script")
    print("=" * 70)
    print()

    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Get commits since last tag
    commits = get_commits_since_last_tag()
    print(f"Commits since last release: {len(commits)}")

    if len(commits) == 0 and not version:
        print("⚠️  No commits since last release. Nothing to release.")
        return

    # Determine new version
    if version:
        new_version = version
    elif bump_type:
        new_version = current_version.bump(bump_type)
    else:
        # Auto-detect bump type from commits
        auto_bump = determine_bump_type(commits)
        new_version = current_version.bump(auto_bump)
        print(f"Auto-detected bump type: {auto_bump}")

    print(f"New version: {new_version}")
    print()

    # Generate changelog entry
    print("📝 Generating changelog entry...")
    changelog_entry = generate_changelog_entry(new_version, commits)

    # Update changelog
    update_changelog(changelog_entry, dry_run=dry_run)

    if changelog_only:
        print("\n✅ Changelog updated. Exiting (changelog-only mode).")
        return

    # Update version files
    print("\n📦 Updating version files...")
    update_version_file(new_version, dry_run=dry_run)
    update_package_json(new_version, dry_run=dry_run)
    update_pyproject_toml(new_version, dry_run=dry_run)

    # Create git tag
    print("\n🏷️  Creating git tag...")
    create_git_tag(new_version, dry_run=dry_run)

    # Generate release notes
    print("\n📄 Generating release notes...")
    release_notes = generate_release_notes(new_version, changelog_entry)

    release_notes_file = PROJECT_ROOT / f"RELEASE_NOTES_v{new_version}.md"
    if not dry_run:
        release_notes_file.write_text(release_notes)
        print(f"✅ Release notes: {release_notes_file}")
    else:
        print(f"[DRY RUN] Would write release notes to: {release_notes_file}")

    # Summary
    print("\n" + "=" * 70)
    print(f"✅ Release v{new_version} prepared successfully!")
    print("=" * 70)

    if not dry_run:
        print("\n📋 Next steps:")
        print(f"   1. Review CHANGELOG.md and {release_notes_file.name}")
        print("   2. Commit changes: git add VERSION CHANGELOG.md package.json pyproject.toml")
        print(f"   3. Commit: git commit -m 'chore: Release v{new_version}'")
        print(f"   4. Push tag: git push origin v{new_version}")
        print("   5. Push branch: git push origin main")
        print("   6. Deploy to production")
    else:
        print("\n[DRY RUN] No changes were made. Run without --dry-run to execute.")


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Cut a new release",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect version bump from commits
  python scripts/release/cut_release.py

  # Specify version explicitly
  python scripts/release/cut_release.py 1.2.3

  # Specify bump type
  python scripts/release/cut_release.py --bump major
  python scripts/release/cut_release.py --bump minor
  python scripts/release/cut_release.py --bump patch

  # Dry run
  python scripts/release/cut_release.py --dry-run

  # Update changelog only
  python scripts/release/cut_release.py --changelog-only
        """
    )

    parser.add_argument(
        "version",
        nargs="?",
        help="Explicit version number (e.g., 1.2.3)"
    )

    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="Version bump type (auto-detected if not specified)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - show what would be done without making changes"
    )

    parser.add_argument(
        "--changelog-only",
        action="store_true",
        help="Only update changelog, don't bump version or create tag"
    )

    args = parser.parse_args()

    # Parse version if provided
    version = None
    if args.version:
        try:
            version = Version.parse(args.version)
        except ValueError as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Execute release
    cut_release(
        version=version,
        bump_type=args.bump,
        dry_run=args.dry_run,
        changelog_only=args.changelog_only
    )


if __name__ == "__main__":
    main()
