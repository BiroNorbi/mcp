"""
Dev Workspace Assistant - A comprehensive MCP server for developers
Provides tools for code generation, project scaffolding, git operations, and more.
"""
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastmcp import FastMCP, Context

mcp = FastMCP("Dev Workspace Assistant")

# ============================================================================
# TOOLS - Interactive actions the AI can perform
# ============================================================================

@mcp.tool()
def create_project_structure(
    project_name: str,
    project_type: str = "python",
    include_tests: bool = True,
    include_docs: bool = True,
    base_path: str = "."
) -> Dict[str, Any]:
    """
    Scaffold a complete project structure with best practices.
    
    Args:
        project_name: Name of the project
        project_type: Type of project (python, node, go, rust, web)
        include_tests: Whether to create test directory structure
        include_docs: Whether to create documentation directory
        base_path: Base path where project should be created
    
    Returns:
        Dictionary with created directories and files
    """
    templates = {
        "python": {
            "dirs": ["src", "tests", "docs", ".github/workflows"],
            "files": {
                "README.md": f"# {project_name}\n\nA Python project.\n",
                "pyproject.toml": f'[project]\nname = "{project_name}"\nversion = "0.1.0"\n',
                ".gitignore": "__pycache__/\n*.pyc\n.env\n.venv/\n",
                "src/__init__.py": "",
                "tests/__init__.py": "",
            }
        },
        "node": {
            "dirs": ["src", "tests", "dist", "docs"],
            "files": {
                "README.md": f"# {project_name}\n\nA Node.js project.\n",
                "package.json": json.dumps({"name": project_name, "version": "0.1.0"}, indent=2),
                ".gitignore": "node_modules/\ndist/\n.env\n",
                "src/index.js": "// Main entry point\n",
            }
        },
        "web": {
            "dirs": ["css", "js", "assets", "pages"],
            "files": {
                "README.md": f"# {project_name}\n\nA web project.\n",
                "index.html": "<!DOCTYPE html>\n<html>\n<head>\n  <title>{}</title>\n</head>\n<body>\n</body>\n</html>\n".format(project_name),
                "css/style.css": "/* Main styles */\n",
                "js/main.js": "// Main JavaScript\n",
            }
        }
    }
    
    template = templates.get(project_type, templates["python"])
    project_path = Path(base_path) / project_name
    created = {"directories": [], "files": []}
    
    try:
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create directories
        for dir_name in template["dirs"]:
            dir_path = project_path / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            created["directories"].append(str(dir_path))
        
        # Create files
        for file_name, content in template["files"].items():
            file_path = project_path / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            created["files"].append(str(file_path))
        
        return {
            "success": True,
            "project_path": str(project_path),
            "created": created,
            "message": f"Successfully created {project_type} project: {project_name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create project: {str(e)}"
        }


@mcp.tool()
def analyze_code_metrics(file_path: str) -> Dict[str, Any]:
    """
    Analyze code metrics for a given file (lines, functions, complexity estimates).
    
    Args:
        file_path: Path to the code file to analyze
    
    Returns:
        Dictionary with code metrics and analysis
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}
        
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        metrics = {
            "file": file_path,
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(1 for line in lines if line.strip().startswith('#')),
            "code_lines": 0,
            "functions": [],
            "classes": [],
            "imports": [],
        }
        
        # Count code lines
        metrics["code_lines"] = metrics["total_lines"] - metrics["blank_lines"] - metrics["comment_lines"]
        
        # Detect functions and classes (basic parsing)
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('def '):
                func_name = stripped.split('(')[0].replace('def ', '').strip()
                metrics["functions"].append({"name": func_name, "line": i})
            elif stripped.startswith('class '):
                class_name = stripped.split('(')[0].split(':')[0].replace('class ', '').strip()
                metrics["classes"].append({"name": class_name, "line": i})
            elif stripped.startswith('import ') or stripped.startswith('from '):
                metrics["imports"].append(stripped)
        
        metrics["complexity_score"] = min(10, metrics["code_lines"] / 50 + len(metrics["functions"]) * 0.5)
        
        return metrics
        
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def git_status_summary(repo_path: str = ".") -> Dict[str, Any]:
    """
    Get a comprehensive git status summary for a repository.
    
    Args:
        repo_path: Path to the git repository (defaults to current directory)
    
    Returns:
        Dictionary with git status information
    """
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return {"error": "Not a git repository or git not available"}
        
        lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        status = {
            "modified": [],
            "added": [],
            "deleted": [],
            "untracked": [],
            "renamed": []
        }
        
        for line in lines:
            if not line:
                continue
            state, file = line[:2], line[3:]
            
            if 'M' in state:
                status["modified"].append(file)
            elif 'A' in state:
                status["added"].append(file)
            elif 'D' in state:
                status["deleted"].append(file)
            elif '??' in state:
                status["untracked"].append(file)
            elif 'R' in state:
                status["renamed"].append(file)
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            "branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown",
            "status": status,
            "total_changes": sum(len(v) for v in status.values()),
            "clean": all(len(v) == 0 for v in status.values())
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Git command timed out"}
    except FileNotFoundError:
        return {"error": "Git not installed or not in PATH"}
    except Exception as e:
        return {"error": str(e)}


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
        language: Programming language (python, javascript, go, rust)
        snippet_type: Type of snippet (function, class, test, api_endpoint, cli)
        name: Name of the code element
        description: Optional description for documentation
    
    Returns:
        Dictionary with generated code and metadata
    """
    snippets = {
        "python": {
            "function": '''def {name}():
    """
    {description}
    """
    pass
''',
            "class": '''class {name}:
    """
    {description}
    """
    
    def __init__(self):
        pass
''',
            "test": '''def test_{name}():
    """
    Test for {description}
    """
    # Arrange
    
    # Act
    
    # Assert
    assert True
''',
            "api_endpoint": '''@app.route("/{name}", methods=["GET", "POST"])
def {name}():
    """
    {description}
    """
    return {{"message": "Success"}}, 200
''',
        },
        "javascript": {
            "function": '''function {name}() {{
  // {description}
  
}}
''',
            "class": '''class {name} {{
  constructor() {{
    // {description}
  }}
}}
''',
            "test": '''describe('{name}', () => {{
  it('should {description}', () => {{
    // Arrange
    
    // Act
    
    // Assert
    expect(true).toBe(true);
  }});
}});
''',
        }
    }
    
    desc = description or f"TODO: Add description for {name}"
    
    if language not in snippets:
        return {"error": f"Language '{language}' not supported"}
    
    if snippet_type not in snippets[language]:
        return {
            "error": f"Snippet type '{snippet_type}' not available for {language}",
            "available_types": list(snippets[language].keys())
        }
    
    code = snippets[language][snippet_type].format(name=name, description=desc)
    
    return {
        "language": language,
        "type": snippet_type,
        "name": name,
        "code": code,
        "lines": len(code.split('\n'))
    }


@mcp.tool()
def search_workspace(
    query: str,
    file_pattern: str = "*",
    base_path: str = ".",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for files and content in the workspace.
    
    Args:
        query: Search query (filename or content to search for)
        file_pattern: Glob pattern for file filtering (e.g., "*.py", "*.js")
        base_path: Base directory to search from
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary with search results
    """
    try:
        base = Path(base_path)
        results = {"files": [], "matches": []}
        
        # Search by filename
        for path in base.rglob(file_pattern):
            if path.is_file() and query.lower() in path.name.lower():
                results["files"].append({
                    "path": str(path),
                    "size": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                })
                
                if len(results["files"]) >= max_results:
                    break
        
        # Search content in text files
        if len(results["files"]) < max_results:
            for path in base.rglob(file_pattern):
                if not path.is_file() or path.suffix in ['.pyc', '.exe', '.dll', '.so']:
                    continue
                    
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    if query.lower() in content.lower():
                        # Find line numbers
                        lines = content.split('\n')
                        matching_lines = [
                            {"line": i+1, "content": line.strip()}
                            for i, line in enumerate(lines)
                            if query.lower() in line.lower()
                        ][:3]  # First 3 matches per file
                        
                        results["matches"].append({
                            "path": str(path),
                            "occurrences": len(matching_lines),
                            "preview": matching_lines
                        })
                        
                        if len(results["matches"]) >= max_results:
                            break
                except:
                    continue
        
        return {
            "query": query,
            "total_files": len(results["files"]),
            "total_content_matches": len(results["matches"]),
            "results": results
        }
        
    except Exception as e:
        return {"error": str(e)}


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
