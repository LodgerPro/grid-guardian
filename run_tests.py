#!/usr/bin/env python3
"""
Comprehensive test runner for Grid Guardian
Generates HTML reports and coverage statistics
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def run_command(cmd, description):
    """Run command and report results"""
    print(f"\n▶ {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ {description} completed successfully")
        return True
    else:
        print(f"✗ {description} failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return False


def main():
    """Main test execution"""
    print_header("GRID GUARDIAN - AUTOMATED TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Ensure reports directory exists
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Run tests with coverage and HTML report
    print_header("Running Tests")

    test_cmd = (
        "venv/Scripts/python.exe -m pytest tests/ "
        "-v "
        "--html=tests/reports/test_report.html "
        "--self-contained-html "
        "--cov=app "
        "--cov=data "
        "--cov=src "
        "--cov-report=html:tests/reports/coverage "
        "--cov-report=term-missing"
    )

    success = run_command(test_cmd, "Test execution")

    # Summary
    print_header("TEST EXECUTION COMPLETE")

    if success:
        print("\n✓ All tests completed")
        print("\nReports generated:")
        print(f"  - Test report:     tests/reports/test_report.html")
        print(f"  - Coverage report: tests/reports/coverage/index.html")
        print(f"  - Test log:        tests/reports/test.log")
        print("\nOpen in browser:")
        print(f"  start tests/reports/test_report.html")
        return 0
    else:
        print("\n✗ Some tests failed")
        print("Check logs for details")
        return 1


if __name__ == "__main__":
    sys.exit(main())
