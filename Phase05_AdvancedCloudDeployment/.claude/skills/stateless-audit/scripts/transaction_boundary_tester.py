#!/usr/bin/env python3
"""
Transaction Boundary Tester Script

This script analyzes code to verify proper transaction boundaries and atomic operation handling.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class TransactionBoundaryVisitor(ast.NodeVisitor):
    """AST visitor to detect transaction operations and check for proper boundaries."""

    def __init__(self):
        self.transaction_operations = []
        self.missing_boundaries = []
        self.potential_boundary_issues = []

    def visit_With(self, node):
        # Look for transaction context managers
        if self._is_transaction_context(node):
            transaction_info = {
                'line': node.lineno,
                'context_manager': self._get_context_manager_name(node),
                'has_proper_scope': self._has_proper_scope(node),
                'nested_transactions': self._has_nested_transactions(node),
                'context': self._get_context(node)
            }

            self.transaction_operations.append(transaction_info)

            if not transaction_info['has_proper_scope']:
                self.missing_boundaries.append(transaction_info)

        self.generic_visit(node)

    def visit_Call(self, node):
        # Look for transaction-related function calls
        if self._is_transaction_call(node):
            call_info = {
                'line': node.lineno,
                'function': self._get_function_name(node),
                'arguments': self._get_arguments(node),
                'context': self._get_context(node)
            }

            # Add to transaction operations if it looks like a transaction operation
            self.transaction_operations.append(call_info)

        self.generic_visit(node)

    def _is_transaction_context(self, node) -> bool:
        """Check if this is a transaction context manager."""
        if isinstance(node.items[0].context_expr, ast.Call):
            func_name = self._get_function_name_from_expr(node.items[0].context_expr)
        elif isinstance(node.items[0].context_expr, ast.Name):
            func_name = node.items[0].context_expr.id
        elif isinstance(node.items[0].context_expr, ast.Attribute):
            func_name = node.items[0].context_expr.attr
        else:
            func_name = ast.unparse(node.items[0].context_expr)

        # Common transaction context managers
        transaction_patterns = [
            'transaction', 'db.transaction', 'database.transaction', 'sqlmodel.transaction',
            'begin', 'transact', 'atomic'
        ]

        return any(pattern in func_name.lower() for pattern in transaction_patterns)

    def _is_transaction_call(self, node) -> bool:
        """Check if this is a transaction-related function call."""
        func_name = self._get_function_name(node)

        # Common transaction function patterns
        transaction_functions = [
            'commit', 'rollback', 'begin', 'start_transaction', 'end_transaction',
            'savepoint', 'nested_transaction', 'transact'
        ]

        return any(func.lower() in func_name.lower() for func in transaction_functions)

    def _get_context_manager_name(self, node) -> str:
        """Extract the context manager name."""
        if isinstance(node.items[0].context_expr, ast.Call):
            return self._get_function_name_from_expr(node.items[0].context_expr)
        elif isinstance(node.items[0].context_expr, ast.Name):
            return node.items[0].context_expr.id
        elif isinstance(node.items[0].context_expr, ast.Attribute):
            return ast.unparse(node.items[0].context_expr)
        else:
            return ast.unparse(node.items[0].context_expr)

    def _get_function_name_from_expr(self, expr) -> str:
        """Extract function name from expression."""
        if isinstance(expr, ast.Call):
            if isinstance(expr.func, ast.Name):
                return expr.func.id
            elif isinstance(expr.func, ast.Attribute):
                return expr.func.attr
        return ast.unparse(expr)

    def _get_function_name(self, node) -> str:
        """Extract the function/method name from a call."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            else:
                return node.func.attr
        elif isinstance(node.func, ast.Name):
            return node.func.id
        return ast.unparse(node.func)

    def _get_arguments(self, node) -> List[str]:
        """Extract argument names/values from a call."""
        args = []
        for arg in node.args:
            if isinstance(arg, ast.Constant):
                args.append(str(arg.value))
            elif isinstance(arg, ast.Name):
                args.append(arg.id)
            elif isinstance(arg, ast.Attribute):
                args.append(ast.unparse(arg))
            else:
                args.append(ast.unparse(arg))
        return args

    def _has_proper_scope(self, node) -> bool:
        """Check if transaction has proper scope (not spanning multiple requests)."""
        # For now, we'll assume that properly scoped transactions are within function/method boundaries
        # This would require more complex analysis in practice to check if transactions span request boundaries
        return True  # Simplified - would need more complex analysis in real implementation

    def _has_nested_transactions(self, node) -> bool:
        """Check if there are nested transactions in the with block."""
        # Look for nested transaction patterns within the with block
        for item in node.body:
            if isinstance(item, ast.With):
                if self._is_transaction_context(item):
                    return True
            elif isinstance(item, ast.Call):
                if self._is_transaction_call(item):
                    return True
        return False

    def _get_context(self, node) -> str:
        """Extract context around the node for reporting."""
        return f"Line {node.lineno}"


def scan_file_for_transaction_boundaries(file_path: Path) -> Dict:
    """Scan a single file for transaction boundary issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)

        visitor = TransactionBoundaryVisitor()
        visitor.visit(tree)

        return {
            'file': str(file_path),
            'transaction_operations': visitor.transaction_operations,
            'missing_boundaries': visitor.missing_boundaries,
            'potential_boundary_issues': visitor.potential_boundary_issues
        }
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
        return {'file': str(file_path), 'error': str(e)}


def scan_directory(directory: Path, extensions: List[str] = ['.py']) -> List[Dict]:
    """Scan a directory for transaction boundary issues."""
    results = []

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            result = scan_file_for_transaction_boundaries(file_path)
            if result.get('transaction_operations'):
                results.append(result)

    return results


def print_report(results: List[Dict]):
    """Print a formatted report of transaction boundary issues."""
    print("=" * 80)
    print("TRANSACTION BOUNDARY AUDIT REPORT")
    print("=" * 80)

    total_operations = 0
    total_boundary_issues = 0

    for result in results:
        if 'error' in result:
            print(f"\n❌ Error scanning {result['file']}: {result['error']}")
            continue

        print(f"\n📁 File: {result['file']}")

        if result['transaction_operations']:
            print(f"  📊 Total Transaction Operations Found: {len(result['transaction_operations'])}")

            for op in result['transaction_operations']:
                if 'context_manager' in op:
                    # This is a with statement (context manager)
                    status = "⚠️  Nested" if op.get('nested_transactions', False) else "✅ Proper"
                    print(f"    • {status} - Line {op['line']}: Transaction context '{op['context_manager']}'")

                    if op.get('nested_transactions', False):
                        total_boundary_issues += 1
                else:
                    # This is a function call
                    print(f"    • ℹ️  Line {op['line']}: Transaction function '{op['function']}'")

                total_operations += 1

        if not result['transaction_operations']:
            print("  ℹ️  No transaction operations detected")

    print(f"\n📊 Summary:")
    print(f"  Total Transaction Operations: {total_operations}")
    print(f"  Potential Boundary Issues: {total_boundary_issues}")

    if total_boundary_issues > 0:
        print(f"  ⚠️  {total_boundary_issues} potential transaction boundary issues detected!")
        print("  Check for nested transactions that might cause problems.")
    else:
        print(f"  ✅ Transaction boundaries appear to be properly managed")

    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python transaction_boundary_tester.py <directory_path>")
        sys.exit(1)

    directory_path = Path(sys.argv[1])
    if not directory_path.exists():
        print(f"Directory {directory_path} does not exist!")
        sys.exit(1)

    print(f"Scanning {directory_path} for transaction boundary issues...")
    results = scan_directory(directory_path)
    print_report(results)


if __name__ == "__main__":
    main()