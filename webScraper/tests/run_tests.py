"""
Test runner script - Run all tests with detailed output

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run unit tests only
    python run_tests.py --integration # Run integration tests only
    python run_tests.py --coverage   # Run with coverage report
"""

import sys
import subprocess
import argparse
import os


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"\n{'='*70}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run web scraper tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--failed', action='store_true', help='Re-run only failed tests')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['pytest']
    
    # Determine test path
    if args.unit:
        cmd.append('unit/')
    elif args.integration:
        cmd.append('integration/')
        cmd.extend(['-m', 'integration'])
    else:
        cmd.append('.')
    
    # Add options
    if args.verbose:
        cmd.append('-vv')
    else:
        cmd.append('-v')
    
    if args.coverage:
        cmd.extend([
            '--cov=../backend/Crawler',
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    if args.failed:
        cmd.append('--lf')
    
    # Add formatting
    cmd.extend(['--tb=short', '--color=yes'])
    
    # Run tests
    exit_code = run_command(cmd)
    
    # Print summary
    print(f"\n{'='*70}")
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ TESTS FAILED (exit code: {exit_code})")
    
    if args.coverage and exit_code == 0:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    print(f"{'='*70}\n")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
