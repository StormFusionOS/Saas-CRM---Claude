#!/usr/bin/env python3
"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""

"""
License Header Verification Script

Verifies that all applicable source files contain proper license headers.
Skips migrations, third-party code, generated files, and test fixtures.

Usage:
    python scripts/policy/headers_check.py [OPTIONS]

Options:
    --fix         Add missing headers automatically
    --verbose     Show detailed output
    --check-only  Exit with code 1 if headers are missing (CI mode)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# ==============================================================================
# Configuration
# ==============================================================================

# License header templates for different file types
PYTHON_HEADER = '''"""
Copyright (c) 2025 RiverCityClean
SPDX-License-Identifier: MIT

This file is part of the RiverCityClean SaaS CRM system.
"""
'''

TYPESCRIPT_HEADER = '''/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */
'''

SHELL_HEADER = '''#!/usr/bin/env bash
# Copyright (c) 2025 RiverCityClean
# SPDX-License-Identifier: MIT
#
# This file is part of the RiverCityClean SaaS CRM system.
'''

SQL_HEADER = '''-- Copyright (c) 2025 RiverCityClean
-- SPDX-License-Identifier: MIT
--
-- This file is part of the RiverCityClean SaaS CRM system.
'''

# File extensions that require headers
FILE_EXTENSIONS = {
    '.py': PYTHON_HEADER,
    '.ts': TYPESCRIPT_HEADER,
    '.tsx': TYPESCRIPT_HEADER,
    '.js': TYPESCRIPT_HEADER,
    '.jsx': TYPESCRIPT_HEADER,
    '.sh': SHELL_HEADER,
    '.sql': SQL_HEADER,
}

# Directories to skip (third-party, generated, etc.)
SKIP_DIRS = {
    'node_modules',
    '__pycache__',
    '.git',
    '.venv',
    'venv',
    'env',
    'dist',
    'build',
    'coverage',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'migrations',  # Database migrations
    'alembic',     # Alembic migrations
    '.vitest',
    'vendor',
    'third_party',
}

# File patterns to skip
SKIP_PATTERNS = [
    r'\.min\.(js|css)$',           # Minified files
    r'\.bundle\.(js|css)$',        # Bundled files
    r'\.generated\.',              # Generated files
    r'\.test\.(ts|tsx|js|jsx)$',  # Test files (optional: remove if you want headers in tests)
    r'\.spec\.(ts|tsx|js|jsx)$',  # Spec files
    r'__init__\.py$',              # Python package init files (often empty)
    r'conftest\.py$',              # Pytest config
    r'setup\.py$',                 # Python setup files
    r'manage\.py$',                # Django management
]

# Files to always skip (by name)
SKIP_FILES = {
    '.gitignore',
    '.gitattributes',
    '.editorconfig',
    '.env.example',
    'package-lock.json',
    'yarn.lock',
    'pnpm-lock.yaml',
    'poetry.lock',
    'Pipfile.lock',
    'requirements.txt',
    'requirements-dev.txt',
    'README.md',
    'LICENSE',
    'CHANGELOG.md',
    'CONTRIBUTING.md',
}

# ==============================================================================
# Helper Functions
# ==============================================================================

def should_skip_file(file_path: Path) -> Tuple[bool, str]:
    """
    Determine if a file should be skipped.

    Returns:
        (should_skip, reason)
    """
    # Check if in skip directory
    for part in file_path.parts:
        if part in SKIP_DIRS:
            return True, f"in skip directory: {part}"

    # Check filename
    if file_path.name in SKIP_FILES:
        return True, f"in skip files list"

    # Check patterns
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, str(file_path)):
            return True, f"matches skip pattern: {pattern}"

    # Check if supported extension
    if file_path.suffix not in FILE_EXTENSIONS:
        return True, f"unsupported extension: {file_path.suffix}"

    return False, ""


def has_header(file_path: Path, verbose: bool = False) -> bool:
    """
    Check if file has a license header.

    Looks for copyright notice or SPDX identifier in first 20 lines.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read first 20 lines
            lines = [f.readline() for _ in range(20)]
            content = ''.join(lines)

            # Check for copyright or SPDX
            has_copyright = 'Copyright' in content or 'copyright' in content
            has_spdx = 'SPDX-License-Identifier' in content

            if verbose and not (has_copyright or has_spdx):
                print(f"  Missing header indicators in {file_path}")

            return has_copyright or has_spdx

    except UnicodeDecodeError:
        if verbose:
            print(f"  Skipping binary file: {file_path}")
        return True  # Skip binary files
    except Exception as e:
        if verbose:
            print(f"  Error reading {file_path}: {e}")
        return True  # Assume OK if can't read


def add_header(file_path: Path, verbose: bool = False) -> bool:
    """
    Add license header to file.

    Returns:
        True if header was added, False otherwise
    """
    ext = file_path.suffix
    if ext not in FILE_EXTENSIONS:
        return False

    header = FILE_EXTENSIONS[ext]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Check if file starts with shebang
        if original_content.startswith('#!'):
            lines = original_content.split('\n', 1)
            shebang = lines[0] + '\n'
            rest = lines[1] if len(lines) > 1 else ''

            # For shell files, header already includes shebang
            if ext == '.sh':
                new_content = header.lstrip() + '\n' + rest
            else:
                new_content = shebang + header + '\n' + rest
        else:
            new_content = header + '\n' + original_content

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        if verbose:
            print(f"  ✓ Added header to {file_path}")

        return True

    except Exception as e:
        print(f"  ✗ Error adding header to {file_path}: {e}")
        return False


def scan_directory(root_dir: Path, verbose: bool = False) -> Tuple[List[Path], List[Path]]:
    """
    Scan directory for files and categorize by header presence.

    Returns:
        (files_with_headers, files_without_headers)
    """
    files_with_headers = []
    files_without_headers = []
    total_scanned = 0
    total_skipped = 0

    for file_path in root_dir.rglob('*'):
        if not file_path.is_file():
            continue

        # Check if should skip
        should_skip, reason = should_skip_file(file_path)
        if should_skip:
            if verbose:
                print(f"⊘ Skip: {file_path.relative_to(root_dir)} ({reason})")
            total_skipped += 1
            continue

        total_scanned += 1

        # Check for header
        if has_header(file_path, verbose):
            files_with_headers.append(file_path)
            if verbose:
                print(f"✓ OK:   {file_path.relative_to(root_dir)}")
        else:
            files_without_headers.append(file_path)
            if verbose:
                print(f"✗ MISS: {file_path.relative_to(root_dir)}")

    if verbose:
        print(f"\nScanned: {total_scanned} files")
        print(f"Skipped: {total_skipped} files")

    return files_with_headers, files_without_headers


# ==============================================================================
# Main Function
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Verify license headers in source files'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Add missing headers automatically'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Exit with code 1 if headers are missing (CI mode)'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to scan (default: current directory)'
    )

    args = parser.parse_args()

    root_dir = Path(args.root).resolve()
    if not root_dir.exists():
        print(f"Error: Directory {root_dir} does not exist")
        return 1

    print(f"{'='*80}")
    print(f"License Header Check")
    print(f"{'='*80}")
    print(f"Root directory: {root_dir}")
    print(f"Mode: {'FIX' if args.fix else 'CHECK'}")
    print()

    # Scan directory
    files_with_headers, files_without_headers = scan_directory(root_dir, args.verbose)

    # Calculate statistics
    total_files = len(files_with_headers) + len(files_without_headers)
    coverage = (len(files_with_headers) / total_files * 100) if total_files > 0 else 100

    # Print summary
    print(f"\n{'='*80}")
    print(f"Summary")
    print(f"{'='*80}")
    print(f"Total applicable files: {total_files}")
    print(f"Files with headers:     {len(files_with_headers)} ({len(files_with_headers)/total_files*100:.1f}%)" if total_files > 0 else "Files with headers: 0")
    print(f"Files missing headers:  {len(files_without_headers)}")
    print(f"Coverage:               {coverage:.1f}%")

    # List files without headers
    if files_without_headers:
        print(f"\n{'='*80}")
        print(f"Files Missing Headers")
        print(f"{'='*80}")
        for file_path in files_without_headers:
            print(f"  ✗ {file_path.relative_to(root_dir)}")

        # Fix if requested
        if args.fix:
            print(f"\n{'='*80}")
            print(f"Adding Headers")
            print(f"{'='*80}")
            fixed_count = 0
            for file_path in files_without_headers:
                if add_header(file_path, args.verbose):
                    fixed_count += 1

            print(f"\n✓ Added headers to {fixed_count}/{len(files_without_headers)} files")

        # Exit with error in check-only mode
        if args.check_only:
            print(f"\n✗ Check failed: {len(files_without_headers)} files missing headers")
            return 1
    else:
        print(f"\n✓ All applicable files have license headers!")

    return 0


if __name__ == '__main__':
    sys.exit(main())
