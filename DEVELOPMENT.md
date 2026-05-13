# Smart Wish Tracker - Development Guide

This document describes the development environment setup and linting configuration for the Smart Wish Tracker project.

## 📋 Overview

The Smart Wish Tracker uses a comprehensive linting and code quality setup with pre-commit hooks to ensure consistent code quality across all contributions.

## 🛠️ Development Environment Setup

### Quick Setup (Recommended)

Run the automated setup script:

```bash
./setup-dev.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Configure pre-commit hooks
- Run initial code quality checks

### Manual Setup

If you prefer manual setup or need to troubleshoot:

```bash
# 1. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg

# 4. Run initial checks
pre-commit run --all-files
```

### Using Make Commands

We provide convenient Make targets for common development tasks:

```bash
# Show all available commands
make help

# Complete development setup
make setup

# Run linting
make lint

# Format code
make format

# Run tests
make test

# Start the application
make run
```

## 🔍 Code Quality Tools

### Linters and Formatters

| Tool | Purpose | Configuration File |
|------|---------|-------------------|
| **Black** | Code formatting | `pyproject.toml` |
| **isort** | Import sorting | `pyproject.toml` |
| **flake8** | Style and error checking | `pyproject.toml` |
| **mypy** | Type checking | `pyproject.toml` |
| **bandit** | Security linting | `pyproject.toml` |
| **pydocstyle** | Docstring style | `pyproject.toml` |
| **autoflake** | Remove unused imports | `pyproject.toml` |

### Pre-commit Hooks

Pre-commit hooks run automatically on every commit and include:

- **Code Formatting**: Black, isort, autoflake
- **Linting**: flake8, mypy, bandit, pydocstyle
- **File Checks**: trailing whitespace, file endings, YAML/JSON validation
- **Security**: bandit security scanning
- **Python Upgrades**: pyupgrade for modern Python syntax

## 📁 Project Structure

```
smart_wish_tracker/
├── .pre-commit-config.yaml    # Pre-commit configuration
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
├── Makefile                   # Development commands
├── setup-dev.sh               # Automated setup script
├── DEVELOPMENT.md             # This file
│
├── app.py                     # Flask application entry point
├── database.py                # Database layer
├── problem.py                 # Level 1: Problem entities
├── project.py                 # Level 2: Project entities  
├── task.py                    # Level 3: Task entities
├── event.py                   # Event management
├── grid_manager.py            # Grid contribution tracking
│
├── tests/                     # Test files
│   └── test-client.py
├── templates/                 # HTML templates
│   └── index.html
├── static/                    # Static assets
│   ├── styles.css
│   └── script.js
└── data/                      # Database files
    └── projects.db
```

## 🚀 Development Workflow

### Day-to-day Development

1. **Activate environment**:
   ```bash
   source .venv/bin/activate
   ```

2. **Make your changes** to the code

3. **Format and lint** (optional, pre-commit will do this):
   ```bash
   make format
   make lint
   ```

4. **Test your changes**:
   ```bash
   make test
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```
   
   Pre-commit hooks will run automatically and may modify files. If they do:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

### Pre-commit Hook Details

#### Automatic Fixes
These hooks will automatically fix issues:
- Remove trailing whitespace
- Fix file endings
- Format code with Black
- Sort imports with isort
- Remove unused imports with autoflake
- Upgrade Python syntax with pyupgrade

#### Manual Fixes Required
These hooks will fail if issues are found (you need to fix manually):
- flake8 style violations
- mypy type errors
- bandit security issues
- pydocstyle docstring problems

## ⚙️ Configuration Details

### Black (Code Formatting)
- Line length: 88 characters
- Target: Python 3.8+
- Profile: Compatible with isort

### flake8 (Linting)
- Line length: 88 characters
- Ignores: E203, W503 (Black compatibility)
- Additional plugins: docstrings, bugbear, comprehensions

### mypy (Type Checking)
- Target: Python 3.8+
- Strict mode: Partially enabled
- Ignores missing imports for external libraries

### bandit (Security)
- Recursive scanning
- Excludes test files
- Generates JSON reports

## 🐛 Troubleshooting

### Common Issues

**Pre-commit hook failures:**
```bash
# Update hooks to latest versions
pre-commit autoupdate

# Run hooks manually
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```

**Virtual environment issues:**
```bash
# Remove and recreate
rm -rf .venv
make setup
```

**Permission errors:**
```bash
# Make scripts executable
chmod +x setup-dev.sh
```

### Getting Help

1. Check this documentation
2. Run `make help` for available commands
3. Check individual tool documentation:
   - [Black](https://black.readthedocs.io/)
   - [isort](https://pycqa.github.io/isort/)
   - [flake8](https://flake8.pycqa.org/)
   - [mypy](https://mypy.readthedocs.io/)
   - [pre-commit](https://pre-commit.com/)

## 📝 Contributing

When contributing to this project:

1. Follow the development workflow above
2. Ensure all pre-commit hooks pass
3. Add tests for new functionality
4. Update documentation as needed
5. Use descriptive commit messages

## 🎯 Code Quality Standards

- **Line Length**: 88 characters (Black standard)
- **Imports**: Sorted with isort, grouped by type
- **Type Hints**: Encouraged for new code
- **Docstrings**: Google style for public functions/classes
- **Security**: No hardcoded secrets, secure coding practices
- **Testing**: Test coverage for critical functionality

---

*This development environment is designed to catch issues early and maintain consistent code quality across the project.*