# Python Coding Standards for NFC Reader/Writer System

## Fundamental Rules
1. All code must adhere to these standards
2. Code will not be merged without passing linting and style checks
3. All code must include appropriate documentation

## Style Guide
We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following specifics:

### Formatting
- 4 spaces for indentation (no tabs)
- Maximum line length of 100 characters
- Use blank lines to separate logical sections
- Use spaces after commas and around operators
- No trailing whitespace

### Naming Conventions
- `snake_case` for variables, functions, methods, and modules
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Prefix private methods and variables with underscore (_)

### Imports
- Imports should be grouped in the following order:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Each group should be separated by a blank line
- Import specific functions/classes, not modules where practical
- Avoid wildcard imports (`from module import *`)

## Documentation
- All modules, classes, methods, and functions must include docstrings
- Use Google style docstrings
- Include type hints for function parameters and return values
- Document exceptions that may be raised

Example:
```python
def process_nfc_data(data: bytes, validate: bool = True) -> Dict[str, Any]:
    """
    Process raw NFC data and return structured format.
    
    Args:
        data: Raw binary data from NFC tag
        validate: Whether to validate the data structure
        
    Returns:
        Dictionary containing parsed NFC data
        
    Raises:
        InvalidNFCDataError: If data format is invalid and validate=True
    """
    # Implementation
```

## Testing
- All code must be unit tested using pytest
- Minimum test coverage of 90%
- Tests must be in a separate test directory mirroring the module structure
- Tests should be independent and not rely on external resources
- Use mocks for external dependencies

## Error Handling
- Use specific exception types instead of generic ones
- Handle exceptions at the appropriate level
- Log exceptions with appropriate context
- Don't use exceptions for flow control

## Project-Specific Guidelines
- All NFC data processing functions must validate input data
- API endpoints must include proper error handling and responses
- USB and WiFi communication code must include connection status monitoring
- Configuration should be loaded from environment variables or config files
- Use dataclasses for data models when appropriate

## Linting and Enforcement
- Use flake8 for linting
- Use black for code formatting
- Use mypy for static type checking
- Configure pre-commit hooks to enforce standards

## Version Control
- Commit messages should follow conventional commits format
- Each commit should address a single logical change
- Branch naming: `feature/description`, `bugfix/description`, `refactor/description`
- Pull requests require code review before merging

## Security Guidelines
- Never store sensitive information in code
- Use environment variables for configuration secrets
- Validate all user inputs
- Sanitize data before logging
- Use secure connections for all network communication
