#!/bin/bash
# Smart Wish Tracker - Development Environment Setup Script

set -e

echo "🚀 Setting up Smart Wish Tracker development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python $python_version is installed, but Python $required_version or higher is required."
    exit 1
fi

print_success "Python $python_version detected"

# Check if virtual environment already exists
if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists. Removing it..."
    rm -rf .venv
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
print_status "Installing project dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Dependencies installed from requirements.txt"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    pre-commit install --hook-type commit-msg
    print_success "Pre-commit hooks installed"
else
    print_error "pre-commit not found. Installing..."
    pip install pre-commit
    pre-commit install
    pre-commit install --hook-type commit-msg
    print_success "Pre-commit installed and hooks configured"
fi

# Run initial pre-commit on all files
print_status "Running initial pre-commit checks..."
if pre-commit run --all-files; then
    print_success "All pre-commit checks passed!"
else
    print_warning "Some pre-commit checks failed. This is normal for the first run."
    print_status "Re-running pre-commit to fix auto-fixable issues..."
    pre-commit run --all-files || true
fi

# Test the setup
print_status "Testing the setup..."
if python test_hierarchy.py > /dev/null 2>&1; then
    print_success "Hierarchy test passed!"
else
    print_warning "Hierarchy test had some issues (this might be due to missing dependencies)"
fi

# Create development aliases
print_status "Creating helpful development commands..."
cat << 'EOF' > .venv/bin/dev-commands.sh
#!/bin/bash
# Development helper commands

alias lint='python -m flake8 . && python -m mypy . && python -m bandit -r .'
alias format='python -m autoflake --in-place --remove-all-unused-imports --remove-unused-variables *.py && python -m isort . && python -m black .'
alias test-hierarchy='python test_hierarchy.py'
alias run-app='python app.py'

echo "🛠️  Development commands available:"
echo "  lint        - Run all linters"
echo "  format      - Format code with black and isort"
echo "  test-hierarchy - Run hierarchy tests"
echo "  run-app     - Start the Flask application"
EOF

chmod +x .venv/bin/dev-commands.sh

print_success "Development environment setup complete! 🎉"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}📋 Next Steps:${NC}"
echo
echo "1. Activate the virtual environment:"
echo -e "   ${BLUE}source .venv/bin/activate${NC}"
echo
echo "2. Load development commands:"
echo -e "   ${BLUE}source .venv/bin/dev-commands.sh${NC}"
echo
echo "3. Alternative: Use make commands:"
echo -e "   ${BLUE}make help${NC}                 # Show available commands"
echo -e "   ${BLUE}make format${NC}               # Format code"
echo -e "   ${BLUE}make lint${NC}                 # Run linters"
echo -e "   ${BLUE}make test${NC}                 # Run tests"
echo -e "   ${BLUE}make run${NC}                  # Start application"
echo
echo "4. Pre-commit hooks are now active for all commits!"
echo
echo -e "${GREEN}🎯 Ready for development!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"