#!/usr/bin/env python3
"""
Cache Key Validator Script

This script analyzes code to verify that cache keys properly include user identifiers
to prevent cross-user data leakage.
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class CacheKeyVisitor(ast.NodeVisitor):
    """AST visitor to detect cache operations and check for proper user isolation."""

    def __init__(self):
        self.cache_operations = []
        self.missing_user_identifiers = []
        self.potential_cache_leaks = []

    def visit_Call(self, node):
        # Look for cache operation patterns
        if self._is_cache_operation(node):
            cache_info = {
                'line': node.lineno,
                'function': self._get_function_name(node),
                'arguments': self._get_arguments(node),
                'has_user_identifier': self._has_user_identifier(node),
                'context': self._get_context(node)
            }

            self.cache_operations.append(cache_info)

            if not cache_info['has_user_identifier']:
                self.missing_user_identifiers.append(cache_info)

        self.generic_visit(node)

    def _is_cache_operation(self, node) -> bool:
        """Check if this is a cache operation call."""
        func_name = self._get_function_name(node)

        # Common cache operation patterns
        cache_methods = [
            'cache.set', 'cache.get', 'cache.delete', 'cache.put', 'cache.update',
            'redis.set', 'redis.get', 'redis.delete', 'memcached.set', 'memcached.get',
            'get_cache', 'set_cache', 'delete_cache', 'cache_key', 'build_cache_key'
        ]

        # Check if function name contains cache-related terms
        func_full_name = func_name.lower()
        return any(method in func_full_name for method in cache_methods)

    def _get_function_name(self, node) -> str:
        """Extract the function/method name from a call."""
        if isinstance(node.func, ast.Attribute):
            # Handle obj.method() calls
            if isinstance(node.func.value, ast.Name):
                return f"{node.func.value.id}.{node.func.attr}"
            elif isinstance(node.func.value, ast.Attribute):
                # Handle nested attribute access like obj.subobj.method()
                return f"{ast.unparse(node.func.value)}.{node.func.attr}"
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

    def _has_user_identifier(self, node) -> bool:
        """Check if cache key includes user identifier."""
        # Convert the entire call to string for pattern matching
        call_str = ast.unparse(node).lower()

        # Look for user identifier patterns in cache key construction
        user_id_patterns = [
            r'cache.*\[.*user_id',  # cache[key + user_id]
            r'cache.*\{.*user_id',  # cache[f"{key}_{user_id}"]
            r'user_id.*cache',      # cache[user_id + key]
            r'conversation.*user',   # conversation cache with user reference
            r'session.*user',       # session cache with user reference
            r'key.*user_id',        # key contains user_id
            r'user.*key'            # user comes before key
        ]

        for pattern in user_id_patterns:
            if re.search(pattern, call_str):
                return True

        # Check if arguments contain user_id related terms
        args_str = ' '.join(self._get_arguments(node)).lower()
        if any(term in args_str for term in ['user_id', 'user', 'userid', 'session']):
            return True

        return False

    def _get_context(self, node) -> str:
        """Extract context around the node for reporting."""
        return f"Line {node.lineno}"


def scan_file_for_cache_keys(file_path: Path) -> Dict:
    """Scan a single file for cache key issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)

        visitor = CacheKeyVisitor()
        visitor.visit(tree)

        return {
            'file': str(file_path),
            'cache_operations': visitor.cache_operations,
            'missing_user_identifiers': visitor.missing_user_identifiers,
            'potential_cache_leaks': visitor.potential_cache_leaks
        }
    except Exception as e:
        print(f"Error scanning {file_path}: {str(e)}")
        return {'file': str(file_path), 'error': str(e)}


def scan_directory(directory: Path, extensions: List[str] = ['.py']) -> List[Dict]:
    """Scan a directory for cache key issues."""
    results = []

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if 'node_modules' in str(file_path) or '.git' in str(file_path):
                continue
            result = scan_file_for_cache_keys(file_path)
            if result.get('cache_operations'):
                results.append(result)

    return results


def print_report(results: List[Dict]):
    """Print a formatted report of cache key issues."""
    print("=" * 80)
    print("CACHE KEY VALIDATION REPORT")
    print("=" * 80)

    total_operations = 0
    total_missing_identifiers = 0

    for result in results:
        if 'error' in result:
            print(f"\n❌ Error scanning {result['file']}: {result['error']}")
            continue

        print(f"\n📁 File: {result['file']}")

        if result['cache_operations']:
            print(f"  📊 Total Cache Operations Found: {len(result['cache_operations'])}")

            for op in result['cache_operations']:
                status = "✅ Secure" if op['has_user_identifier'] else "🚨 Missing User ID"
                print(f"    • {status} - Line {op['line']}: {op['function']}")

                if not op['has_user_identifier']:
                    total_missing_identifiers += 1

                total_operations += 1

        if not result['cache_operations']:
            print("  ℹ️  No cache operations detected")

    print(f"\n📊 Summary:")
    print(f"  Total Cache Operations: {total_operations}")
    print(f"  Operations Missing User Identifiers: {total_missing_identifiers}")

    if total_missing_identifiers > 0:
        print(f"  ⚠️  {total_missing_identifiers} cache operations may have security issues!")
        print("  These could allow cross-user data leakage if user_id is not in cache keys.")
    else:
        print(f"  ✅ All cache operations appear to include proper user identification")

    print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python cache_key_validator.py <directory_path>")
        sys.exit(1)

    directory_path = Path(sys.argv[1])
    if not directory_path.exists():
        print(f"Directory {directory_path} does not exist!")
        sys.exit(1)

    print(f"Scanning {directory_path} for cache key issues...")
    results = scan_directory(directory_path)
    print_report(results)


if __name__ == "__main__":
    main()