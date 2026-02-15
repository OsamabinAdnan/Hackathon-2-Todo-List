#!/usr/bin/env python3
"""
Database Isolation Checker Script

This script analyzes database queries in code to verify proper user isolation
through user_id filters and foreign key relationships.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class DatabaseIsolationVisitor(ast.NodeVisitor):
    """AST visitor to detect database queries and check for user isolation."""

    def __init__(self):
        self.database_queries = []
        self.missing_user_filters = []
        self.potential_isolation_issues = []

    def visit_Call(self, node):
        # Look for database query patterns
        if self._is_database_query(node):
            query_info = {
                'line': node.lineno,
                'function': self._get_function_name(node),
                'arguments': self._get_arguments(node),
                'has_user_filter': self._has_user_filter(node),
                'context': self._get_context(node)
            }

            self.database_queries.append(query_info)

            if not query_info['has_user_filter']:
                self.missing_user_filters.append(query_info)

        self.generic_visit(node)

    def _is_database_query(self, node) -> bool:
        """Check if this is a database query call."""
        func_name = self._get_function_name(node)

        # Common database query patterns
        db_methods = [
            'query', 'filter', 'filter_by', 'get', 'select', 'execute',
            'fetch', 'find', 'all', 'first', 'one', 'where', 'join'
        ]

        return any(method in func_name.lower() for method in db_methods)

    def _get_function_name(self, node) -> str:
        """Extract the function/method name from a call."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return str(node.func)

    def _get_arguments(self, node) -> List[str]:
        """Extract argument names/values from a call."""
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Attribute):
                args.append(f"{arg.value.id}.{arg.attr}" if isinstance(arg.value, ast.Name) else arg.attr)
        return args

    def _has_user_filter(self, node) -> bool:
        """Check if the query has proper user isolation (user_id filter)."""
        # Look for user_id in arguments or chained calls
        query_str = ast.unparse(node)

        # Check for user_id patterns in the query
        user_id_patterns = [
            r'\.filter.*user_id',
            r'\.filter_by.*user_id',
            r'where.*user_id',
            r'and_.*user_id',
            r'user_id.*==',
            r'user_id.*in'
        ]

        for pattern in user_id_patterns:
            if re.search(pattern, query_str, re.IGNORECASE):
                return True

        # Check if user_id is passed as a parameter (more complex check needed)
        return self._check_for_user_id_parameter(node)

    def _check_for_user_id_parameter(self, node) -> bool:
        """More sophisticated check for user_id parameter."""
        # This is a simplified version - in practice, you'd need more complex analysis
        # to trace where the user_id comes from
        query_str = ast.unparse(node).lower()
        return 'user_id' in query_str or 'userid' in query_str

    def _get_context(self, node) -> str:
        """Extract context around the node for reporting."""
        return f"Line {node.lineno}"


def scan_file_for_database_isolation(file_path: Path) -> Dict:
    """Scan a single file for database isolation issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)

        visitor = DatabaseIsolationVisitor()
        visitor.visit(tree)

        return {
            'file': str(file_path),
            'database_queries': visitor.database_queries,
            'missing_user_filters': visitor.missing_user_filters,
            'potential_isolation_issues': visitor.potential_isolation_issues
        }
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
        return {'file': str(file_path), 'error': str(e)}


def scan_directory(directory: Path, extensions: List[str] = ['.py']) -> List[Dict]:
    """Scan a directory for database isolation issues."""
    results = []

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            result = scan_file_for_database_isolation(file_path)
            if result.get('database_queries'):
                results.append(result)

    return results


def print_report(results: List[Dict]):
    """Print a formatted report of database isolation issues."""
    print("=" * 80)
    print("DATABASE ISOLATION AUDIT REPORT")
    print("=" * 80)

    total_queries = 0
    total_missing_filters = 0

    for result in results:
        if 'error' in result:
            print(f"\n❌ Error scanning {result['file']}: {result['error']}")
            continue

        print(f"\n📁 File: {result['file']}")

        if result['database_queries']:
            print(f"  📊 Total Queries Found: {len(result['database_queries'])}")

            for query in result['database_queries']:
                status = "✅ Isolated" if query['has_user_filter'] else "🚨 Missing Filter"
                print(f"    • {status} - Line {query['line']}: {query['function']}")

                if not query['has_user_filter']:
                    total_missing_filters += 1

                total_queries += 1

        if not result['database_queries']:
            print("  ℹ️  No database queries detected")

    print(f"\n📊 Summary:")
    print(f"  Total Queries Analyzed: {total_queries}")
    print(f"  Queries Missing User Filters: {total_missing_filters}")

    if total_missing_filters > 0:
        print(f"  ⚠️  {total_missing_filters} queries may have isolation issues!")
    else:
        print(f"  ✅ All queries appear to have proper user isolation")

    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python database_isolation_checker.py <directory_path>")
        sys.exit(1)

    directory_path = Path(sys.argv[1])
    if not directory_path.exists():
        print(f"Directory {directory_path} does not exist!")
        sys.exit(1)

    print(f"Scanning {directory_path} for database isolation issues...")
    results = scan_directory(directory_path)
    print_report(results)


if __name__ == "__main__":
    main()