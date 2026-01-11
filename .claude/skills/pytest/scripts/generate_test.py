#!/usr/bin/env python3
"""
Generate pytest test files from Python source code.

Usage:
    python generate_test.py <source_file.py> [--output <test_file.py>]
    python generate_test.py <source_file.py> --fastapi

Examples:
    # Generate test for a regular module
    python generate_test.py app/models.py

    # Generate test for FastAPI endpoints
    python generate_test.py app/main.py --fastapi

    # Specify custom output location
    python generate_test.py app/utils.py --output tests/test_utils.py
"""

import ast
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any


class FunctionAnalyzer(ast.NodeVisitor):
    """Analyze Python source code to extract function signatures."""

    def __init__(self):
        self.functions = []
        self.classes = []
        self.fastapi_routes = []

    def visit_FunctionDef(self, node):
        """Extract function information."""
        func_info = {
            'name': node.name,
            'args': [arg.arg for arg in node.args.args],
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node)),
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list]
        }

        # Check if it's a FastAPI route
        if any(d in ['app.get', 'app.post', 'app.put', 'app.delete', 'app.patch']
               for d in func_info['decorators']):
            self.fastapi_routes.append(func_info)
        else:
            self.functions.append(func_info)

        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Handle async functions."""
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        """Extract class information."""
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append({
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args if arg.arg != 'self'],
                    'is_async': isinstance(item, ast.AsyncFunctionDef)
                })

        self.classes.append({
            'name': node.name,
            'methods': methods
        })

        self.generic_visit(node)

    def _get_decorator_name(self, decorator):
        """Extract decorator name as string."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Attribute):
                return f"{decorator.func.value.id}.{decorator.func.attr}"
            elif isinstance(decorator.func, ast.Name):
                return decorator.func.id
        elif isinstance(decorator, ast.Attribute):
            return f"{decorator.value.id}.{decorator.attr}"
        return ""


def generate_function_test(func: Dict[str, Any], module_name: str) -> str:
    """Generate test code for a function."""
    test_name = f"test_{func['name']}"
    args_str = ", ".join(func['args'])

    # Generate parametrize decorator if function has arguments
    parametrize = ""
    if func['args']:
        param_names = ", ".join(func['args'])
        param_values = ", ".join(["None"] * len(func['args']))
        parametrize = f'@pytest.mark.parametrize("{param_names}", [({param_values})])\n'

    async_prefix = "async " if func['is_async'] else ""
    await_prefix = "await " if func['is_async'] else ""

    return f'''{parametrize}{"@pytest.mark.asyncio" if func['is_async'] else ""}
{async_prefix}def {test_name}({args_str}):
    """Test {func['name']} function."""
    # Arrange
    # TODO: Set up test data and mocks

    # Act
    result = {await_prefix}{module_name}.{func['name']}({args_str})

    # Assert
    assert result is not None  # TODO: Add specific assertions
'''


def generate_class_test(cls: Dict[str, Any], module_name: str) -> str:
    """Generate test code for a class."""
    tests = [f"class Test{cls['name']}:"]
    tests.append('    """Test suite for {} class."""\n'.format(cls['name']))

    # Add fixture for class instance
    tests.append("    @pytest.fixture")
    tests.append(f"    def instance(self):")
    tests.append(f"        \"\"\"Create {cls['name']} instance for testing.\"\"\"")
    tests.append(f"        return {module_name}.{cls['name']}()")
    tests.append("")

    # Generate tests for each method
    for method in cls['methods']:
        if method['name'].startswith('_') and method['name'] != '__init__':
            continue  # Skip private methods

        test_name = f"test_{method['name']}"
        args_str = ", ".join(method['args']) if method['args'] else ""

        async_prefix = "async " if method['is_async'] else ""
        await_prefix = "await " if method['is_async'] else ""
        pytest_mark = "    @pytest.mark.asyncio\n" if method['is_async'] else ""

        tests.append(f"{pytest_mark}    {async_prefix}def {test_name}(self, instance{', ' + args_str if args_str else ''}):")
        tests.append(f'        """Test {method["name"]} method."""')
        tests.append("        # Arrange")
        tests.append("        # TODO: Set up test data")
        tests.append("")
        tests.append("        # Act")
        tests.append(f"        result = {await_prefix}instance.{method['name']}({args_str})")
        tests.append("")
        tests.append("        # Assert")
        tests.append("        assert result is not None  # TODO: Add specific assertions")
        tests.append("")

    return "\n".join(tests)


def generate_fastapi_test(route: Dict[str, Any], module_name: str) -> str:
    """Generate test code for FastAPI route."""
    test_name = f"test_{route['name']}"

    # Determine HTTP method from decorator
    method = "get"
    for dec in route['decorators']:
        if 'post' in dec.lower():
            method = "post"
        elif 'put' in dec.lower():
            method = "put"
        elif 'delete' in dec.lower():
            method = "delete"
        elif 'patch' in dec.lower():
            method = "patch"

    async_prefix = "async " if route['is_async'] else ""
    await_prefix = "await " if route['is_async'] else ""
    pytest_mark = "@pytest.mark.asyncio\n" if route['is_async'] else ""

    if route['is_async']:
        client_code = f'''    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.{method}("/endpoint")  # TODO: Update endpoint path'''
    else:
        client_code = f'''    response = client.{method}("/endpoint")  # TODO: Update endpoint path'''

    return f'''{pytest_mark}{async_prefix}def {test_name}():
    """Test {route['name']} endpoint."""
    # Arrange
    # TODO: Set up test data

    # Act
{client_code}

    # Assert
    assert response.status_code == 200
    # TODO: Add response body assertions
'''


def generate_test_file(source_path: Path, is_fastapi: bool = False) -> str:
    """Generate complete test file content."""
    # Read and parse source file
    with open(source_path, 'r') as f:
        source_code = f.read()

    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        print(f"Error parsing {source_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Analyze source code
    analyzer = FunctionAnalyzer()
    analyzer.visit(tree)

    # Generate module name
    module_name = source_path.stem

    # Build test file content
    lines = [
        '"""',
        f'Tests for {source_path.name}',
        '',
        'Generated by pytest skill - customize as needed.',
        '"""',
        '',
        'import pytest',
    ]

    # Add imports based on content
    if any(f['is_async'] for f in analyzer.functions) or analyzer.fastapi_routes:
        lines.append('import pytest')

    if is_fastapi or analyzer.fastapi_routes:
        lines.extend([
            'from fastapi.testclient import TestClient',
            'from httpx import AsyncClient',
        ])

    lines.extend([
        f'from {module_name} import *  # TODO: Import specific items',
        '',
        ''
    ])

    # Add FastAPI fixtures if needed
    if is_fastapi or analyzer.fastapi_routes:
        lines.extend([
            '@pytest.fixture',
            'def client():',
            '    """FastAPI test client fixture."""',
            '    from app.main import app  # TODO: Update import path',
            '    return TestClient(app)',
            '',
            ''
        ])

    # Generate tests for functions
    for func in analyzer.functions:
        lines.append(generate_function_test(func, module_name))
        lines.append('')

    # Generate tests for FastAPI routes
    for route in analyzer.fastapi_routes:
        lines.append(generate_fastapi_test(route, module_name))
        lines.append('')

    # Generate tests for classes
    for cls in analyzer.classes:
        lines.append(generate_class_test(cls, module_name))
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Generate pytest test files from Python source code'
    )
    parser.add_argument('source_file', type=str, help='Source Python file to generate tests for')
    parser.add_argument('--output', '-o', type=str, help='Output test file path')
    parser.add_argument('--fastapi', action='store_true', help='Generate FastAPI-specific tests')

    args = parser.parse_args()

    source_path = Path(args.source_file)
    if not source_path.exists():
        print(f"Error: Source file '{source_path}' not found", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        # Default: create test_<filename>.py in tests/ directory
        output_path = Path('tests') / f'test_{source_path.name}'

    # Generate test content
    test_content = generate_test_file(source_path, args.fastapi)

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write test file
    with open(output_path, 'w') as f:
        f.write(test_content)

    print(f"✅ Generated test file: {output_path}")
    print(f"📝 Review and customize the generated tests before running")


if __name__ == '__main__':
    main()
