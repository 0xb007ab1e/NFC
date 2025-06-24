#!/bin/bash

# Script to install Git hooks for the NFC project
# This ensures all developers have the same safety checks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing Git hooks for NFC project...${NC}"

# Get the root directory of the project
PROJECT_ROOT=$(git rev-parse --show-toplevel)
if [ -z "$PROJECT_ROOT" ]; then
  echo -e "${RED}Error: Not in a Git repository.${NC}"
  exit 1
fi

# Create hooks directory if it doesn't exist
HOOKS_DIR="$PROJECT_ROOT/.git/hooks"
mkdir -p "$HOOKS_DIR"

# Create pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOL'
#!/bin/bash

# Pre-commit hook to prevent sensitive files from being committed

# Define patterns to check for
SENSITIVE_PATTERNS=(
  "\.p1d$"
  "password"
  "secret"
  "token"
  "credential"
  "api[_-]key"
)

# Check if any sensitive files are being committed
check_sensitive_files() {
  local files_to_commit=$(git diff --cached --name-only)
  
  # Exit if there are no files to commit
  if [ -z "$files_to_commit" ]; then
    return 0
  fi
  
  local sensitive_files=()
  
  for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    matching_files=$(echo "$files_to_commit" | grep -E "$pattern" || true)
    if [ -n "$matching_files" ]; then
      while IFS= read -r file; do
        if [ -n "$file" ]; then
          sensitive_files+=("$file")
        fi
      done <<< "$matching_files"
    fi
  done
  
  # If sensitive files found, block the commit
  if [ ${#sensitive_files[@]} -gt 0 ]; then
    echo "ERROR: Attempting to commit sensitive files:"
    for file in "${sensitive_files[@]}"; do
      echo "  - $file"
    done
    echo ""
    echo "These files may contain sensitive information and should not be committed."
    echo "If you're certain this is safe, you can bypass this check with git commit --no-verify"
    echo "But PLEASE ENSURE these files don't contain authentication credentials, private keys, or sensitive data."
    echo ""
    echo "Commit aborted."
    return 1
  fi
  
  return 0
}

# Main execution
check_sensitive_files
exit $?
EOL

# Make the hook executable
chmod +x "$HOOKS_DIR/pre-commit"

echo -e "${GREEN}✓ Pre-commit hook installed successfully!${NC}"
echo -e "${YELLOW}This hook will prevent committing sensitive files like:${NC}"
echo -e "  - ${RED}*.p1d${NC} files (proprietary authentication files)"
echo -e "  - Files with names containing: password, secret, token, credential, api_key"
echo ""
echo -e "${YELLOW}New contributors should run:${NC}"
echo -e "  ${GREEN}bash tools/install_git_hooks.sh${NC}"
echo -e "after cloning the repository to install these safety checks."
