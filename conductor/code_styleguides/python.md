# Python Style Guide

## Formatter & Linter
- Use **Ruff** for both linting and formatting (`ruff check` + `ruff format`)
- Configure via `pyproject.toml`
- Line length: 88 characters (Ruff/Black default)

## Naming Conventions (PEP 8)
- `snake_case` for variables, functions, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- Prefix private members with `_`

## Type Hints (PEP 484)
- All function signatures must include type annotations
- Use `from __future__ import annotations` for forward references
- Use `typing` module for complex types (`Optional`, `List`, `Dict`, etc.)
- Prefer `X | None` over `Optional[X]` in Python 3.10+

## Imports
- Standard library → third-party → local (separated by blank lines)
- No wildcard imports (`from x import *`)
- Prefer absolute imports

## Functions & Classes
- Max function length: ~30 lines; extract helpers if longer
- One class per file for major components
- Docstrings for all public functions and classes (Google style)

## Error Handling
- Catch specific exceptions, not bare `except:`
- Log errors before re-raising or handling
- Use custom exception classes for domain errors

## Async
- Use `async/await` consistently with Playwright
- Do not mix sync and async code paths
