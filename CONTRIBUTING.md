# Contributing to the NFC Project

Thank you for your interest in contributing to the NFC Reader/Writer System! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

All contributors are expected to adhere to the project's code of conduct. Please be respectful and constructive in your communications and contributions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue using the bug report template. Include:

1. Clear steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Screenshots if applicable
5. Environment details (OS, device, version, etc.)

### Suggesting Enhancements

For feature requests, use the feature request template and include:

1. A clear description of the proposed feature
2. The rationale behind the feature
3. Any technical considerations
4. Implementation ideas if you have them

### Pull Requests

1. Fork the repository
2. Create a feature branch from `develop`
3. Make your changes
4. Run tests to ensure they pass
5. Submit a pull request to the `develop` branch

### Branching Strategy

We follow a modified GitFlow workflow:

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features and non-emergency fixes
- `hotfix/*`: Emergency fixes for production issues

### Commit Messages

Follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line
- Consider using the following structure:
  ```
  [Component] Brief description

  Longer description if necessary, explaining what and why.

  Ref #123
  ```

## Development Environment Setup

### Server (Python)

1. Clone the repository
2. Navigate to the server directory
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - Unix/Mac: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run tests to verify setup: `pytest`

### Android App

1. Clone the repository
2. Open the android directory in Android Studio
3. Sync Gradle dependencies
4. Build the project to verify setup

## Testing

- All new features must include appropriate tests
- All tests must pass before a pull request will be merged
- Cover both unit tests and integration tests when applicable

## Documentation

- Update documentation for any changes to APIs, features, or behaviors
- Document code with clear comments following the established style
- Update README.md if your changes require new setup steps or dependencies

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Document functions and classes with docstrings
- Run `black` and `flake8` before committing

### Kotlin/Java

- Follow the Android Kotlin style guide
- Use consistent naming conventions
- Document public APIs
- Run lint checks before committing

## Review Process

1. All pull requests require at least one review before merging
2. CI checks must pass (tests, linting, etc.)
3. Follow up on review comments promptly
4. Maintain a civil and collaborative tone in discussions

Thank you for contributing to the NFC project!
