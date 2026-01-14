---
name: test-execution-analysis
description: Run full test suites (pytest for backend, Vitest for frontend) after code regeneration; capture outputs, coverage reports, and failures. Analyze errors (e.g., JWT mismatches, query inefficiencies, UI render bugs) with stack traces and suggestions. Report pass/fail status, coverage metrics, and prioritized failures for main agent delegation. Use when (1) Running full test suites after code regeneration, (2) Capturing test outputs, coverage reports, and failures, (3) Analyzing errors like JWT mismatches, query inefficiencies, and UI render bugs, (4) Providing stack traces and suggestions for fixes, (5) Reporting pass/fail status and coverage metrics, (6) Prioritizing failures for main agent delegation.
---

# Test Execution and Analysis Skill

Comprehensive test execution, analysis, and reporting for backend (pytest), frontend (Vitest), and E2E (Playwright) test suites with detailed error analysis and prioritization.

## Core Capabilities

### 1. Test Suite Execution

Execute comprehensive test suites across all layers:

**Backend Test Execution (pytest):**
```bash
# Execute backend test suite with coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing --tb=short -v

# Execute specific test categories
pytest tests/unit/ --tb=short -v  # Unit tests only
pytest tests/integration/ --tb=short -v  # Integration tests only
pytest tests/security/ --tb=short -v  # Security tests only
```

**Frontend Test Execution (Vitest):**
```bash
# Execute frontend test suite with coverage
cd frontend
npm run test -- --coverage --reporter=verbose

# Execute specific test types
npm run test -- --run tests/unit/  # Unit tests only
npm run test -- --run tests/components/  # Component tests only
npm run test -- --run tests/hooks/  # Hook tests only
```

**E2E Test Execution (Playwright):**
```bash
# Execute E2E test suite
cd frontend
npx playwright test --reporter=html,verbose

# Execute specific browsers or configurations
npx playwright test --project=chromium  # Specific browser
npx playwright test --headed  # Visual mode
npx playwright test --debug  # Debug mode
```

### 2. Output Capture and Analysis

Capture and analyze comprehensive test outputs:

**Pytest Output Analysis:**
```python
import subprocess
import json
import re
from typing import Dict, List, Any

def run_pytest_with_analysis(test_path: str = ".") -> Dict[str, Any]:
    """
    Execute pytest and analyze the output comprehensively.

    Args:
        test_path: Path to run tests from

    Returns:
        Dictionary containing test results, coverage, and analysis
    """
    # Run pytest with JSON output
    cmd = [
        "pytest",
        test_path,
        "--json-report",
        "--cov=app",
        "--cov-report=json",
        "-v",
        "-x"  # Stop on first failure
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd="backend")

    analysis = {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "failures": [],
        "coverage": None,
        "performance": {}
    }

    # Parse pytest output
    lines = result.stdout.split('\n')
    for line in lines:
        if 'PASSED' in line:
            analysis['passed'] += 1
        elif 'FAILED' in line:
            analysis['failed'] += 1
            analysis['failures'].append(line.strip())
        elif 'SKIPPED' in line:
            analysis['skipped'] += 1

    # Extract error information
    if result.stderr:
        error_lines = result.stderr.split('\n')
        analysis['errors'] = [line for line in error_lines if line.strip()]

    return analysis

def analyze_pytest_failure(error_output: str) -> Dict[str, Any]:
    """
    Analyze pytest failure output and extract key information.

    Args:
        error_output: Raw pytest error output

    Returns:
        Parsed error information with suggestions
    """
    analysis = {
        "error_type": "unknown",
        "location": "unknown",
        "description": "unknown",
        "suggestions": [],
        "severity": "medium"
    }

    # Common error patterns
    patterns = [
        (r"AttributeError.*'NoneType' object has no attribute", "null_reference", "High"),
        (r"jwt.exceptions.*", "jwt_error", "Critical"),
        (r"sqlalchemy.exc.*", "database_error", "High"),
        (r"KeyError.*", "key_error", "Medium"),
        (r"AssertionError.*", "assertion_error", "Medium"),
        (r"TypeError.*", "type_error", "High"),
        (r"ImportError.*", "import_error", "Critical")
    ]

    for pattern, error_type, severity in patterns:
        if re.search(pattern, error_output, re.IGNORECASE):
            analysis["error_type"] = error_type
            analysis["severity"] = severity
            break

    # Extract location from traceback
    location_match = re.search(r'File "(.*?)", line (\d+)', error_output)
    if location_match:
        analysis["location"] = f"{location_match.group(1)}:{location_match.group(2)}"

    # Extract error description
    desc_match = re.search(r'(\w+Error):\s*(.*)', error_output)
    if desc_match:
        analysis["description"] = f"{desc_match.group(1)}: {desc_match.group(2)[:200]}..."

    # Provide specific suggestions based on error type
    suggestions_map = {
        "null_reference": [
            "Check if the object is properly initialized",
            "Add null checks before accessing attributes",
            "Verify the return value of the function that should return the object"
        ],
        "jwt_error": [
            "Verify JWT token format and signature",
            "Check SECRET_KEY configuration",
            "Validate token expiration and claims",
            "Ensure proper token extraction from headers"
        ],
        "database_error": [
            "Check database connection and credentials",
            "Verify SQL query syntax",
            "Ensure proper session management",
            "Validate foreign key relationships"
        ],
        "key_error": [
            "Check if dictionary key exists before accessing",
            "Add default values for missing keys",
            "Validate data structure before access"
        ],
        "assertion_error": [
            "Review test assertion logic",
            "Verify expected vs actual values",
            "Check test data setup"
        ]
    }

    analysis["suggestions"] = suggestions_map.get(analysis["error_type"], ["Review the error details and traceback"])

    return analysis
```

**Vitest Output Analysis:**
```typescript
// Example analysis of Vitest output
interface VitestResult {
  exitCode: number;
  stdout: string;
  stderr: string;
  tests: {
    name: string;
    result: 'pass' | 'fail' | 'skip';
    duration: number;
    error?: string;
  }[];
  coverage?: any;
}

function analyzeVitestOutput(output: string): VitestResult {
  // Parse Vitest output and extract test results
  const lines = output.split('\n');
  const result: VitestResult = {
    exitCode: 0,
    stdout: output,
    stderr: '',
    tests: [],
    coverage: undefined
  };

  // Parse test results from output
  for (const line of lines) {
    if (line.includes('✓')) {
      // Parse passed test
      const testName = extractTestName(line, '✓');
      result.tests.push({
        name: testName,
        result: 'pass',
        duration: extractDuration(line)
      });
    } else if (line.includes('✗')) {
      // Parse failed test
      const testName = extractTestName(line, '✗');
      result.tests.push({
        name: testName,
        result: 'fail',
        duration: extractDuration(line),
        error: extractError(line)
      });
    }
  }

  return result;
}

function analyzeVitestFailure(errorOutput: string): {
  errorType: string;
  location: string;
  description: string;
  suggestions: string[];
  severity: string;
} {
  // Analyze Vitest failure output
  const analysis = {
    errorType: 'unknown',
    location: 'unknown',
    description: 'unknown',
    suggestions: [],
    severity: 'medium'
  };

  // Common React/Vitest error patterns
  if (errorOutput.includes('TypeError: Cannot read property')) {
    analysis.errorType = 'null_reference';
    analysis.severity = 'high';
    analysis.suggestions = [
      'Check if component props are properly passed',
      'Add conditional rendering for potentially null values',
      'Verify data structure before accessing nested properties'
    ];
  } else if (errorOutput.includes('React does not recognize')) {
    analysis.errorType = 'prop_validation';
    analysis.severity = 'medium';
    analysis.suggestions = [
      'Remove invalid props being passed to DOM elements',
      'Use destructuring to separate component props from DOM props',
      'Validate prop types in component definition'
    ];
  } else if (errorOutput.includes('Maximum update depth exceeded')) {
    analysis.errorType = 'infinite_loop';
    analysis.severity = 'critical';
    analysis.suggestions = [
      'Check useEffect dependencies for infinite loops',
      'Verify state updates are not causing continuous renders',
      'Review component lifecycle and state management'
    ];
  }

  return analysis;
}
```

### 3. Error Analysis and Classification

Comprehensive error analysis with categorization:

**JWT Error Analysis:**
```python
def analyze_jwt_errors(error_output: str) -> List[Dict[str, Any]]:
    """
    Analyze JWT-related errors and provide specific solutions.
    """
    jwt_errors = []

    # JWT-specific error patterns
    jwt_patterns = [
        (r"jwt.exceptions.ExpiredSignatureError", "Token has expired", "HIGH"),
        (r"jwt.exceptions.InvalidSignatureError", "Invalid token signature", "CRITICAL"),
        (r"jwt.exceptions.InvalidTokenError", "Invalid token format", "HIGH"),
        (r"Signature verification failed", "Token signature verification failed", "CRITICAL"),
        (r"exp.*not.*found", "Missing expiration claim", "HIGH"),
        (r"iat.*not.*found", "Missing issued-at claim", "MEDIUM")
    ]

    for pattern, description, severity in jwt_patterns:
        if re.search(pattern, error_output, re.IGNORECASE):
            jwt_errors.append({
                "type": "JWT_ERROR",
                "description": description,
                "severity": severity,
                "location": extract_location(error_output),
                "suggestions": get_jwt_suggestions(pattern)
            })

    return jwt_errors

def get_jwt_suggestions(error_pattern: str) -> List[str]:
    """Get specific suggestions for JWT errors."""
    suggestions_map = {
        "ExpiredSignatureError": [
            "Verify token expiration time",
            "Implement token refresh mechanism",
            "Check system clock synchronization",
            "Adjust token expiry duration if needed"
        ],
        "InvalidSignatureError": [
            "Verify SECRET_KEY matches between services",
            "Check algorithm consistency (HS256, RS256)",
            "Ensure proper token signing and verification",
            "Validate token encoding format"
        ],
        "InvalidTokenError": [
            "Check token format (should be header.payload.signature)",
            "Verify base64url encoding of token parts",
            "Validate token structure before decoding"
        ]
    }

    # Extract pattern name for mapping
    for key in suggestions_map:
        if key in error_pattern:
            return suggestions_map[key]

    return ["Review JWT implementation and token handling"]
```

**Database Query Error Analysis:**
```python
def analyze_database_errors(error_output: str) -> List[Dict[str, Any]]:
    """
    Analyze database-related errors and performance issues.
    """
    db_errors = []

    # Database-specific error patterns
    db_patterns = [
        (r"psycopg2.*duplicate key", "Duplicate key violation", "HIGH"),
        (r"psycopg2.*foreign key", "Foreign key constraint violation", "CRITICAL"),
        (r"sqlalchemy.orm.exc.DetachedInstanceError", "Detached instance access", "MEDIUM"),
        (r"sqlalchemy.exc.StatementError", "SQL statement error", "HIGH"),
        (r"N\+1 query", "N+1 query problem detected", "HIGH"),
        (r"timeout", "Query timeout", "MEDIUM")
    ]

    for pattern, description, severity in db_patterns:
        if re.search(pattern, error_output, re.IGNORECASE):
            db_errors.append({
                "type": "DATABASE_ERROR",
                "description": description,
                "severity": severity,
                "location": extract_location(error_output),
                "suggestions": get_database_suggestions(description)
            })

    return db_errors

def get_database_suggestions(error_description: str) -> List[str]:
    """Get specific suggestions for database errors."""
    suggestions_map = {
        "Duplicate key violation": [
            "Add unique constraint validation before database operation",
            "Implement proper error handling for constraint violations",
            "Check for existing records before creating new ones"
        ],
        "Foreign key constraint violation": [
            "Verify referenced record exists before creating dependent record",
            "Check foreign key relationships and data integrity",
            "Implement proper cascade operations if needed"
        ],
        "N+1 query problem detected": [
            "Use eager loading with selectinload or joinedload",
            "Optimize queries to fetch related data efficiently",
            "Review relationship queries for performance"
        ],
        "Query timeout": [
            "Add proper database indexes for query optimization",
            "Review query complexity and add limits if needed",
            "Consider pagination for large result sets"
        ]
    }

    return suggestions_map.get(error_description, ["Review database query and connection settings"])
```

**UI/React Error Analysis:**
```typescript
function analyzeUIErrors(errorOutput: string): Array<{
  type: string;
  description: string;
  severity: string;
  location: string;
  suggestions: string[];
}> {
  // Analyze React/UI-specific errors
  const uiErrors = [];

  // Common React error patterns
  const patterns = [
    {
      regex: /Cannot read property '.*' of null/,
      description: "Null reference in component",
      severity: "HIGH",
      suggestions: [
        "Add conditional rendering for null values",
        "Verify props are properly passed to component",
        "Check data loading states"
      ]
    },
    {
      regex: /Maximum update depth exceeded/,
      description: "Infinite re-render loop",
      severity: "CRITICAL",
      suggestions: [
        "Review useEffect dependencies",
        "Check for state updates in render cycle",
        "Verify stable dependencies in hooks"
      ]
    },
    {
      regex: /Invalid hook call/,
      description: "Invalid React hook usage",
      severity: "CRITICAL",
      suggestions: [
        "Hooks must be called at top level of component",
        "Don't call hooks inside loops or conditions",
        "Verify React version compatibility"
      ]
    },
    {
      regex: /Failed prop type/,
      description: "Prop type validation error",
      severity: "MEDIUM",
      suggestions: [
        "Check prop types match component expectations",
        "Verify data structure being passed to component",
        "Update prop type definitions if needed"
      ]
    }
  ];

  for (const pattern of patterns) {
    if (pattern.regex.test(errorOutput)) {
      uiErrors.push({
        type: "UI_ERROR",
        description: pattern.description,
        severity: pattern.severity,
        location: extractLocation(errorOutput),
        suggestions: pattern.suggestions
      });
    }
  }

  return uiErrors;
}
```

### 4. Coverage Analysis

Analyze test coverage and identify gaps:

```python
def analyze_coverage_report(coverage_file: str = "backend/coverage.json") -> Dict[str, Any]:
    """
    Analyze coverage report and identify uncovered code areas.

    Args:
        coverage_file: Path to coverage JSON file

    Returns:
        Coverage analysis with gaps and recommendations
    """
    try:
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)

        analysis = {
            "total_coverage": coverage_data.get("totals", {}).get("percent_covered", 0),
            "files": [],
            "gaps": [],
            "recommendations": []
        }

        # Analyze each file
        for file_path, file_data in coverage_data.get("files", {}).items():
            file_coverage = file_data.get("summary", {}).get("percent_covered", 0)
            missing_lines = file_data.get("executed_lines", [])

            file_info = {
                "path": file_path,
                "coverage": file_coverage,
                "missing_lines": missing_lines
            }

            analysis["files"].append(file_info)

            # Identify gaps in coverage
            if file_coverage < 80:  # Backend target
                analysis["gaps"].append({
                    "file": file_path,
                    "coverage": file_coverage,
                    "missing_lines": missing_lines
                })

        # Generate recommendations based on coverage gaps
        if analysis["total_coverage"] < 80:
            analysis["recommendations"].append(
                f"Overall coverage is {analysis['total_coverage']:.1f}%, below 80% target. "
                "Focus on creating tests for uncovered code paths."
            )

        # Identify critical areas that need coverage
        critical_patterns = [r".*auth.*", r".*security.*", r".*user.*", r".*task.*"]
        for gap in analysis["gaps"]:
            for pattern in critical_patterns:
                if re.search(pattern, gap["file"], re.IGNORECASE):
                    analysis["recommendations"].append(
                        f"Critical file {gap['file']} has low coverage ({gap['coverage']:.1f}%). "
                        "Add security and authentication tests immediately."
                    )
                    break

        return analysis

    except FileNotFoundError:
        return {
            "total_coverage": 0,
            "files": [],
            "gaps": [],
            "recommendations": ["Coverage report not found. Run tests with coverage enabled."]
        }
    except json.JSONDecodeError:
        return {
            "total_coverage": 0,
            "files": [],
            "gaps": [],
            "recommendations": ["Invalid coverage report format."]
        }
```

### 5. Performance Analysis

Analyze test performance and execution time:

```python
def analyze_test_performance(pytest_output: str) -> Dict[str, Any]:
    """
    Analyze test performance and identify slow tests.

    Args:
        pytest_output: Raw pytest output

    Returns:
        Performance analysis with slow test identification
    """
    performance_analysis = {
        "total_time": 0,
        "slow_tests": [],
        "recommendations": []
    }

    # Extract test times from output
    time_pattern = r'(\d+\.?\d*ms|[\d.]+s|[\d.]+m)'
    time_matches = re.findall(time_pattern, pytest_output)

    # Extract test names and times
    test_lines = pytest_output.split('\n')
    for line in test_lines:
        if 'ms' in line or 's' in line or 'm' in line:
            # Look for test names with timing
            test_match = re.search(r'(test_\w+)\s+(\d+\.?\d*\w+)', line)
            if test_match:
                test_name = test_match.group(1)
                time_str = test_match.group(2)

                # Convert time to milliseconds for comparison
                time_ms = convert_time_to_ms(time_str)

                if time_ms > 1000:  # More than 1 second
                    performance_analysis["slow_tests"].append({
                        "test": test_name,
                        "time": time_str,
                        "time_ms": time_ms
                    })

    # Generate recommendations for slow tests
    if performance_analysis["slow_tests"]:
        slow_test_count = len(performance_analysis["slow_tests"])
        performance_analysis["recommendations"].append(
            f"Found {slow_test_count} slow tests (>1s). "
            "Consider mocking external dependencies or optimizing database operations."
        )

    return performance_analysis

def convert_time_to_ms(time_str: str) -> float:
    """Convert time string to milliseconds."""
    if 'ms' in time_str:
        return float(time_str.replace('ms', ''))
    elif 's' in time_str:
        return float(time_str.replace('s', '')) * 1000
    elif 'm' in time_str:
        return float(time_str.replace('m', '')) * 60000
    else:
        return 0.0
```

### 6. Comprehensive Test Report Generation

Generate comprehensive reports for main agent delegation:

```python
def generate_test_report(
    pytest_results: Dict[str, Any],
    coverage_analysis: Dict[str, Any],
    performance_analysis: Dict[str, Any]
) -> str:
    """
    Generate comprehensive test report for main agent delegation.

    Args:
        pytest_results: Results from pytest execution
        coverage_analysis: Coverage analysis results
        performance_analysis: Performance analysis results

    Returns:
        Formatted test report
    """
    report = """
# Test Execution Report

## Summary
- **Total Tests**: {total_tests}
- **Passed**: {passed}
- **Failed**: {failed}
- **Skipped**: {skipped}
- **Coverage**: {coverage:.1f}%
- **Execution Time**: {execution_time}s

## Status
{status}

## Failed Tests
{failed_tests}

## Coverage Analysis
{coverage_details}

## Performance Analysis
{performance_details}

## Recommendations
{recommendations}

## Priority Issues
{priority_issues}
""".format(
        total_tests=pytest_results['passed'] + pytest_results['failed'] + pytest_results['skipped'],
        passed=pytest_results['passed'],
        failed=pytest_results['failed'],
        skipped=pytest_results['skipped'],
        coverage=coverage_analysis['total_coverage'],
        execution_time=performance_analysis.get('total_time', 0),
        status=get_status_summary(pytest_results, coverage_analysis),
        failed_tests=format_failed_tests(pytest_results['failures']),
        coverage_details=format_coverage_analysis(coverage_analysis),
        performance_details=format_performance_analysis(performance_analysis),
        recommendations=format_recommendations(coverage_analysis, performance_analysis),
        priority_issues=format_priority_issues(pytest_results, coverage_analysis)
    )

    return report

def get_status_summary(pytest_results: Dict[str, Any], coverage_analysis: Dict[str, Any]) -> str:
    """Generate status summary based on results."""
    if pytest_results['failed'] > 0:
        return "❌ **FAILED** - Tests have failures that need immediate attention"
    elif coverage_analysis['total_coverage'] < 80:
        return "⚠️  **PARTIAL** - Tests pass but coverage is below 80% target"
    else:
        return "✅ **PASSED** - All tests pass and coverage meets requirements"

def format_failed_tests(failures: List[str]) -> str:
    """Format failed tests for report."""
    if not failures:
        return "No failed tests."

    formatted = []
    for i, failure in enumerate(failures[:5], 1):  # Limit to top 5
        formatted.append(f"{i}. {failure[:200]}...")  # Truncate long messages

    if len(failures) > 5:
        formatted.append(f"... and {len(failures) - 5} more failures")

    return '\n'.join(formatted)

def format_coverage_analysis(analysis: Dict[str, Any]) -> str:
    """Format coverage analysis for report."""
    report = f"- **Overall Coverage**: {analysis['total_coverage']:.1f}%\n"

    if analysis['gaps']:
        report += "- **Low Coverage Files**:\n"
        for gap in analysis['gaps'][:3]:  # Top 3 gaps
            report += f"  - {gap['file']}: {gap['coverage']:.1f}%\n"

    return report

def format_priority_issues(pytest_results: Dict[str, Any], coverage_analysis: Dict[str, Any]) -> str:
    """Format priority issues for main agent delegation."""
    issues = []

    if pytest_results['failed'] > 0:
        issues.append(f"🔴 CRITICAL: {pytest_results['failed']} tests failed - fix immediately")

    if coverage_analysis['total_coverage'] < 80:
        issues.append(f"🟡 MEDIUM: Coverage at {coverage_analysis['total_coverage']:.1f}% - below 80% target")

    if coverage_analysis['gaps']:
        critical_gaps = [gap for gap in coverage_analysis['gaps'] if gap['coverage'] < 50]
        if critical_gaps:
            issues.append(f"🔴 CRITICAL: {len(critical_gaps)} files have <50% coverage")

    return '\n'.join(issues) if issues else "No priority issues identified."
```

### 7. Real-time Test Monitoring

Monitor test execution in real-time:

```python
def monitor_test_execution(test_command: List[str], timeout: int = 300) -> Dict[str, Any]:
    """
    Monitor test execution in real-time with timeout protection.

    Args:
        test_command: Command to execute tests
        timeout: Maximum time to wait for test completion

    Returns:
        Execution results with real-time monitoring
    """
    import signal
    from subprocess import Popen, PIPE, TimeoutExpired

    start_time = time.time()

    # Start test process
    process = Popen(test_command, stdout=PIPE, stderr=PIPE, text=True, cwd="backend")

    try:
        # Wait for process with timeout
        stdout, stderr = process.communicate(timeout=timeout)

        execution_time = time.time() - start_time

        return {
            "exit_code": process.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": execution_time,
            "timeout": False,
            "completed": True
        }

    except TimeoutExpired:
        # Terminate process if timeout
        process.kill()
        process.communicate()  # Clean up

        execution_time = time.time() - start_time

        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Test execution timed out after {timeout} seconds",
            "execution_time": execution_time,
            "timeout": True,
            "completed": False
        }
```

## Usage Examples

### Example 1: Backend Test Execution
```
User: "Run the backend test suite and analyze results"
Agent: [Triggers test-execution-analysis skill] → Executes pytest with coverage, captures output, analyzes 15 failures (JWT, DB queries), generates report with priority fixes, coverage gaps identified in auth module
```

### Example 2: Frontend Test Analysis
```
User: "Analyze the failing frontend tests"
Agent: [Triggers test-execution-analysis skill] → Runs Vitest, identifies 3 component render errors, provides specific React hook fixes, suggests prop validation improvements, reports 72% coverage needing improvement
```

### Example 3: E2E Test Monitoring
```
User: "Execute and monitor the E2E test suite"
Agent: [Triggers test-execution-analysis skill] → Runs Playwright tests with real-time monitoring, identifies 2 flaky tests, provides debugging suggestions, generates performance report showing slow page loads
```

### Example 4: Coverage Analysis
```
User: "Analyze test coverage for the auth module"
Agent: [Triggers test-execution-analysis skill] → Analyzes coverage reports, identifies 65% coverage in auth module, generates recommendations for missing security tests, prioritizes JWT validation test creation
```

## Quality Checklist

- [ ] Test execution captures all outputs (stdout, stderr)
- [ ] Error analysis includes specific suggestions for fixes
- [ ] Coverage analysis identifies gaps and priorities
- [ ] Performance analysis flags slow tests
- [ ] Reports include severity classification
- [ ] Priority issues are clearly identified
- [ ] Stack traces are properly parsed
- [ ] Timeout protection is implemented
- [ ] Real-time monitoring is available
- [ ] Results are actionable for main agent
- [ ] All test layers are covered (backend, frontend, E2E)
- [ ] Security tests are prioritized
- [ ] User isolation tests are verified
- [ ] Error handling paths are tested

## Integration Points

- **CI/CD Pipeline**: Automated test execution and reporting
- **Code Review**: Provides test quality metrics for review
- **Development Workflow**: Real-time test feedback
- **Coverage Tools**: Integration with coverage.py, Istanbul
- **Monitoring Systems**: Test execution metrics and alerts
- **Main Agent Delegation**: Prioritized issue reporting

## References

- **Backend Testing Spec**: `@specs/testing/backend-testing.md` for pytest requirements
- **Frontend Testing Spec**: `@specs/testing/frontend-testing.md` for Vitest patterns
- **E2E Testing Spec**: `@specs/testing/e2e-testing.md` for Playwright flows
- **Coverage Requirements**: `@specs/testing/overview.md` for coverage targets
- **Security Testing**: `@specs/features/authentication.md` for auth test requirements
- **Performance Testing**: `@specs/ui/animations.md` for performance metrics