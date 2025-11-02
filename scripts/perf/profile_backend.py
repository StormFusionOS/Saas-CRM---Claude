#!/usr/bin/env python3
"""
Backend Performance Profiling

Profiles backend code using cProfile and generates flamegraph-compatible collapsed stacks.

Outputs:
- .prof file (cProfile binary format)
- .txt file (pstats text output)
- .collapsed file (flamegraph collapsed stacks format)

Usage:
    # Profile a Python module
    python scripts/perf/profile_backend.py --module my_module --function main

    # Profile with custom duration
    python scripts/perf/profile_backend.py --module api.server --duration 60

    # Profile and generate all outputs
    python scripts/perf/profile_backend.py --module worker --output artifacts/perf/worker_profile

Visualizing:
    # Using flamegraph.pl (if available)
    flamegraph.pl artifacts/perf/profile.collapsed > flamegraph.svg

    # Using speedscope (upload .prof file)
    https://www.speedscope.app/
"""

import sys
import cProfile
import pstats
import io
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime
import time


class ProfilerBackend:
    """
    Backend profiling using cProfile

    Generates multiple output formats for analysis.
    """

    def __init__(self, output_path: str = "artifacts/perf/profile"):
        """
        Initialize profiler

        Args:
            output_path: Base path for output files (without extension)
        """
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def profile_function(
        self,
        func,
        *args,
        duration: Optional[int] = None,
        **kwargs
    ):
        """
        Profile a function call

        Args:
            func: Function to profile
            args: Positional arguments to pass to function
            duration: If set, profile for this many seconds
            kwargs: Keyword arguments to pass to function
        """
        print(f"=== Profiling {func.__name__} ===")

        profiler = cProfile.Profile()

        if duration:
            print(f"Duration: {duration} seconds")
            profiler.enable()
            time.sleep(duration)  # Profile for duration
            profiler.disable()
        else:
            print("Single execution")
            profiler.runcall(func, *args, **kwargs)

        # Save outputs
        self._save_prof(profiler)
        self._save_text(profiler)
        self._save_collapsed(profiler)

        print(f"\n✓ Profile saved to:")
        print(f"  Binary: {self.output_path}.prof")
        print(f"  Text: {self.output_path}.txt")
        print(f"  Collapsed: {self.output_path}.collapsed")

    def profile_code(self, code_string: str):
        """
        Profile a code string

        Args:
            code_string: Python code to profile
        """
        print(f"=== Profiling Code ===")

        profiler = cProfile.Profile()
        profiler.run(code_string)

        # Save outputs
        self._save_prof(profiler)
        self._save_text(profiler)
        self._save_collapsed(profiler)

    def _save_prof(self, profiler: cProfile.Profile):
        """Save binary .prof file"""
        prof_file = f"{self.output_path}.prof"
        profiler.dump_stats(prof_file)

    def _save_text(self, profiler: cProfile.Profile):
        """Save text stats"""
        txt_file = f"{self.output_path}.txt"

        # Generate stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)

        # Sort by cumulative time
        stats.sort_stats('cumulative')

        # Write header
        stream.write("=" * 80 + "\n")
        stream.write(f"Profile Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        stream.write("=" * 80 + "\n\n")

        # Top functions by cumulative time
        stream.write("Top 50 functions by cumulative time:\n")
        stream.write("-" * 80 + "\n")
        stats.print_stats(50)

        # Top functions by total time
        stream.write("\n" + "=" * 80 + "\n")
        stream.write("Top 50 functions by total time:\n")
        stream.write("-" * 80 + "\n")
        stats.sort_stats('time')
        stats.print_stats(50)

        # Callers
        stream.write("\n" + "=" * 80 + "\n")
        stream.write("Callers for top 20 functions:\n")
        stream.write("-" * 80 + "\n")
        stats.sort_stats('cumulative')
        stats.print_callers(20)

        # Save to file
        Path(txt_file).write_text(stream.getvalue())

    def _save_collapsed(self, profiler: cProfile.Profile):
        """
        Save collapsed stacks for flamegraph visualization

        Format: semicolon-separated call stacks with sample counts
        Example: func1;func2;func3 100

        This format is compatible with:
        - flamegraph.pl (Brendan Gregg's flamegraph tool)
        - speedscope
        - Firefox Profiler
        """
        collapsed_file = f"{self.output_path}.collapsed"

        # Get stats
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')

        # Build call graph
        stacks = {}

        # Extract function calls and build stacks
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            # Format: filename:line(function)
            func_name = self._format_func_name(func)

            # Add to stacks with call count
            if func_name not in stacks:
                stacks[func_name] = 0
            stacks[func_name] += nc  # number of calls

            # Process callers to build full stack
            for caller in callers:
                caller_name = self._format_func_name(caller)
                stack_trace = f"{caller_name};{func_name}"

                if stack_trace not in stacks:
                    stacks[stack_trace] = 0
                stacks[stack_trace] += callers[caller][0]  # call count

        # Write collapsed stacks
        with open(collapsed_file, 'w') as f:
            for stack, count in sorted(stacks.items(), key=lambda x: x[1], reverse=True):
                if count > 0:  # Only include stacks with calls
                    f.write(f"{stack} {count}\n")

    def _format_func_name(self, func_tuple) -> str:
        """Format function tuple as readable name"""
        filename, line, func_name = func_tuple

        # Simplify filename (remove full path, keep relative)
        if filename.startswith('/'):
            # Extract just the module name
            parts = filename.split('/')
            if 'site-packages' in parts:
                # For libraries, show package name
                idx = parts.index('site-packages') + 1
                filename = '/'.join(parts[idx:])
            else:
                # For local code, show relative path
                filename = '/'.join(parts[-3:]) if len(parts) > 3 else '/'.join(parts)

        return f"{filename}:{line}({func_name})"


# Example functions to profile
def example_slow_function():
    """Example function with performance issues"""
    import time
    import random

    # Simulate database query
    def simulate_db_query():
        time.sleep(0.01)
        return [{"id": i, "value": random.random()} for i in range(100)]

    # Simulate data processing
    def process_data(data):
        result = []
        for item in data:
            # Inefficient processing
            result.append({
                "id": item["id"],
                "computed": sum([item["value"] ** i for i in range(10)])
            })
        return result

    # Main logic
    results = []
    for _ in range(10):
        data = simulate_db_query()
        processed = process_data(data)
        results.extend(processed)

    return results


def example_api_endpoint():
    """Example API endpoint simulation"""
    import time

    def validate_input():
        time.sleep(0.002)

    def check_auth():
        time.sleep(0.005)

    def db_lookup():
        time.sleep(0.020)

    def serialize_response():
        time.sleep(0.003)

    # Simulate request handling
    validate_input()
    check_auth()
    data = db_lookup()
    response = serialize_response()

    return response


def main():
    parser = argparse.ArgumentParser(description="Backend Performance Profiling")
    parser.add_argument(
        '--module',
        type=str,
        help="Python module to import and profile"
    )
    parser.add_argument(
        '--function',
        type=str,
        default='main',
        help="Function to profile (default: main)"
    )
    parser.add_argument(
        '--duration',
        type=int,
        help="Profile for this many seconds (for long-running processes)"
    )
    parser.add_argument(
        '--output',
        type=str,
        default='artifacts/perf/profile',
        help="Output path (without extension)"
    )
    parser.add_argument(
        '--example',
        type=str,
        choices=['slow', 'api'],
        help="Profile example function (slow or api)"
    )

    args = parser.parse_args()

    profiler = ProfilerBackend(output_path=args.output)

    if args.example:
        # Profile example function
        if args.example == 'slow':
            print("Profiling slow example function...")
            profiler.profile_function(example_slow_function)
        elif args.example == 'api':
            print("Profiling API endpoint example...")
            # Run multiple times to get meaningful stats
            def run_api_multiple_times():
                for _ in range(100):
                    example_api_endpoint()

            profiler.profile_function(run_api_multiple_times)

    elif args.module:
        # Import and profile module
        try:
            # Import module
            module = __import__(args.module, fromlist=[args.function])
            func = getattr(module, args.function)

            # Profile function
            profiler.profile_function(func, duration=args.duration)

        except ImportError as e:
            print(f"❌ Failed to import module '{args.module}': {e}")
            sys.exit(1)
        except AttributeError as e:
            print(f"❌ Function '{args.function}' not found in module '{args.module}': {e}")
            sys.exit(1)

    else:
        parser.print_help()
        print("\nExample:")
        print("  python scripts/perf/profile_backend.py --example slow")
        print("  python scripts/perf/profile_backend.py --module myapp.api --function process_request")
        sys.exit(1)


if __name__ == "__main__":
    main()
