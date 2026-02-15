---
name: bug-error-detection
description: Focused detection of runtime and simulated errors including JWT verification failures, database query inefficiencies, and security vulnerabilities. Cross-checks against Next.js/FastAPI/SQLModel best practices, provides reproducible steps and prioritized fixes ensuring alignment with multi-user isolation and no-manual-code rules. Use when (1) Identifying runtime errors and exceptions in application code, (2) Detecting security vulnerabilities like JWT token issues, database injection risks, or authentication bypasses, (3) Finding performance bottlenecks and query inefficiencies (especially for recurring tasks), (4) Verifying proper error handling and logging across frontend/backend, (5) Ensuring compliance with multi-user isolation requirements, (6) Prioritizing fixes based on severity and impact to user experience.
---

# Bug and Error Detection Skill

Advanced detection and analysis of runtime errors, security vulnerabilities, and performance issues in the Todo application stack, with focus on Next.js, FastAPI, and SQLModel specific concerns.

## Core Capabilities

### 1. Runtime Error Detection

Identify common runtime errors and exceptions:

**Frontend Runtime Errors:**
```typescript
// Common Next.js/React runtime error patterns to detect:

// 1. Undefined/null access
const task = tasks.find(t => t.id === id);
return <div>{task.title}</div>; // Potential undefined access

// 2. State update on unmounted components
useEffect(() => {
  fetchData().then(setData);
  return () => controller.abort(); // Missing cleanup
}, []);

// 3. Memory leaks with intervals/subscriptions
useEffect(() => {
  const interval = setInterval(() => {
    // Missing cleanup
  }, 1000);
  // Missing return clearInterval(interval);
}, []);

// 4. Incorrect async/await usage
const handleSubmit = () => {
  // Missing async/await
  api.createTask(task).then(() => {
    // Potential race conditions
  });
};
```

**Backend Runtime Errors:**
```python
# Common FastAPI/SQLModel runtime error patterns to detect:

# 1. Unhandled database exceptions
def get_user_tasks(user_id: str):
    return session.exec(select(Task).where(Task.user_id == user_id)).all()
    # Missing try-catch for potential database errors

# 2. Improper JWT handling
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception:  # Too broad exception handling
        return None  # Silent failure

# 3. Resource leaks
def process_tasks():
    file = open("tasks.txt", "r")  # Missing proper resource management
    # Missing file.close() or context manager

# 4. Race conditions in async operations
async def update_task_status(task_id: str, status: bool):
    task = session.get(Task, task_id)  # Potential race condition
    task.completed = status
    session.add(task)
    session.commit()  # No transaction safety
```

### 2. JWT Security Vulnerability Detection

Identify JWT-related security issues:

```python
def scan_jwt_vulnerabilities():
    """Scan for JWT-related security vulnerabilities."""
    issues = []

    # Check for common JWT issues in backend
    jwt_patterns = [
        # Weak signing algorithms
        "alg.*none",
        "algorithm.*none",
        "HS256.*without.*validation",
        # Hardcoded secrets
        'SECRET_KEY.*="',
        "secret.*=",
        # Missing token validation
        "jwt.decode.*without.*verify",
        "decode.*without.*algorithm",
        # Insufficient expiration checks
        "exp.*not.*checked",
        "expiration.*not.*validated"
    ]

    import subprocess
    for pattern in jwt_patterns:
        result = subprocess.run([
            "grep", "-r", "-n", "-i",
            pattern,
            "backend/"
        ], capture_output=True, text=True)

        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if ':' in line and len(line.split(':', 2)) >= 3:
                    file_path, line_num, code = line.split(':', 2)
                    severity = "critical" if "none" in pattern or "hardcoded" in pattern else "high"

                    issues.append({
                        'file': file_path,
                        'line': int(line_num),
                        'type': 'jwt_security_vulnerability',
                        'severity': severity,
                        'description': f'Potential JWT vulnerability: {code.strip()}',
                        'pattern': pattern,
                        'recommendation': get_jwt_recommendation(pattern)
                    })

    return issues

def get_jwt_recommendation(pattern):
    """Get specific recommendation based on JWT vulnerability pattern."""
    if "none" in pattern:
        return "Never allow 'none' algorithm in JWT verification. Only accept strong algorithms like RS256."
    elif "SECRET_KEY" in pattern:
        return "Use environment variables for secrets, never hardcode them in source code."
    elif "without.*validation" in pattern:
        return "Always validate JWT tokens with proper verification and algorithm specification."
    elif "exp.*not.*checked" in pattern:
        return "Always validate token expiration (exp) and issue time (iat) claims."
    else:
        return "Review JWT implementation against security best practices."
```

### 3. Database Query Inefficiency Detection

Identify performance bottlenecks in database queries:

```python
def scan_database_inefficiencies():
    """Scan for database query performance issues."""
    issues = []

    # N+1 query detection
    n_plus_1_patterns = [
        # Loop with individual queries
        r"for.*in.*:",
        r".*session\.exec.*select.*",
        # Pattern: iterating and making db calls
    ]

    import subprocess
    # Look for patterns indicating N+1 queries
    result = subprocess.run([
        "grep", "-r", "-n", "-A", "5", "-B", "2",
        "for.*in.*session\\|for.*in.*select\\|for.*in.*exec",
        "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for block in result.stdout.strip().split('\n--\n'):
            lines = block.split('\n')
            for i, line in enumerate(lines):
                if ('for ' in line and
                    ('session.exec' in line or 'select(' in line) and
                    i + 1 < len(lines)):
                    # Check if this pattern continues with more queries
                    issues.append({
                        'type': 'potential_n_plus_1',
                        'severity': 'high',
                        'description': f'Potential N+1 query pattern detected in loop: {line.strip()}',
                        'recommendation': 'Use eager loading with selectinload or joinedload to optimize queries'
                    })

    # Recurring tasks inefficiency detection
    recurring_patterns = [
        "recurrence",
        "repeat",
        "schedule",
        "cron",
        "interval"
    ]

    for pattern in recurring_patterns:
        result = subprocess.run([
            "grep", "-r", "-n", "-C", "5",
            pattern,
            "backend/"
        ], capture_output=True, text=True)

        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if ':' in line and len(line.split(':', 2)) >= 3:
                    file_path, line_num, code = line.split(':', 2)
                    if any(ineff_pattern in code.lower() for ineff_pattern in
                          ['while true', 'sleep', 'time.sleep', 'blocking']):
                        issues.append({
                            'file': file_path,
                            'line': int(line_num),
                            'type': 'recurring_task_inefficiency',
                            'severity': 'medium',
                            'description': f'Potential inefficiency in recurring task handling: {code.strip()}',
                            'recommendation': 'Use a proper task queue system like Celery or database triggers instead of blocking operations'
                        })

    return issues
```

### 4. Multi-User Isolation Verification

Check for proper user isolation:

```python
def scan_user_isolation_breaches():
    """Detect potential multi-user isolation breaches."""
    issues = []

    # Look for queries that don't properly filter by user_id
    import subprocess

    # Find all task-related queries
    result = subprocess.run([
        "grep", "-r", "-n", "-C", "3",
        "select.*Task\\|session\\.exec\\|get.*task",
        "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if ':' in line and len(line.split(':', 2)) >= 3:
                file_path, line_num, code = line.split(':', 2)

                # Check if the query lacks user_id filtering
                if ('Task' in code and
                    'user_id' not in code and
                    'where.*user_id' not in code.lower() and
                    'filter.*user_id' not in code.lower()):

                    issues.append({
                        'file': file_path,
                        'line': int(line_num),
                        'type': 'user_isolation_breach',
                        'severity': 'critical',
                        'description': f'Potential user isolation breach - query may access other users\' data: {code.strip()}',
                        'recommendation': 'Always filter queries by user_id to ensure proper isolation between users'
                    })

    # Check for missing user validation in API endpoints
    api_result = subprocess.run([
        "grep", "-r", "-n", "-A", "10",
        "def.*get\\|def.*post\\|def.*put\\|def.*delete",
        "backend/app/api/"
    ], capture_output=True, text=True)

    if api_result.stdout:
        for block in api_result.stdout.strip().split('\n--\n'):
            if ('user_id' not in block.lower() and
                ('task' in block.lower() or 'tasks' in block.lower())):
                issues.append({
                    'type': 'missing_user_validation',
                    'severity': 'high',
                    'description': 'API endpoint may lack proper user validation for task access',
                    'recommendation': 'Verify that endpoints validate user_id matches the requested resource'
                })

    return issues
```

### 5. Error Handling and Logging Verification

Ensure proper error handling:

```python
def scan_error_handling_issues():
    """Scan for missing or improper error handling."""
    issues = []

    import subprocess

    # Look for try blocks without proper exception handling
    result = subprocess.run([
        "grep", "-r", "-n", "-A", "5",
        "try:",
        "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for block in result.stdout.strip().split('\n--\n'):
            if 'except:' in block or 'except Exception:' in block:
                # Check for bare except or too broad exception handling
                if 'except:' in block and 'Exception' not in block:
                    issues.append({
                        'type': 'bare_except_clause',
                        'severity': 'high',
                        'description': 'Bare except clause detected - catches all exceptions including system exits',
                        'recommendation': 'Use specific exception types instead of bare except:'
                    })
                elif 'except Exception:' in block and 'raise' not in block:
                    issues.append({
                        'type': 'broad_exception_handling',
                        'severity': 'medium',
                        'description': 'Too broad exception handling without re-raising',
                        'recommendation': 'Handle specific exceptions and re-raise unexpected ones'
                    })

    # Check for missing error logging
    result = subprocess.run([
        "grep", "-r", "-n", "-C", "3",
        "raise\\|except\\|error",
        "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if ('except' in line and
                'logging' not in line.lower() and
                'log' not in line.lower() and
                'print' not in line.lower()):
                issues.append({
                    'type': 'missing_error_logging',
                    'severity': 'medium',
                    'description': 'Exception caught without proper logging',
                    'recommendation': 'Log exceptions with sufficient context for debugging'
                })

    return issues
```

### 6. Frontend Security Vulnerabilities

Check for client-side security issues:

```typescript
// Security vulnerability patterns to detect in frontend:

// 1. XSS vulnerabilities
function vulnerableComponent(props: { content: string }) {
  return <div dangerouslySetInnerHTML={{ __html: props.content }} />;
  // Direct HTML injection without sanitization
}

// 2. CSRF protection issues
async function submitTask(task: Task) {
  const response = await fetch('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
    // Missing CSRF token
  });
}

// 3. Authentication bypass
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token'); // Client-side storage is vulnerable
  if (!token) return <Login />; // Simple check, not server-validated
  return <>{children}</>;
}

// 4. Insecure API calls
async function fetchUserData() {
  // Using HTTP instead of HTTPS
  const response = await fetch('http://api.example.com/user');
  return response.json();
}
```

### 7. Comprehensive Detection Function

```python
def run_bug_detection_scan():
    """Run comprehensive bug and error detection scan."""
    scan_results = {
        'summary': {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        },
        'findings': {
            'jwt_vulnerabilities': [],
            'database_inefficiencies': [],
            'user_isolation_breaches': [],
            'error_handling_issues': [],
            'frontend_security_issues': []
        },
        'reproducible_steps': [],
        'prioritized_fixes': []
    }

    # Run all detection functions
    scan_results['findings']['jwt_vulnerabilities'] = scan_jwt_vulnerabilities()
    scan_results['findings']['database_inefficiencies'] = scan_database_inefficiencies()
    scan_results['findings']['user_isolation_breaches'] = scan_user_isolation_breaches()
    scan_results['findings']['error_handling_issues'] = scan_error_handling_issues()

    # Categorize findings by severity
    for category, issues in scan_results['findings'].items():
        for issue in issues:
            severity = issue.get('severity', 'medium')
            scan_results['summary'][severity] += 1

    # Generate reproducible steps
    for category, issues in scan_results['findings'].items():
        for issue in issues:
            step = f"1. Navigate to {issue.get('file', 'N/A')} line {issue.get('line', 'N/A')}\n"
            step += f"2. Observe the {issue['type']} issue: {issue['description']}\n"
            step += f"3. Apply the recommended fix: {issue['recommendation']}"
            scan_results['reproducible_steps'].append(step)

    # Generate prioritized fixes
    # Critical issues first
    critical_issues = []
    high_issues = []

    for category, issues in scan_results['findings'].items():
        for issue in issues:
            if issue['severity'] == 'critical':
                critical_issues.append({
                    'issue': issue['description'],
                    'location': f"{issue.get('file', 'N/A')}:{issue.get('line', 'N/A')}",
                    'fix': issue['recommendation']
                })
            elif issue['severity'] == 'high':
                high_issues.append({
                    'issue': issue['description'],
                    'location': f"{issue.get('file', 'N/A')}:{issue.get('line', 'N/A')}",
                    'fix': issue['recommendation']
                })

    scan_results['prioritized_fixes'] = {
        'critical': critical_issues,
        'high': high_issues
    }

    return scan_results

# Example usage
if __name__ == "__main__":
    results = run_bug_detection_scan()
    print(f"Bug detection scan completed:")
    print(f"- Critical issues: {results['summary']['critical']}")
    print(f"- High issues: {results['summary']['high']}")
    print(f"- Medium issues: {results['summary']['medium']}")
    print(f"- Low issues: {results['summary']['low']}")
```

### 8. Integration with Testing Framework

```python
def generate_test_cases_for_bugs():
    """Generate test cases to verify bug fixes."""
    test_cases = []

    # JWT vulnerability test cases
    test_cases.append({
        'name': 'JWT None Algorithm Attack Prevention',
        'description': 'Verify that JWT tokens with "none" algorithm are rejected',
        'implementation': '''
async def test_jwt_none_algorithm_rejection():
    # Create a JWT token with "none" algorithm
    malicious_token = jwt.encode({}, key="", algorithm="none")

    # Attempt to use the token
    response = client.get("/api/user/tasks",
                         headers={"Authorization": f"Bearer {malicious_token}"})

    # Should return 401 Unauthorized
    assert response.status_code == 401
        ''',
        'file': 'tests/test_security.py'
    })

    # User isolation test cases
    test_cases.append({
        'name': 'User Isolation Verification',
        'description': 'Verify that users cannot access other users\' tasks',
        'implementation': '''
async def test_user_task_isolation():
    # Create two users
    user1 = create_test_user("user1@example.com")
    user2 = create_test_user("user2@example.com")

    # Create tasks for user1
    task1 = create_task_for_user(user1.id, "User 1 task")

    # User2 should not be able to access user1's tasks
    response = client.get(f"/api/{user2.id}/tasks",
                         headers={"Authorization": f"Bearer {user2.token}"})

    # Should not contain user1's task
    assert task1.id not in [task['id'] for task in response.json()]
        ''',
        'file': 'tests/test_isolation.py'
    })

    return test_cases
```

## Usage Examples

### Example 1: JWT Security Audit
```
User: "Check for JWT security vulnerabilities"
Agent: [Triggers bug-error-detection skill] → Scans backend for JWT implementation issues, identifies hardcoded secrets and missing expiration validation, generates critical fixes with specific file:line references
```

### Example 2: Performance Issue Detection
```
User: "Find database query inefficiencies in recurring tasks"
Agent: [Triggers bug-error-detection skill] → Identifies N+1 queries and blocking operations in recurring task handlers, provides optimization recommendations
```

### Example 3: Multi-User Isolation Verification
```
User: "Verify user isolation in task access"
Agent: [Triggers bug-error-detection skill] → Checks all task-related queries and API endpoints, identifies potential breaches, generates test cases to verify fixes
```

## Quality Checklist

- [ ] Scans for JWT security vulnerabilities (algorithm, expiration, validation)
- [ ] Detects database query inefficiencies (N+1, blocking operations)
- [ ] Verifies multi-user isolation in queries and endpoints
- [ ] Checks for proper error handling and logging
- [ ] Identifies frontend security vulnerabilities (XSS, CSRF)
- [ ] Provides reproducible steps for each issue
- [ ] Prioritizes fixes by severity and impact
- [ ] Ensures compliance with no-manual-code rules
- [ ] Generates test cases to verify fixes
- [ ] Follows SDD and TDD principles

## Integration Points

- **Security Auditing**: Integrates with security review processes
- **Performance Monitoring**: Identifies bottlenecks for optimization
- **Testing Framework**: Generates test cases for bug verification
- **CI/CD Pipeline**: Automated security and performance checks
- **Code Review**: Provides detailed issue reports for review

## References

- **Security Guidelines**: `@specs/features/authentication.md` for security scanning
- **Database Spec**: `@specs/database/schema.md` for query optimization
- **API Spec**: `@specs/api/rest-endpoints.md` for endpoint validation
- **Authentication Spec**: `@specs/features/authentication.md` for JWT implementation
- **Testing Spec**: `@specs/testing/backend-testing.md` for test case generation