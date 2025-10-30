"""
Dev Utility Assistant - A practical MCP server with useful development tools
Provides text processing, code generation, calculations, and data manipulation utilities.
"""
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastmcp import FastMCP

mcp = FastMCP("Dev Utility Assistant")

# ============================================================================
# TOOLS - Interactive actions the AI can perform
# ============================================================================

@mcp.tool()
def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2 * 3")
    
    Returns:
        Dictionary with result and formatted expression
    """
    try:
        # Remove any potentially dangerous characters
        safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
        
        # Evaluate safely
        result = eval(safe_expr)
        
        return {
            "expression": expression,
            "safe_expression": safe_expr,
            "result": result,
            "formatted": f"{expression} = {result}"
        }
    except Exception as e:
        return {
            "error": str(e),
            "expression": expression,
            "message": "Could not evaluate expression"
        }


@mcp.tool()
def generate_code_snippet(
    language: str,
    snippet_type: str,
    name: str,
    description: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate common code snippets and boilerplate.
    
    Args:
        language: Programming language (python, javascript, typescript, go, rust)
        snippet_type: Type of snippet (function, class, test, api_endpoint, cli)
        name: Name of the code element
        description: Optional description for documentation
    
    Returns:
        Dictionary with generated code and metadata
    """
    desc = description or f"TODO: Add description for {name}"
    
    snippets = {
        "python": {
            "function": f'''def {name}():
    """
    {desc}
    """
    pass
''',
            "class": f'''class {name}:
    """
    {desc}
    """
    
    def __init__(self):
        pass
    
    def __str__(self):
        return f"<{name}>"
''',
            "test": f'''def test_{name}():
    """
    Test for {desc}
    """
    # Arrange
    
    # Act
    
    # Assert
    assert True
''',
            "api_endpoint": f'''@app.route("/{name}", methods=["GET", "POST"])
def {name}():
    """
    {desc}
    """
    return {{"message": "Success", "data": None}}, 200
''',
        },
        "javascript": {
            "function": f'''function {name}() {{
  // {desc}
  
}}
''',
            "class": f'''class {name} {{
  constructor() {{
    // {desc}
  }}
  
  toString() {{
    return '{name}';
  }}
}}
''',
            "test": f'''describe('{name}', () => {{
  it('should {desc}', () => {{
    // Arrange
    
    // Act
    
    // Assert
    expect(true).toBe(true);
  }});
}});
''',
        },
        "typescript": {
            "function": f'''function {name}(): void {{
  // {desc}
  
}}
''',
            "class": f'''class {name} {{
  constructor() {{
    // {desc}
  }}
  
  toString(): string {{
    return '{name}';
  }}
}}
''',
        }
    }
    
    if language not in snippets:
        return {
            "error": f"Language '{language}' not supported",
            "available_languages": list(snippets.keys())
        }
    
    if snippet_type not in snippets[language]:
        return {
            "error": f"Snippet type '{snippet_type}' not available for {language}",
            "available_types": list(snippets[language].keys())
        }
    
    code = snippets[language][snippet_type]
    
    return {
        "language": language,
        "type": snippet_type,
        "name": name,
        "code": code,
        "lines": len(code.split('\n')),
        "description": desc
    }


@mcp.tool()
def text_transform(
    text: str,
    operation: str
) -> Dict[str, Any]:
    """
    Transform text in various ways.
    
    Args:
        text: Input text to transform
        operation: Type of transformation (uppercase, lowercase, titlecase, 
                   reverse, snake_case, camelCase, kebab-case, count_words,
                   count_chars, remove_whitespace)
    
    Returns:
        Dictionary with transformed text and metadata
    """
    operations = {
        "uppercase": lambda t: t.upper(),
        "lowercase": lambda t: t.lower(),
        "titlecase": lambda t: t.title(),
        "reverse": lambda t: t[::-1],
        "snake_case": lambda t: re.sub(r'[\s\-]+', '_', t.lower()),
        "camelCase": lambda t: ''.join(word.capitalize() if i > 0 else word.lower() 
                                      for i, word in enumerate(re.split(r'[\s_\-]+', t))),
        "kebab-case": lambda t: re.sub(r'[\s_]+', '-', t.lower()),
        "remove_whitespace": lambda t: ''.join(t.split()),
    }
    
    if operation not in operations:
        return {
            "error": f"Operation '{operation}' not supported",
            "available_operations": list(operations.keys())
        }
    
    result = operations[operation](text)
    
    return {
        "original": text,
        "operation": operation,
        "result": result,
        "original_length": len(text),
        "result_length": len(result),
        "word_count": len(text.split()),
        "char_count": len(text)
    }


@mcp.tool()
def json_formatter(
    json_string: str,
    indent: int = 2,
    sort_keys: bool = False
) -> Dict[str, Any]:
    """
    Format and validate JSON strings.
    
    Args:
        json_string: JSON string to format
        indent: Number of spaces for indentation
        sort_keys: Whether to sort object keys alphabetically
    
    Returns:
        Dictionary with formatted JSON and validation info
    """
    try:
        # Parse JSON
        data = json.loads(json_string)
        
        # Format with options
        formatted = json.dumps(data, indent=indent, sort_keys=sort_keys)
        
        # Get structure info
        def count_structure(obj, depth=0):
            if isinstance(obj, dict):
                return {
                    "objects": 1 + sum(count_structure(v, depth+1).get("objects", 0) for v in obj.values()),
                    "arrays": sum(count_structure(v, depth+1).get("arrays", 0) for v in obj.values()),
                    "keys": len(obj),
                    "max_depth": max([depth] + [count_structure(v, depth+1).get("max_depth", depth) for v in obj.values()])
                }
            elif isinstance(obj, list):
                return {
                    "objects": sum(count_structure(item, depth+1).get("objects", 0) for item in obj),
                    "arrays": 1 + sum(count_structure(item, depth+1).get("arrays", 0) for item in obj),
                    "keys": 0,
                    "max_depth": max([depth] + [count_structure(item, depth+1).get("max_depth", depth) for item in obj])
                }
            return {"objects": 0, "arrays": 0, "keys": 0, "max_depth": depth}
        
        structure = count_structure(data)
        
        return {
            "valid": True,
            "formatted": formatted,
            "original_length": len(json_string),
            "formatted_length": len(formatted),
            "structure": structure,
            "root_type": type(data).__name__
        }
        
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "Invalid JSON format"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }


@mcp.tool()
def regex_match(
    pattern: str,
    text: str,
    flags: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test regular expression patterns against text.
    
    Args:
        pattern: Regular expression pattern
        text: Text to match against
        flags: Optional regex flags (i=ignorecase, m=multiline, s=dotall)
    
    Returns:
        Dictionary with match results and groups
    """
    try:
        # Parse flags
        regex_flags = 0
        if flags:
            if 'i' in flags:
                regex_flags |= re.IGNORECASE
            if 'm' in flags:
                regex_flags |= re.MULTILINE
            if 's' in flags:
                regex_flags |= re.DOTALL
        
        # Compile and search
        compiled = re.compile(pattern, regex_flags)
        matches = list(compiled.finditer(text))
        
        match_details = []
        for match in matches:
            match_details.append({
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "groups": list(match.groups()),
                "groupdict": match.groupdict()
            })
        
        return {
            "pattern": pattern,
            "text_length": len(text),
            "match_count": len(matches),
            "matches": match_details[:10],  # Limit to 10 matches
            "has_matches": len(matches) > 0
        }
        
    except re.error as e:
        return {
            "error": f"Invalid regex pattern: {str(e)}",
            "pattern": pattern
        }
    except Exception as e:
        return {
            "error": str(e)
        }


@mcp.tool()
def uuid_generator(
    count: int = 1,
    format: str = "uuid4"
) -> Dict[str, Any]:
    """
    Generate UUIDs in various formats.
    
    Args:
        count: Number of UUIDs to generate (max 100)
        format: UUID format (uuid4, hex, int, short)
    
    Returns:
        Dictionary with generated UUIDs
    """
    import uuid
    
    count = min(count, 100)  # Limit to 100
    uuids = []
    
    for _ in range(count):
        new_uuid = uuid.uuid4()
        
        if format == "uuid4":
            uuids.append(str(new_uuid))
        elif format == "hex":
            uuids.append(new_uuid.hex)
        elif format == "int":
            uuids.append(new_uuid.int)
        elif format == "short":
            # Short UUID (first 8 chars)
            uuids.append(str(new_uuid)[:8])
        else:
            uuids.append(str(new_uuid))
    
    return {
        "count": len(uuids),
        "format": format,
        "uuids": uuids
    }
@mcp.tool()
def base64_encode_decode(
    text: str,
    operation: str = "encode"
) -> Dict[str, Any]:
    """
    Encode or decode base64 strings.
    
    Args:
        text: Text to encode or decode
        operation: 'encode' or 'decode'
    
    Returns:
        Dictionary with result
    """
    import base64
    
    try:
        if operation == "encode":
            encoded = base64.b64encode(text.encode()).decode()
            return {
                "operation": "encode",
                "input": text,
                "result": encoded,
                "length": len(encoded)
            }
        elif operation == "decode":
            decoded = base64.b64decode(text.encode()).decode()
            return {
                "operation": "decode",
                "input": text,
                "result": decoded,
                "length": len(decoded)
            }
        else:
            return {
                "error": "Operation must be 'encode' or 'decode'"
            }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to encode/decode"
        }


@mcp.tool()
def timestamp_converter(
    value: Optional[str] = None,
    operation: str = "to_timestamp"
) -> Dict[str, Any]:
    """
    Convert between timestamps and human-readable dates.
    
    Args:
        value: Timestamp (int/str) or date string (ISO format)
        operation: 'to_timestamp', 'to_date', or 'now'
    
    Returns:
        Dictionary with conversion results
    """
    try:
        if operation == "now":
            now = datetime.now()
            return {
                "timestamp": int(now.timestamp()),
                "iso": now.isoformat(),
                "readable": now.strftime("%Y-%m-%d %H:%M:%S"),
                "utc": datetime.utcnow().isoformat() + "Z"
            }
        elif operation == "to_date":
            if not value:
                return {"error": "Value required for conversion"}
            timestamp = int(float(value))
            dt = datetime.fromtimestamp(timestamp)
            return {
                "timestamp": timestamp,
                "iso": dt.isoformat(),
                "readable": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "day_of_week": dt.strftime("%A")
            }
        elif operation == "to_timestamp":
            if not value:
                return {"error": "Value required for conversion"}
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return {
                "date": value,
                "timestamp": int(dt.timestamp()),
                "readable": dt.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {
                "error": "Operation must be 'now', 'to_timestamp', or 'to_date'"
            }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to convert timestamp"
        }


# ============================================================================
# RESOURCES - Data the AI can retrieve
# ============================================================================

@mcp.resource("templates://project/{project_type}")
def get_project_template(project_type: str) -> str:
    """
    Get project scaffolding templates for different project types.
    """
    templates = {
        "python-cli": """# Python CLI Application Template

## Structure
```
project_name/
├── src/
│   ├── __init__.py
│   ├── cli.py
│   └── commands/
│       └── __init__.py
├── tests/
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

## Dependencies
- click or typer (CLI framework)
- pytest (testing)
- black, ruff (formatting, linting)

## Usage
```bash
python -m src.cli --help
```
""",
        "fastapi-service": """# FastAPI Service Template

## Structure
```
project_name/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   │   └── __init__.py
│   └── dependencies.py
├── tests/
│   └── test_api.py
├── pyproject.toml
└── README.md
```

## Dependencies
- fastapi
- uvicorn
- pydantic
- pytest, httpx

## Run
```bash
uvicorn app.main:app --reload
```
""",
        "react-app": """# React Application Template

## Structure
```
project_name/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── utils/
│   ├── App.jsx
│   └── index.js
├── public/
├── package.json
└── README.md
```

## Dependencies
- react, react-dom
- vite or webpack
- eslint, prettier

## Run
```bash
npm install
npm run dev
```
"""
    }
    
    return templates.get(project_type, "Template not found. Available: " + ", ".join(templates.keys()))


@mcp.resource("docs://best-practices/{topic}")
def get_best_practices(topic: str) -> str:
    """
    Retrieve best practices and guidelines for various development topics.
    """
    practices = {
        "git": """# Git Best Practices

1. **Commit Messages**
   - Use imperative mood: "Add feature" not "Added feature"
   - First line: brief summary (50 chars)
   - Body: detailed explanation (72 chars per line)

2. **Branching**
   - main/master: production-ready code
   - develop: integration branch
   - feature/xyz: new features
   - fix/xyz: bug fixes

3. **Workflow**
   - Pull before push
   - Commit often, push regularly
   - Review before merging
   - Keep commits atomic

4. **Common Commands**
   ```bash
   git commit -m "Add user authentication"
   git checkout -b feature/new-thing
   git rebase -i HEAD~3  # Interactive rebase
   git stash save "WIP: feature"
   ```
""",
        "testing": """# Testing Best Practices

1. **Test Structure (AAA Pattern)**
   - Arrange: Set up test data
   - Act: Execute the code
   - Assert: Verify results

2. **Test Coverage**
   - Aim for 80%+ coverage
   - Focus on critical paths
   - Test edge cases

3. **Test Types**
   - Unit: Individual functions/methods
   - Integration: Component interactions
   - E2E: Full user workflows

4. **Naming**
   - test_function_name_expected_behavior
   - Be descriptive and specific

5. **Best Practices**
   - Tests should be fast
   - Tests should be isolated
   - Use fixtures/mocks appropriately
   - One assertion per test (generally)
""",
        "security": """# Security Best Practices

1. **Secrets Management**
   - Never commit secrets to git
   - Use .env files (gitignored)
   - Use secret management services
   - Rotate secrets regularly

2. **Input Validation**
   - Validate all user input
   - Sanitize data before use
   - Use parameterized queries (SQL)
   - Escape output properly

3. **Authentication**
   - Use strong password policies
   - Implement MFA where possible
   - Use secure session management
   - Hash passwords (bcrypt, argon2)

4. **Dependencies**
   - Keep dependencies updated
   - Run security audits (npm audit, pip-audit)
   - Use lock files
   - Review third-party code

5. **HTTPS/TLS**
   - Always use HTTPS in production
   - Use up-to-date TLS versions
   - Validate certificates
"""
    }
    
    return practices.get(topic, "Topic not found. Available: " + ", ".join(practices.keys()))


@mcp.resource("config://github-actions/{workflow}")
def get_github_action_template(workflow: str) -> str:
    """
    Get GitHub Actions workflow templates.
    """
    workflows = {
        "python-ci": """name: Python CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov
        pip install -e .
    
    - name: Run tests
      run: |
        pytest --cov=src tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
""",
        "node-ci": """name: Node.js CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - run: npm ci
    - run: npm run build --if-present
    - run: npm test
"""
    }
    
    return workflows.get(workflow, "Workflow not found. Available: " + ", ".join(workflows.keys()))


# ============================================================================
# PROMPTS - Pre-configured prompt templates for common tasks
# ============================================================================

@mcp.prompt()
def code_review_prompt() -> str:
    """Generate a comprehensive code review prompt."""
    return """Please review the following code and provide feedback on:

1. **Code Quality**
   - Readability and maintainability
   - Naming conventions
   - Code structure and organization

2. **Best Practices**
   - Design patterns usage
   - Error handling
   - Security considerations

3. **Performance**
   - Potential bottlenecks
   - Optimization opportunities
   - Resource usage

4. **Testing**
   - Test coverage
   - Edge cases
   - Test quality

5. **Documentation**
   - Code comments
   - Docstrings/JSDoc
   - README completeness

Provide specific, actionable suggestions for improvement."""


@mcp.prompt()
def debug_assistant_prompt() -> str:
    """Generate a debugging assistance prompt."""
    return """I'm encountering an issue. Please help me debug by:

1. **Understanding the Problem**
   - What is the expected behavior?
   - What is the actual behavior?
   - When did this start happening?

2. **Gathering Information**
   - Error messages and stack traces
   - Relevant code sections
   - Environment details (OS, language version, dependencies)
   - Steps to reproduce

3. **Analysis**
   - Identify potential causes
   - Check common pitfalls
   - Review recent changes

4. **Solution**
   - Provide step-by-step fix
   - Explain why the issue occurred
   - Suggest preventive measures

5. **Testing**
   - How to verify the fix
   - What edge cases to test"""


@mcp.prompt()
def refactor_suggestion_prompt() -> str:
    """Generate a code refactoring suggestion prompt."""
    return """Analyze this code and suggest refactoring opportunities:

1. **Code Smells**
   - Long methods/functions
   - Duplicate code
   - Complex conditionals
   - Large classes

2. **Design Patterns**
   - Which patterns could improve the design?
   - How to implement them?

3. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

4. **Specific Improvements**
   - Extract methods
   - Simplify logic
   - Improve naming
   - Reduce coupling

5. **Trade-offs**
   - Benefits of each refactoring
   - Potential risks
   - Migration strategy

Provide code examples for suggested changes."""


# ============================================================================
# Run the server
# ============================================================================

if __name__ == "__main__":
    mcp.run()
