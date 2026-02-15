"""
Stateless Validation Scripts

Pre-built scripts for validating common stateless architecture compliance scenarios.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_memory_state_audit(project_path: str):
    """
    Run memory state audit on a project directory.

    Args:
        project_path: Path to the project to audit
    """
    script_path = Path(__file__).parent.parent / "scripts" / "memory_state_audit.py"

    if not script_path.exists():
        print(f"❌ Memory state audit script not found: {script_path}")
        return False

    try:
        result = subprocess.run([
            sys.executable, str(script_path), project_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print("🔍 Memory State Audit Results:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Audit Warnings/Errors:")
            print(result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Memory state audit timed out")
        return False
    except Exception as e:
        print(f"❌ Error running memory state audit: {e}")
        return False


def run_database_isolation_check(project_path: str):
    """
    Run database isolation check on a project directory.

    Args:
        project_path: Path to the project to audit
    """
    script_path = Path(__file__).parent.parent / "scripts" / "database_isolation_checker.py"

    if not script_path.exists():
        print(f"❌ Database isolation checker script not found: {script_path}")
        return False

    try:
        result = subprocess.run([
            sys.executable, str(script_path), project_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print("🔍 Database Isolation Check Results:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Check Warnings/Errors:")
            print(result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Database isolation check timed out")
        return False
    except Exception as e:
        print(f"❌ Error running database isolation check: {e}")
        return False


def run_cache_key_validation(project_path: str):
    """
    Run cache key validation on a project directory.

    Args:
        project_path: Path to the project to audit
    """
    script_path = Path(__file__).parent.parent / "scripts" / "cache_key_validator.py"

    if not script_path.exists():
        print(f"❌ Cache key validator script not found: {script_path}")
        return False

    try:
        result = subprocess.run([
            sys.executable, str(script_path), project_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print("🔍 Cache Key Validation Results:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Validation Warnings/Errors:")
            print(result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Cache key validation timed out")
        return False
    except Exception as e:
        print(f"❌ Error running cache key validation: {e}")
        return False


def run_transaction_boundary_test(project_path: str):
    """
    Run transaction boundary test on a project directory.

    Args:
        project_path: Path to the project to audit
    """
    script_path = Path(__file__).parent.parent / "scripts" / "transaction_boundary_tester.py"

    if not script_path.exists():
        print(f"❌ Transaction boundary tester script not found: {script_path}")
        return False

    try:
        result = subprocess.run([
            sys.executable, str(script_path), project_path
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout

        print("🔍 Transaction Boundary Test Results:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Test Warnings/Errors:")
            print(result.stderr)

        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Transaction boundary test timed out")
        return False
    except Exception as e:
        print(f"❌ Error running transaction boundary test: {e}")
        return False


def run_comprehensive_stateless_audit(project_path: str):
    """
    Run all stateless validation checks on a project.

    Args:
        project_path: Path to the project to audit
    """
    print(f"🚀 Starting comprehensive stateless audit for: {project_path}")
    print("="*60)

    results = {}

    print("\n1️⃣  Running Memory State Audit...")
    results['memory_state'] = run_memory_state_audit(project_path)

    print("\n2️⃣  Running Database Isolation Check...")
    results['database_isolation'] = run_database_isolation_check(project_path)

    print("\n3️⃣  Running Cache Key Validation...")
    results['cache_validation'] = run_cache_key_validation(project_path)

    print("\n4️⃣  Running Transaction Boundary Test...")
    results['transaction_boundary'] = run_transaction_boundary_test(project_path)

    print("\n" + "="*60)
    print("📋 COMPREHENSIVE AUDIT RESULTS")
    print("="*60)

    for check_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} - {check_name.replace('_', ' ').title()}")

    all_passed = all(results.values())
    overall_status = "✅ ALL CHECKS PASSED" if all_passed else "❌ SOME CHECKS FAILED"

    print(f"\n📊 OVERALL STATUS: {overall_status}")
    print("="*60)

    return all_passed


def generate_compliance_report(project_path: str, output_file: str = None):
    """
    Generate a compliance report for stateless architecture validation.

    Args:
        project_path: Path to the project to audit
        output_file: Optional file path to save the report
    """
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines = [
        "Stateless Architecture Compliance Report",
        "=" * 50,
        f"Generated: {timestamp}",
        f"Project: {project_path}",
        "",
    ]

    # Run audit and capture results
    import io
    from contextlib import redirect_stdout

    captured_output = io.StringIO()
    with redirect_stdout(captured_output):
        all_passed = run_comprehensive_stateless_audit(project_path)

    report_lines.extend(captured_output.getvalue().split('\n'))

    # Add compliance summary
    report_lines.extend([
        "",
        "Compliance Summary:",
        f"  Stateless Architecture Compliant: {'YES' if all_passed else 'NO'}",
        "  Recommendations: See individual check results above",
        "",
        "Next Steps:",
        "  1. Address any failed checks identified above",
        "  2. Re-run audit after implementing fixes",
        "  3. Ensure all changes maintain stateless principles",
    ])

    report_content = '\n'.join(report_lines)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(report_content)
        print(f"📄 Report saved to: {output_file}")

    return report_content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validation_scripts.py <project_path> [report_output]")
        print("Example: python validation_scripts.py /path/to/project report.txt")
        sys.exit(1)

    project_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)

    if output_file:
        report = generate_compliance_report(project_path, output_file)
        print(f"\n📄 Full report content:")
        print(report)
    else:
        run_comprehensive_stateless_audit(project_path)