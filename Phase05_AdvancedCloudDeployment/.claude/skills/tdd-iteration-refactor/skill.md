---
name: tdd-iteration-refactor
description: Upon test failures, generate refined Markdown specs for domain subagents to implement green/refactor phases. Suggest refactors for cleaner code (e.g., modular components, optimized SQLModel queries) while preserving intent. Loop with code reviewer until 100% pass rate; enforce no manual edits, full spec-driven compliance for hackathon judging. Use when (1) Generating refined specs for test failures during green/refactor phases, (2) Suggesting code refactors for cleaner, more maintainable code, (3) Creating modular components and optimized database queries, (4) Enforcing no manual edits and spec-driven compliance, (5) Looping with code reviewer until 100% test pass rate, (6) Ensuring hackathon judging criteria compliance.
---

# TDD Iteration and Refactor Skill

Advanced test-driven development iteration and refactoring for maintaining clean, maintainable code while preserving functionality and ensuring full spec-driven compliance.

## Core Capabilities

### 1. Failure-Driven Spec Refinement

Generate refined specifications based on test failures:

**Markdown Spec Generation:**
```markdown
# Refined Specification: Task Creation Feature

## Original Spec
@specs/features/task-crud.md - Task creation with validation

## Test Failures Analysis
- `test_create_task_with_empty_title_fails_validation` - Expected validation error, got 201
- `test_create_task_with_long_title_truncated` - Expected truncation, got validation error
- `test_create_task_sets_default_values` - Expected default completed=False, got True

## Refined Requirements

### 1. Input Validation
**Before**: Title validation exists
**After**:
- Title must be 1-200 characters
- Empty titles return 422 validation error
- Titles over 200 characters return 422 validation error
- Trimmed whitespace titles of 0 length return 422 validation error

### 2. Default Values
**Before**: Default values handled inconsistently
**After**:
- `completed` defaults to `False`
- `created_at` defaults to current timestamp
- `updated_at` defaults to current timestamp
- `priority` defaults to `"NONE"`

### 3. Error Responses
**Before**: Generic error responses
**After**:
- Validation errors return 422 with detailed error messages
- Error response format: `{ "error": "Validation failed", "details": { "field": "reason" } }`
- Include specific field validation errors

## Implementation Tasks
1. Update Task model validation rules
2. Add API endpoint validation
3. Update error response format
4. Add comprehensive validation tests
```

**Python Implementation Spec:**
```python
# Generated refined implementation specification
"""
Refined Implementation: Task Creation with Validation

Based on test failures, implement the following requirements:

1. Model Validation:
   - Task.title: Required, 1-200 characters, trimmed
   - Task.completed: Default False
   - Task.priority: Default "NONE", enum validation

2. API Validation:
   - Return 422 for validation errors
   - Include detailed error messages
   - Validate on POST /api/{user_id}/tasks

3. Error Response Format:
   - Standardized error responses
   - Field-specific validation errors
   - Proper HTTP status codes
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class PriorityEnum(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NONE = "NONE"

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title (1-200 chars)")
    description: Optional[str] = Field(None, max_length=1000)
    completed: bool = Field(default=False)
    priority: PriorityEnum = Field(default=PriorityEnum.NONE)

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or just whitespace')
        if len(v.strip()) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()

# API endpoint implementation
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session

def create_task_endpoint(
    user_id: str,
    task_request: TaskCreateRequest,
    session: Session = Depends(get_session)
):
    """
    POST /api/{user_id}/tasks endpoint with proper validation
    """
    try:
        # Create task with validated data
        task = Task(
            title=task_request.title,
            description=task_request.description,
            completed=task_request.completed,
            priority=task_request.priority,
            user_id=user_id
        )

        session.add(task)
        session.commit()
        session.refresh(task)

        return task

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail={"error": "Validation failed", "message": str(e)}
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e)}
        )
```

### 2. Refactoring Suggestions

Provide intelligent refactoring suggestions:

**Code Quality Refactoring:**
```python
# Before: Complex, hard-to-test function
def process_user_tasks(user_id, filter_type, sort_order, limit=50):
    # Multiple responsibilities in one function
    tasks = session.query(Task).filter(Task.user_id == user_id)

    if filter_type == 'completed':
        tasks = tasks.filter(Task.completed == True)
    elif filter_type == 'pending':
        tasks = tasks.filter(Task.completed == False)
    elif filter_type == 'high_priority':
        tasks = tasks.filter(Task.priority == 'HIGH')

    if sort_order == 'date':
        tasks = tasks.order_by(Task.created_at.desc())
    elif sort_order == 'priority':
        tasks = tasks.order_by(Task.priority)

    return tasks.limit(limit).all()

# After: Clean, modular, testable functions
from enum import Enum
from typing import Optional
from sqlalchemy.orm import Query

class TaskFilter(Enum):
    ALL = "all"
    COMPLETED = "completed"
    PENDING = "pending"
    HIGH_PRIORITY = "high_priority"

class TaskSort(Enum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    PRIORITY = "priority"

def build_task_query(
    session,
    user_id: str,
    filter_type: Optional[TaskFilter] = None,
    sort_order: Optional[TaskSort] = None
) -> Query:
    """Build task query with specified filters and sorting."""
    query = session.query(Task).filter(Task.user_id == user_id)

    # Apply filters
    if filter_type:
        query = _apply_task_filter(query, filter_type)

    # Apply sorting
    if sort_order:
        query = _apply_task_sorting(query, sort_order)

    return query

def _apply_task_filter(query: Query, filter_type: TaskFilter) -> Query:
    """Apply filter to task query."""
    filter_mapping = {
        TaskFilter.COMPLETED: lambda q: q.filter(Task.completed == True),
        TaskFilter.PENDING: lambda q: q.filter(Task.completed == False),
        TaskFilter.HIGH_PRIORITY: lambda q: q.filter(Task.priority == 'HIGH')
    }

    if filter_type in filter_mapping:
        return filter_mapping[filter_type](query)

    return query

def _apply_task_sorting(query: Query, sort_order: TaskSort) -> Query:
    """Apply sorting to task query."""
    sort_mapping = {
        TaskSort.DATE_DESC: lambda q: q.order_by(Task.created_at.desc()),
        TaskSort.DATE_ASC: lambda q: q.order_by(Task.created_at.asc()),
        TaskSort.PRIORITY: lambda q: q.order_by(Task.priority)
    }

    if sort_order in sort_mapping:
        return sort_mapping[sort_order](query)

    return query

def get_filtered_tasks(
    session,
    user_id: str,
    filter_type: Optional[TaskFilter] = None,
    sort_order: Optional[TaskSort] = None,
    limit: int = 50
) -> list:
    """Get filtered and sorted tasks with limit."""
    query = build_task_query(session, user_id, filter_type, sort_order)
    return query.limit(limit).all()
```

**Frontend Component Refactoring:**
```typescript
// Before: Complex, untestable component
const TaskList = ({ tasks, onToggle, onDelete, filter, sort }) => {
  const [localTasks, setLocalTasks] = useState(tasks);

  useEffect(() => {
    let filtered = [...tasks];

    if (filter === 'completed') {
      filtered = filtered.filter(t => t.completed);
    } else if (filter === 'pending') {
      filtered = filtered.filter(t => !t.completed);
    }

    if (sort === 'priority') {
      filtered.sort((a, b) => priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority));
    } else if (sort === 'date') {
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    setLocalTasks(filtered);
  }, [tasks, filter, sort]);

  return (
    <div className="task-list">
      {localTasks.map(task => (
        <div key={task.id} className="task-item">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={() => onToggle(task.id)}
          />
          <span>{task.title}</span>
          <button onClick={() => onDelete(task.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
};

// After: Modular, testable components with custom hooks
import { useState, useEffect, useMemo } from 'react';

// Custom hook for task filtering and sorting
const useFilteredTasks = (tasks, filter, sort) => {
  return useMemo(() => {
    let filtered = [...tasks];

    // Apply filter
    if (filter === 'completed') {
      filtered = filtered.filter(t => t.completed);
    } else if (filter === 'pending') {
      filtered = filtered.filter(t => !t.completed);
    }

    // Apply sort
    if (sort === 'priority') {
      filtered.sort((a, b) => priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority));
    } else if (sort === 'date') {
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    return filtered;
  }, [tasks, filter, sort]);
};

// Separate task item component
const TaskItem = ({ task, onToggle, onDelete }) => {
  return (
    <div className="task-item">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
      />
      <span className={task.completed ? 'completed' : ''}>{task.title}</span>
      <button onClick={() => onDelete(task.id)}>Delete</button>
    </div>
  );
};

// Main component with separated concerns
const TaskList = ({ tasks, onToggle, onDelete, filter, sort }) => {
  const filteredTasks = useFilteredTasks(tasks, filter, sort);

  return (
    <div className="task-list">
      {filteredTasks.map(task => (
        <TaskItem
          key={task.id}
          task={task}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};
```

### 3. Database Query Optimization

Optimize SQLModel queries:

**Before: Inefficient Query Pattern**
```python
# Inefficient: Multiple queries in a loop (N+1 problem)
def get_user_tasks_with_details(user_id: str):
    tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

    result = []
    for task in tasks:
        # Separate query for each task - N+1 problem!
        user = session.get(User, task.user_id)  # Additional query
        category = session.get(Category, task.category_id)  # Additional query

        result.append({
            'task': task,
            'user': user,
            'category': category
        })

    return result
```

**After: Optimized Query Pattern**
```python
# Efficient: Single query with joined data
from sqlmodel import select
from sqlalchemy.orm import selectinload

def get_user_tasks_with_details_optimized(user_id: str):
    """
    Get user tasks with related data using optimized query.

    Uses selectinload to prevent N+1 query problem.
    """
    # Single query with eager loading
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .options(
            selectinload(Task.user),      # Eager load user relationship
            selectinload(Task.category)   # Eager load category relationship
        )
    )

    tasks = session.exec(statement).all()

    return [
        {
            'task': task,
            'user': task.user,        # Already loaded, no additional query
            'category': task.category  # Already loaded, no additional query
        }
        for task in tasks
    ]

# Alternative: Using joinedload for fewer queries
from sqlalchemy.orm import joinedload

def get_user_tasks_with_joinedload(user_id: str):
    """
    Alternative optimization using joinedload.
    """
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .options(
            joinedload(Task.user),
            joinedload(Task.category)
        )
    )

    return session.exec(statement).all()
```

**Index Optimization Suggestions:**
```python
# Model with optimized indexes for common query patterns
from sqlmodel import Field, SQLModel, create_engine
from sqlalchemy import Index

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_tasks_user_completed", "user_id", "completed"),  # Common filter
        Index("ix_tasks_user_priority", "user_id", "priority"),    # Priority filtering
        Index("ix_tasks_user_created_at", "user_id", "created_at"), # Date sorting
        Index("ix_tasks_user_due_date", "user_id", "due_date"),    # Due date queries
    )

    id: str = Field(primary_key=True)
    user_id: str = Field(index=True)  # Individual index for joins
    title: str = Field(max_length=200, index=True)  # For search
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False, index=True)
    priority: str = Field(default="NONE", index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 4. Test-Driven Refactoring Loop

Implement the TDD refactoring loop:

**Refactoring Process:**
```python
def tdd_refactor_process(failing_test_analysis: Dict[str, Any]) -> str:
    """
    Generate refactoring specification based on failing test analysis.

    Args:
        failing_test_analysis: Analysis of why tests are failing

    Returns:
        Markdown specification for refactoring
    """
    spec = f"""
# Refactoring Specification: {failing_test_analysis['feature']}

## Problem Analysis
**Failed Tests**: {len(failing_test_analysis['failures'])}
**Root Causes**:
"""

    for failure in failing_test_analysis['failures']:
        spec += f"- {failure['test_name']}: {failure['reason']}\n"

    spec += f"""

## Refactoring Strategy

### 1. Immediate Fixes
- [ ] Fix validation logic for {failing_test_analysis['validation_issues']}
- [ ] Update error handling for {failing_test_analysis['error_issues']}
- [ ] Correct default values for {failing_test_analysis['default_issues']}

### 2. Code Quality Improvements
- [ ] Extract {failing_test_analysis['complex_functions']} to separate functions
- [ ] Add type hints to {failing_test_analysis['untyped_functions']}
- [ ] Improve error messages in {failing_test_analysis['error_prone_areas']}

### 3. Performance Optimizations
- [ ] Add database indexes for {failing_test_analysis['performance_issues']}
- [ ] Optimize queries in {failing_test_analysis['query_issues']}
- [ ] Implement caching for {failing_test_analysis['repeated_operations']}

## Implementation Plan
1. **Red Phase**: Update tests to reflect corrected behavior
2. **Green Phase**: Implement fixes to make tests pass
3. **Refactor Phase**: Improve code quality while keeping tests green

## Success Criteria
- [ ] All previously failing tests now pass
- [ ] Code coverage remains at or above current level
- [ ] Performance metrics meet requirements
- [ ] Code quality scores improve
- [ ] No new test failures introduced

## Review Checklist
- [ ] Changes preserve original functionality
- [ ] New code follows project standards
- [ ] Error handling is comprehensive
- [ ] Security requirements are maintained
- [ ] Performance hasn't regressed
"""

    return spec

def generate_refactored_implementation(refactoring_spec: str) -> str:
    """
    Generate refactored implementation based on specification.
    """
    implementation = f"""
# Refactored Implementation Based on Specification

## Updated Model
```python
# Updated model with proper validation and optimization
class Task(SQLModel, table=True):
    # Implementation details based on refactoring spec
    pass
```

## Updated API Endpoints
```python
# Updated endpoints with proper error handling
@router.post("/tasks")
def create_task():
    # Implementation based on spec
    pass
```

## Updated Tests
```python
# Additional tests to verify refactoring success
def test_refactored_functionality():
    # Tests based on refactoring requirements
    pass
```
"""

    return implementation
```

### 5. Code Review Integration

Integrate with code review process:

**Review Integration Workflow:**
```python
def integrate_with_code_review(failing_tests: List[Dict], current_code: str) -> Dict[str, Any]:
    """
    Generate code review integration plan for failing tests.

    Args:
        failing_tests: List of failing tests with analysis
        current_code: Current implementation code

    Returns:
        Integration plan with review suggestions
    """
    review_plan = {
        "critical_issues": [],
        "refactoring_suggestions": [],
        "security_considerations": [],
        "performance_improvements": [],
        "next_steps": []
    }

    # Analyze each failing test for review integration
    for test in failing_tests:
        if test['severity'] == 'CRITICAL':
            review_plan['critical_issues'].append({
                "test": test['name'],
                "issue": test['analysis'],
                "fix_suggestion": generate_fix_suggestion(test['analysis'])
            })
        elif test['category'] == 'performance':
            review_plan['performance_improvements'].append({
                "test": test['name'],
                "performance_issue": test['analysis'],
                "optimization": suggest_optimization(test['analysis'])
            })
        elif test['category'] == 'security':
            review_plan['security_considerations'].append({
                "test": test['name'],
                "security_issue": test['analysis'],
                "security_fix": suggest_security_fix(test['analysis'])
            })

    # Generate refactoring suggestions
    review_plan['refactoring_suggestions'] = analyze_code_for_refactoring(current_code)

    # Create next steps
    review_plan['next_steps'] = [
        "Address critical issues first",
        "Run tests after each fix",
        "Refactor incrementally",
        "Verify all tests pass before proceeding"
    ]

    return review_plan

def generate_fix_suggestion(error_analysis: str) -> str:
    """Generate specific fix suggestion based on error analysis."""
    # Pattern matching for common error types
    if "validation" in error_analysis.lower():
        return "Add proper input validation with Pydantic models"
    elif "database" in error_analysis.lower():
        return "Check database connection and query optimization"
    elif "authentication" in error_analysis.lower():
        return "Verify JWT token validation and user permissions"
    elif "performance" in error_analysis.lower():
        return "Optimize queries and add appropriate indexes"
    else:
        return "Review the error details and implement appropriate fix"
```

### 6. Spec-Driven Compliance

Ensure full spec-driven compliance:

**Compliance Verification:**
```python
def verify_spec_compliance(implementation: str, specification: str) -> Dict[str, Any]:
    """
    Verify that implementation complies with specification.

    Args:
        implementation: Current implementation code
        specification: Original specification

    Returns:
        Compliance report with gaps and suggestions
    """
    compliance_report = {
        "compliance_score": 0,
        "requirements_met": [],
        "requirements_missing": [],
        "spec_violations": [],
        "suggestions": []
    }

    # Extract requirements from specification
    spec_requirements = extract_requirements_from_spec(specification)

    # Check implementation against each requirement
    for requirement in spec_requirements:
        if requirement_met_in_implementation(requirement, implementation):
            compliance_report['requirements_met'].append(requirement)
        else:
            compliance_report['requirements_missing'].append(requirement)

    # Check for spec violations (implementation doing more/less than spec)
    violations = find_spec_violations(implementation, specification)
    compliance_report['spec_violations'] = violations

    # Calculate compliance score
    total_requirements = len(spec_requirements)
    if total_requirements > 0:
        compliance_report['compliance_score'] = (
            len(compliance_report['requirements_met']) / total_requirements
        ) * 100

    # Generate suggestions for compliance
    if compliance_report['requirements_missing']:
        compliance_report['suggestions'].append(
            f"Implement missing requirements: {', '.join(compliance_report['requirements_missing'][:3])}"
        )

    if compliance_report['spec_violations']:
        compliance_report['suggestions'].append(
            f"Fix spec violations: {len(compliance_report['spec_violations'])} issues found"
        )

    return compliance_report

def extract_requirements_from_spec(spec_text: str) -> List[str]:
    """Extract specific requirements from specification text."""
    # Look for requirement patterns in spec
    import re

    # Common requirement patterns
    patterns = [
        r"SHOULD\s+(.+?)(?:\n|\.|$)",      # "SHOULD do something"
        r"MUST\s+(.+?)(?:\n|\.|$)",        # "MUST do something"
        r"REQUIRE[S]?\s+(.+?)(?:\n|\.|$)", # "REQUIRES something"
        r"NEED[S]?\s+(.+?)(?:\n|\.|$)",    # "NEEDS to do something"
    ]

    requirements = []
    for pattern in patterns:
        matches = re.findall(pattern, spec_text, re.IGNORECASE)
        requirements.extend(matches)

    return requirements

def requirement_met_in_implementation(requirement: str, implementation: str) -> bool:
    """Check if a requirement is met in the implementation."""
    # This is a simplified check - in practice, this would be more sophisticated
    # Look for keywords from requirement in implementation
    requirement_keywords = requirement.lower().split()

    # Simple keyword matching (would be enhanced in real implementation)
    implementation_lower = implementation.lower()
    return any(keyword in implementation_lower for keyword in requirement_keywords[:3])
```

### 7. Hackathon Judging Criteria Compliance

Ensure code meets hackathon standards:

**Quality Standards Verification:**
```python
def verify_hackathon_compliance(code: str) -> Dict[str, Any]:
    """
    Verify code meets hackathon judging criteria.

    Checks for clean architecture, maintainability, and best practices.
    """
    compliance_checklist = {
        "clean_architecture": {
            "score": 0,
            "issues": [],
            "suggestions": []
        },
        "code_quality": {
            "score": 0,
            "issues": [],
            "suggestions": []
        },
        "security": {
            "score": 0,
            "issues": [],
            "suggestions": []
        },
        "performance": {
            "score": 0,
            "issues": [],
            "suggestions": []
        },
        "maintainability": {
            "score": 0,
            "issues": [],
            "suggestions": []
        }
    }

    # Check for clean architecture patterns
    if has_separation_of_concerns(code):
        compliance_checklist["clean_architecture"]["score"] = 100
    else:
        compliance_checklist["clean_architecture"]["issues"].append(
            "Missing separation of concerns - business logic mixed with presentation"
        )
        compliance_checklist["clean_architecture"]["suggestions"].append(
            "Separate business logic, data access, and presentation layers"
        )

    # Check for code quality (type hints, error handling, etc.)
    quality_issues = check_code_quality(code)
    compliance_checklist["code_quality"]["issues"].extend(quality_issues)
    compliance_checklist["code_quality"]["suggestions"].extend(
        generate_quality_suggestions(quality_issues)
    )
    compliance_checklist["code_quality"]["score"] = calculate_quality_score(quality_issues)

    # Check for security best practices
    security_issues = check_security_practices(code)
    compliance_checklist["security"]["issues"].extend(security_issues)
    compliance_checklist["security"]["suggestions"].extend(
        generate_security_suggestions(security_issues)
    )
    compliance_checklist["security"]["score"] = calculate_security_score(security_issues)

    # Calculate overall compliance
    total_score = sum(
        section["score"] for section in compliance_checklist.values()
    ) / len(compliance_checklist)

    compliance_checklist["overall_score"] = total_score
    compliance_checklist["passing"] = total_score >= 80  # 80% threshold

    return compliance_checklist

def has_separation_of_concerns(code: str) -> bool:
    """Check if code has proper separation of concerns."""
    # Look for patterns that indicate good separation
    import re

    # Check for function/class names that suggest separation
    patterns_indicating_separation = [
        r'class.*Service',      # Service layer
        r'class.*Repository',   # Data access layer
        r'def.*validate',       # Validation functions
        r'def.*format',         # Formatting functions
        r'class.*Controller',   # Controller layer
        r'def.*to_dict',        # Data transformation
    ]

    for pattern in patterns_indicating_separation:
        if re.search(pattern, code, re.IGNORECASE):
            return True

    # Check for mixed concerns (bad sign)
    mixed_concerns_patterns = [
        r'fetch.*render',       # Data fetching mixed with rendering
        r'database.*response',  # DB operations mixed with HTTP responses
        r'validation.*print',   # Validation mixed with output
    ]

    for pattern in mixed_concerns_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False

    return False  # Default to False if no clear patterns found

def check_code_quality(code: str) -> List[str]:
    """Check code for quality issues."""
    issues = []

    # Check for type hints
    if not has_type_hints(code):
        issues.append("Missing type hints in functions and variables")

    # Check for error handling
    if not has_proper_error_handling(code):
        issues.append("Missing proper error handling and validation")

    # Check for function length
    if has_excessively_long_functions(code):
        issues.append("Functions are too long and should be broken down")

    # Check for complexity
    if has_complex_logic(code):
        issues.append("Complex logic should be simplified or broken down")

    return issues
```

### 8. Automated Refactoring Loop

Create an automated refactoring loop:

```python
def automated_refactoring_loop(
    failing_tests: List[Dict],
    current_implementation: str,
    specification: str
) -> Dict[str, Any]:
    """
    Automated refactoring loop that iterates until tests pass.

    Args:
        failing_tests: List of currently failing tests
        current_implementation: Current implementation code
        specification: Original specification

    Returns:
        Refactoring results with final status
    """
    results = {
        "iterations": 0,
        "final_status": "FAILED",
        "refactored_code": current_implementation,
        "tests_passing": False,
        "compliance_score": 0,
        "improvements_made": []
    }

    max_iterations = 10  # Prevent infinite loops
    current_code = current_implementation

    while failing_tests and results["iterations"] < max_iterations:
        results["iterations"] += 1

        # Analyze failures and generate refactoring plan
        refactoring_plan = analyze_failures_and_plan_refactor(failing_tests)

        # Apply refactoring to code
        refactored_code = apply_refactoring_plan(current_code, refactoring_plan)
        results["improvements_made"].append(refactoring_plan["summary"])

        # Test the refactored code (simulated)
        newly_passing_tests, still_failing_tests = test_refactored_code(
            refactored_code,
            failing_tests
        )

        # Update state
        current_code = refactored_code
        failing_tests = still_failing_tests

        # Log iteration results
        print(f"Iteration {results['iterations']}: {len(newly_passing_tests)} tests now pass, {len(failing_tests)} still failing")

        if not failing_tests:
            results["final_status"] = "SUCCESS"
            results["tests_passing"] = True
            break

    # Final compliance check
    compliance = verify_hackathon_compliance(current_code)
    results["compliance_score"] = compliance["overall_score"]
    results["refactored_code"] = current_code

    return results

def analyze_failures_and_plan_refactor(failing_tests: List[Dict]) -> Dict[str, Any]:
    """
    Analyze failing tests and create refactoring plan.
    """
    # Group failures by type
    failure_types = {}
    for test in failing_tests:
        failure_type = classify_failure_type(test['error'])
        if failure_type not in failure_types:
            failure_types[failure_type] = []
        failure_types[failure_type].append(test)

    # Create refactoring plan based on failure types
    plan = {
        "priority_fixes": [],
        "refactoring_tasks": [],
        "summary": f"Addressing {len(failing_tests)} failing tests across {len(failure_types)} categories"
    }

    for failure_type, tests in failure_types.items():
        if failure_type == "validation_error":
            plan["priority_fixes"].append("Fix input validation logic")
            plan["refactoring_tasks"].append({
                "type": "validation",
                "description": f"Update validation for {len(tests)} tests",
                "implementation": "Add proper Pydantic validation models"
            })
        elif failure_type == "database_error":
            plan["priority_fixes"].append("Fix database query issues")
            plan["refactoring_tasks"].append({
                "type": "database",
                "description": f"Optimize queries for {len(tests)} tests",
                "implementation": "Use proper SQLAlchemy/SQLModel patterns"
            })
        elif failure_type == "security_error":
            plan["priority_fixes"].append("Fix security validation")
            plan["refactoring_tasks"].append({
                "type": "security",
                "description": f"Add security checks for {len(tests)} tests",
                "implementation": "Implement proper authentication/authorization"
            })

    return plan
```

## Usage Examples

### Example 1: Green Phase Implementation
```
User: "Tests are failing, need to implement to make them pass"
Agent: [Triggers tdd-iteration-refactor skill] → Analyzes 5 failing tests, generates refined spec with validation requirements, provides implementation code that makes tests pass, maintains 100% spec compliance
```

### Example 2: Refactoring for Clean Code
```
User: "Refactor the task service for better maintainability"
Agent: [Triggers tdd-iteration-refactor skill] → Analyzes code quality issues, suggests separation of concerns, provides refactored implementation with improved architecture, maintains all test coverage
```

### Example 3: Performance Optimization
```
User: "Optimize database queries for better performance"
Agent: [Triggers tdd-iteration-refactor skill] → Identifies N+1 queries, suggests eager loading with selectinload, adds proper indexes, provides optimized implementation with performance tests
```

### Example 4: Spec Compliance Verification
```
User: "Verify implementation meets hackathon judging criteria"
Agent: [Triggers tdd-iteration-refactor skill] → Runs comprehensive compliance check, identifies architecture issues, suggests improvements for clean code, generates 95% compliance score
```

## Quality Checklist

- [ ] All refactoring preserves original functionality
- [ ] Code follows separation of concerns
- [ ] Type hints are properly implemented
- [ ] Error handling is comprehensive
- [ ] Database queries are optimized
- [ ] Performance hasn't regressed
- [ ] Security requirements are maintained
- [ ] Tests continue to pass after refactoring
- [ ] Code quality scores improve
- [ ] Specification compliance is maintained
- [ ] No manual edits bypass TDD process
- [ ] Refactoring is incremental and safe
- [ ] All changes are test-verified
- [ ] Hackathon judging criteria are met

## Integration Points

- **TDD Workflow**: Integrates with Red-Green-Refactor cycle
- **Code Review**: Provides refactoring suggestions for review
- **Testing Framework**: Maintains test coverage during refactoring
- **CI/CD Pipeline**: Automated refactoring and compliance checks
- **Spec-Driven Development**: Ensures spec compliance
- **Quality Gates**: Compliance verification before merging

## References

- **TDD Principles**: `@specs/testing/overview.md` for TDD workflow
- **Backend Testing**: `@specs/testing/backend-testing.md` for backend refactoring
- **Frontend Testing**: `@specs/testing/frontend-testing.md` for frontend refactoring
- **API Specifications**: `@specs/api/rest-endpoints.md` for API improvements
- **Database Schema**: `@specs/database/schema.md` for query optimization
- **Architecture Guidelines**: `@specs/overview.md` for clean architecture
- **Security Requirements**: `@specs/features/authentication.md` for security compliance
- **Performance Requirements**: `@specs/ui/animations.md` for optimization
- **Code Quality Standards**: `@specs/overview.md` for quality guidelines