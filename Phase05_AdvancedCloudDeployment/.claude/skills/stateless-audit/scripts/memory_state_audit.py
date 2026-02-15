#!/usr/bin/env python3
"""
Memory State Audit Script

This script automatically detects potential state leaks in memory by scanning
code for global variables, class attributes, and other patterns that could
persist across requests in a stateless system.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class MemoryStateVisitor(ast.NodeVisitor):
    """AST visitor to detect potential memory state patterns."""

    def __init__(self):
        self.global_assignments = []
        self.class_attributes = []
        self.singleton_patterns = []
        self.module_level_state = []

    def visit_Assign(self, node):
        # Check for module-level assignments that could be global state
        if isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            if self._is_potential_global_state(target_name, node.value):
                self.global_assignments.append({
                    'line': node.lineno,
                    'variable': target_name,
                    'context': self._get_context(node),
                    'type': self._get_assignment_type(node.value)
                })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Look for class attributes that might maintain state
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        self.class_attributes.append({
                            'class': node.name,
                            'line': item.lineno,
                            'attribute': target.id,
                            'context': self._get_context(item)
                        })
            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                self.class_attributes.append({
                    'class': node.name,
                    'line': item.lineno,
                    'attribute': item.target.id,
                    'context': self._get_context(item)
                })
        self.generic_visit(node)

    def _is_potential_global_state(self, name: str, value_node) -> bool:
        """Check if assignment looks like potential global state."""
        # Check for common global state patterns
        suspicious_names = [
            'cache', 'session', 'state', 'storage', 'data', 'conversations',
            'users', 'messages', 'history', 'db_connection', 'pool'
        ]

        # Check if name suggests state storage
        if any(suspicious in name.lower() for suspicious in suspicious_names):
            return True

        # Check if it's a dictionary or list being assigned at module level
        if isinstance(value_node, (ast.Dict, ast.List, ast.Call)):
            if hasattr(value_node, 'func') and hasattr(value_node.func, 'id'):
                # Common collection types that might store state
                if value_node.func.id in ['dict', 'list', 'set', 'OrderedDict']:
                    return True

        return False

    def _get_context(self, node) -> str:
        """Extract context around the node for reporting."""
        # This is simplified - in practice, you'd extract more context
        return f"Line {node.lineno}"

    def _get_assignment_type(self, value_node) -> str:
        """Determine the type of assignment."""
        if isinstance(value_node, ast.Dict):
            return "dictionary"
        elif isinstance(value_node, ast.List):
            return "list"
        elif isinstance(value_node, ast.Call):
            if hasattr(value_node.func, 'id'):
                return f"function_call({value_node.func.id})"
        return "unknown"


def scan_file_for_memory_state(file_path: Path) -> Dict:
    """Scan a single file for potential memory state issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)

        visitor = MemoryStateVisitor()
        visitor.visit(tree)

        return {
            'file': str(file_path),
            'global_assignments': visitor.global_assignments,
            'class_attributes': visitor.class_attributes,
            'singleton_patterns': visitor.singleton_patterns,
            'module_level_state': visitor.module_level_state
        }
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
        return {'file': str(file_path), 'error': str(e)}


def scan_directory(directory: Path, extensions: List[str] = ['.py']) -> List[Dict]:
    """Scan a directory for memory state issues."""
    results = []

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            result = scan_file_for_memory_state(file_path)
            if result.get('global_assignments') or result.get('class_attributes'):
                results.append(result)

    return results


def print_report(results: List[Dict]):
    """Print a formatted report of memory state issues."""
    print("=" * 80)
    print("MEMORY STATE AUDIT REPORT")
    print("=" * 80)

    total_issues = 0

    for result in results:
        if 'error' in result:
            print(f"\n❌ Error scanning {result['file']}: {result['error']}")
            continue

        file_has_issues = False
        print(f"\n📁 File: {result['file']}")

        if result['global_assignments']:
            print("  🚨 Global Assignments (Potential State Leaks):")
            for assignment in result['global_assignments']:
                print(f"    • Line {assignment['line']}: {assignment['variable']} ({assignment['type']}) - {assignment['context']}")
                total_issues += 1
                file_has_issues = True

        if result['class_attributes']:
            print("  ⚠️  Class Attributes (Potential State Storage):")
            for attr in result['class_attributes']:
                print(f"    • Line {attr['line']}: {attr['class']}.{attr['attribute']} - {attr['context']}")
                total_issues += 1
                file_has_issues = True

        if not file_has_issues:
            print("  ✅ No obvious memory state issues detected")

    print(f"\n📊 Total Potential Issues Found: {total_issues}")
    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python memory_state_audit.py <directory_path>")
        sys.exit(1)

    directory_path = Path(sys.argv[1])
    if not directory_path.exists():
        print(f"Directory {directory_path} does not exist!")
        sys.exit(1)

    print(f"Scanning {directory_path} for memory state issues...")
    results = scan_directory(directory_path)
    print_report(results)


if __name__ == "__main__":
    main()