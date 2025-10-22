---
name: python-code-review
description: Performs code reviews for Python files, checking for code quality, best practices, security issues, and maintainability. Use when reviewing Python code or when asked to check, audit, or improve Python code quality.
---

# Python Code Review

Perform systematic code reviews of Python files to identify issues and suggest improvements.

## Review Process

When reviewing Python code:

1. **Read the entire file** to understand its purpose and structure

2. **Check these areas** and report findings:

   - **Code Quality**: Readability, naming conventions (PEP 8), Python idioms
   - **Best Practices**: Type hints, docstrings, error handling, resource management
   - **Security**: Input validation, SQL injection risks, hardcoded secrets, unsafe functions
   - **Performance**: Inefficient loops, unnecessary computations, memory issues
   - **Maintainability**: Function complexity, code duplication, clear dependencies

3. **Structure output as**:

   **Summary**
   - Overall assessment (Good/Fair/Needs Improvement)
   - 2-3 key strengths
   - Critical issues requiring immediate attention

   **Detailed Findings** (for each issue):
   - **Severity**: Critical/High/Medium/Low
   - **Line(s)**: Specific line numbers
   - **Issue**: Clear description
   - **Recommendation**: Specific fix with code example

   **Positive Highlights**
   - Well-implemented patterns worth noting

## Common Issues to Check

- Naming: Use `snake_case` for functions/variables, `PascalCase` for classes
- Error handling: Avoid bare `except:` clauses
- Security: Never use f-strings in SQL queries, check for hardcoded credentials
- Performance: Use list comprehensions, avoid string concatenation in loops
- Resources: Use context managers (`with` statements) for files/connections

## Notes

Focus on actionable feedback with specific recommendations and acknowledge good practices.