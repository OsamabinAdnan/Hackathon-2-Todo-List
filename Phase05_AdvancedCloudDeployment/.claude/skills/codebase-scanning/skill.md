---
name: codebase-scanning
description: Comprehensive codebase analysis using Glob and Grep to identify syntax errors, logical bugs, and inconsistencies with specifications. Scans all files in frontend/, backend/, specs/ and outputs structured reports with severity levels, file/line references, and explanations for code review delegation. Use when (1) Performing initial code quality assessment across the entire codebase, (2) Identifying syntax errors and logical bugs in recently modified files, (3) Checking for inconsistencies between implementation and specifications, (4) Generating structured reports for main agent delegation, (5) Verifying adherence to multi-user isolation and no-manual-code rules.
---

# Codebase Scanning Skill

Comprehensive analysis of the Todo application codebase using advanced search and pattern matching to identify potential issues and ensure specification compliance.

## Core Capabilities

### 1. Multi-Directory Analysis

Scan across all relevant directories simultaneously:

```bash
# Scan frontend directory for issues
grep -r "console.log" frontend/ --include="*.ts" --include="*.tsx"

# Scan backend for potential security issues
grep -r "password\|token\|secret" backend/ --include="*.py"

# Cross-reference specs for consistency
grep -r "priority" specs/ --include="*.md"
```

**Python Implementation for FastAPI Backend:**
```python
import subprocess
from pathlib import Path
from typing import List, Dict, Any

def scan_backend_issues() -> List[Dict[str, Any]]:
    """Scan backend directory for common issues."""
    issues = []

    # Find Python files
    result = subprocess.run([
        "grep", "-r", "-n",
        "--include=*.py",
        "print(", "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if ':' in line:
                file_path, line_num, code = line.split(':', 2)
                issues.append({
                    'file': file_path,
                    'line': int(line_num),
                    'type': 'debug_print',
                    'severity': 'medium',
                    'description': f'Debug print statement found: {code.strip()}'
                })

    return issues
```

**TypeScript Implementation for Next.js Frontend:**
```typescript
import { execSync } from 'child_process';

function scanFrontendIssues(): Array<{
  file: string;
  line: number;
  type: string;
  severity: string;
  description: string;
}> {
  const issues = [];

  // Find potential XSS issues
  const xssResult = execSync('grep -r -n "innerHTML\\|eval\\|dangerouslySetInnerHTML" frontend/ --include="*.ts" --include="*.tsx"', { encoding: 'utf-8' });

  if (xssResult) {
    xssResult.trim().split('\n').forEach(line => {
      if (line.includes(':')) {
        const [filePath, lineNum, code] = line.split(':', 3);
        issues.push({
          file: filePath,
          line: parseInt(lineNum),
          type: 'potential_xss',
          severity: 'critical',
          description: `Potential XSS vulnerability: ${code.trim()}`
        });
      }
    });
  }

  return issues;
}
```

### 2. Specification Compliance Checking

Cross-reference implementation against specifications:

**Checking Task Model Against Database Schema:**
```python
def check_task_model_compliance():
    """Verify Task model matches database schema spec."""
    from sqlmodel import SQLModel, Field
    import inspect

    # Read the spec file
    with open('specs/database/schema.md', 'r') as f:
        spec_content = f.read()

    # Read the actual model
    with open('backend/app/models.py', 'r') as f:
        model_content = f.read()

    issues = []

    # Check for missing fields mentioned in spec
    required_fields = ['id', 'user_id', 'title', 'completed', 'created_at']
    for field in required_fields:
        if field not in model_content:
            issues.append({
                'type': 'missing_field',
                'severity': 'critical',
                'description': f'Task model missing required field: {field}',
                'spec_reference': 'specs/database/schema.md'
            })

    # Check for priority field if mentioned in spec
    if 'priority' in spec_content and 'priority' not in model_content:
        issues.append({
            'type': 'missing_priority_field',
            'severity': 'high',
            'description': 'Priority field mentioned in spec but missing from Task model',
            'spec_reference': 'specs/database/schema.md'
        })

    return issues
```

### 3. Logical Bug Detection

Identify common logical errors:

**Authentication Bypass Detection:**
```python
def scan_auth_bypass():
    """Scan for potential authentication bypass issues."""
    issues = []

    # Look for routes without authentication
    result = subprocess.run([
        "grep", "-r", "-n", "-A", "5", "-B", "5",
        "def.*get\\|def.*post\\|def.*put\\|def.*delete",
        "backend/app/api/"
    ], capture_output=True, text=True)

    # Check for missing auth decorators
    if 'def ' in result.stdout:
        # Additional logic to check for missing authentication
        pass

    return issues
```

**Database Query Inefficiency Detection:**
```python
def scan_n_plus_1_queries():
    """Scan for potential N+1 query problems."""
    issues = []

    # Look for patterns that might indicate N+1 queries
    result = subprocess.run([
        "grep", "-r", "-n", "-C", "3",
        "for.*in.*session.exec\\|for.*in.*db.query",
        "backend/"
    ], capture_output=True, text=True)

    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            if 'for ' in line and ('session.exec' in line or 'db.query' in line):
                issues.append({
                    'type': 'potential_n_plus_1',
                    'severity': 'high',
                    'description': f'Potential N+1 query pattern detected: {line.strip()}',
                    'recommendation': 'Use eager loading with selectinload or joinedload'
                })

    return issues
```

### 4. Multi-User Isolation Verification

Check for proper user isolation:

```python
def scan_user_isolation_issues():
    """Verify multi-user isolation in database queries."""
    issues = []

    # Look for queries that don't filter by user_id
    result = subprocess.run([
        "grep", "-r", "-n", "-C", "3",
        "SELECT\\|select\\|exec\\|session.",
        "backend/"
    ], capture_output=True, text=True)

    suspicious_patterns = []
    for line in result.stdout.strip().split('\n'):
        if ('Task' in line or 'task' in line) and 'user_id' not in line.lower():
            suspicious_patterns.append(line)

    if suspicious_patterns:
        issues.append({
            'type': 'potential_user_isolation_breach',
            'severity': 'critical',
            'description': 'Found potential user isolation breaches in database queries',
            'details': suspicious_patterns,
            'recommendation': 'Ensure all queries filter by user_id to maintain isolation'
        })

    return issues
```

### 5. Structured Reporting

Generate comprehensive reports with proper categorization:

```python
def generate_scan_report():
    """Generate a comprehensive scan report."""
    report = {
        'summary': {
            'total_files_scanned': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        },
        'critical_issues': [],
        'high_issues': [],
        'medium_issues': [],
        'low_issues': [],
        'compliance_status': {
            'spec_compliance': True,
            'security_compliance': True,
            'performance_compliance': True
        },
        'recommendations': []
    }

    # Run all scan functions
    issues = []
    issues.extend(scan_backend_issues())
    issues.extend(scan_user_isolation_issues())
    issues.extend(scan_n_plus_1_queries())
    issues.extend(check_task_model_compliance())

    # Categorize issues by severity
    for issue in issues:
        severity = issue.get('severity', 'medium')
        if severity == 'critical':
            report['critical_issues'].append(issue)
            report['summary']['critical_issues'] += 1
        elif severity == 'high':
            report['high_issues'].append(issue)
            report['summary']['high_issues'] += 1
        elif severity == 'medium':
            report['medium_issues'].append(issue)
            report['summary']['medium_issues'] += 1
        else:
            report['low_issues'].append(issue)
            report['summary']['low_issues'] += 1

    # Update compliance status
    report['compliance_status']['spec_compliance'] = report['summary']['critical_issues'] == 0
    report['compliance_status']['security_compliance'] = not any(
        issue for issue in issues if issue.get('type') in ['potential_xss', 'potential_user_isolation_breach', 'auth_bypass']
    )

    # Generate recommendations
    if report['summary']['critical_issues'] > 0:
        report['recommendations'].append("Address all critical issues immediately before proceeding")
    if report['summary']['high_issues'] > 0:
        report['recommendations'].append("Fix high severity issues before deployment")
    if report['summary']['medium_issues'] > 0:
        report['recommendations'].append("Review medium severity issues for potential improvements")

    return report

# Example usage
if __name__ == "__main__":
    report = generate_scan_report()
    print(f"Scan completed. Found {report['summary']['critical_issues']} critical, "
          f"{report['summary']['high_issues']} high, "
          f"{report['summary']['medium_issues']} medium, "
          f"{report['summary']['low_issues']} low severity issues")
```

### 6. Integration with Code Review Process

Example integration with the code-reviewer agent:

```python
def run_codebase_scan_for_review(file_paths=None):
    """
    Run codebase scan specifically for code review purposes.

    Args:
        file_paths: Optional list of specific files to scan. If None, scans entire codebase.
    """
    if file_paths:
        # Scan only specific files
        print(f"Scanning {len(file_paths)} specific files...")
        # Implementation for specific file scanning
    else:
        # Full codebase scan
        print("Running comprehensive codebase scan...")
        report = generate_scan_report()

        # Format for code reviewer
        formatted_issues = []
        for severity_level in ['critical', 'high', 'medium', 'low']:
            issues = report[f'{severity_level}_issues']
            for issue in issues:
                formatted_issue = f"[{severity_level.upper()}] {issue.get('description', 'No description')}"
                if 'file' in issue:
                    formatted_issue += f" ({issue['file']}"
                    if 'line' in issue:
                        formatted_issue += f":{issue['line']}"
                    formatted_issue += ")"
                formatted_issues.append(formatted_issue)

        return {
            'status': 'completed',
            'issues_found': sum(report['summary'].values()) - report['summary']['total_files_scanned'],
            'formatted_issues': formatted_issues,
            'compliance_status': report['compliance_status']
        }
```

## Usage Examples

### Example 1: Full Codebase Scan
```
User: "Run a comprehensive scan of the entire codebase"
Agent: [Triggers codebase-scanning skill] → Scans frontend/, backend/, specs/ directories, identifies 3 critical issues (user isolation), 5 high issues (security), generates detailed report with file:line references
```

### Example 2: Pre-Commit Verification
```
User: "Check my recent changes for compliance with specs"
Agent: [Triggers codebase-scanning skill] → Focuses on recently modified files, cross-references with specs/database/schema.md, verifies multi-user isolation, reports 2 medium issues with recommendations
```

### Example 3: Specification Compliance Check
```
User: "Verify the Task model matches the database schema spec"
Agent: [Triggers codebase-scanning skill] → Compares backend/app/models.py with specs/database/schema.md, identifies missing priority field, generates fix recommendation
```

## Quality Checklist

- [ ] Scan covers all relevant directories (frontend/, backend/, specs/)
- [ ] Issues categorized by severity (critical, high, medium, low)
- [ ] File and line number references provided for all issues
- [ ] Cross-references with specification files
- [ ] Checks for multi-user isolation compliance
- [ ] Identifies potential security vulnerabilities
- [ ] Detects performance issues (N+1 queries, etc.)
- [ ] Reports are structured and actionable
- [ ] No manual code rule is enforced
- [ ] Follows SDD and TDD principles

## Integration Points

- **Code Review Agent**: Provides initial scan results for detailed review
- **Spec Verification**: Ensures implementation matches approved specifications
- **Pre-Commit Hooks**: Can be integrated into development workflow
- **CI/CD Pipeline**: Automated scanning during build process

## References

- **Database Spec**: `@specs/database/schema.md` for schema compliance
- **API Spec**: `@specs/api/rest-endpoints.md` for API contract verification
- **Authentication Spec**: `@specs/features/authentication.md` for security scanning
- **Frontend Guidelines**: `@specs/ui/accessibility.md` for UI/UX compliance
- **Testing Guidelines**: `@specs/testing/overview.md` for testing compliance