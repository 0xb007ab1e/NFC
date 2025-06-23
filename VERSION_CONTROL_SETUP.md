# NFC Reader/Writer System - Version Control Repository Setup

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Repository Organization

### GitHub Repository Setup
- Repository Name: `nfc-reader-writer-system`
- Description: Android application and PC server for NFC tag reading/writing with USB/WiFi connectivity
- Visibility: Private
- Include README: Yes
- Include .gitignore: Yes (Python and Android templates)
- License: MIT

### Branch Strategy
- **main**: Production-ready code, protected branch requiring PR approval
- **develop**: Integration branch for feature development, protected branch
- **feature/***:  Feature branches branched from develop (e.g., `feature/usb-communication`)
- **bugfix/***:  Bug fix branches branched from develop (e.g., `bugfix/connection-timeout`)
- **release/***:  Release preparation branches (e.g., `release/v1.0.0`)
- **hotfix/***:  Emergency fixes branched from main (e.g., `hotfix/critical-security-fix`)

### Directory Structure

#### PC Server Component
```
server/
├── api/              # API endpoint definitions
├── auth/             # Authentication logic
├── comm/             # Communication modules
│   ├── usb/          # USB communication code
│   └── wifi/         # WiFi communication code
├── config/           # Configuration management
├── data/             # Data processing logic
├── db/               # Database models and migrations
├── logging/          # Logging framework
├── tests/            # Test modules
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
├── utils/            # Utility functions
├── .gitignore        # Git ignore file
├── requirements.txt  # Python dependencies
├── setup.py          # Package setup script
└── README.md         # Server-specific documentation
```

#### Android Application Component
```
android/
├── app/
│   └── src/
│       ├── main/
│       │   ├── java/com/nfc/readwriter/
│       │   │   ├── api/           # API client code
│       │   │   ├── comm/          # Communication modules
│       │   │   │   ├── usb/       # USB communication code
│       │   │   │   └── wifi/      # WiFi communication code
│       │   │   ├── data/          # Data models and processing
│       │   │   ├── nfc/           # NFC handling code
│       │   │   ├── ui/            # UI components
│       │   │   └── utils/         # Utility functions
│       │   └── res/               # Resources
│       └── test/                  # Unit tests
├── .gitignore                     # Git ignore file
├── build.gradle                   # Build configuration
└── README.md                      # Android-specific documentation
```

#### Project Root
```
/
├── android/          # Android application
├── server/           # PC server application
├── docs/             # Project documentation
├── tools/            # Development tools and scripts
├── .github/          # GitHub configuration
│   ├── workflows/    # GitHub Actions CI/CD
│   └── ISSUE_TEMPLATE/ # Issue templates
├── .gitignore        # Git ignore file
├── README.md         # Project overview
└── LICENSE           # License file
```

## Commit Message Conventions
We follow the Conventional Commits specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Code change that improves performance
- **test**: Adding or correcting tests
- **chore**: Changes to the build process or auxiliary tools and libraries

### Examples:
```
feat(android): implement NFC tag reading service
fix(server): resolve connection timeout issue
docs: update API documentation
test(usb): add unit tests for USB data transmission
```

## Pull Request Process
1. Create a branch from the appropriate base branch
2. Implement changes with appropriate tests
3. Ensure code passes all automated tests
4. Submit PR with a clear description of changes
5. Request review from at least one team member
6. Address any review feedback
7. PR is merged after approval

## PR Template
```markdown
## Description
Brief description of the changes

## Type of change
- [ ] Bug fix
- [ ] New feature
- [ ] Enhancement
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests that you ran

## Checklist:
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## GitHub Actions CI/CD Pipeline

### Workflows to Implement
1. **Unit Testing**: Run unit tests on PR creation and updates
2. **Linting**: Check code style and quality
3. **Integration Testing**: Run integration tests on merge to develop
4. **Build Verification**: Build Android APK and Server package
5. **Documentation Build**: Generate and deploy documentation

### Example CI/CD Pipeline Configuration (Python Server)
```yaml
name: Python CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'server/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'server/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        cd server
        python -m pip install --upgrade pip
        pip install flake8 pytest pytest-cov
        pip install -r requirements.txt
    - name: Lint with flake8
      run: |
        cd server
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
    - name: Test with pytest
      run: |
        cd server
        pytest --cov=./ --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Example CI/CD Pipeline Configuration (Android)
```yaml
name: Android CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'android/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'android/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up JDK
      uses: actions/setup-java@v2
      with:
        java-version: '11'
        distribution: 'adopt'
    - name: Grant execute permission for gradlew
      run: |
        cd android
        chmod +x gradlew
    - name: Run tests
      run: |
        cd android
        ./gradlew test
    - name: Build with Gradle
      run: |
        cd android
        ./gradlew build
```

## Protected Branches Configuration
- **main**
  - Require pull request reviews before merging
  - Require status checks to pass before merging
  - Require branches to be up to date before merging
  - Include administrators in restrictions
  
- **develop**
  - Require pull request reviews before merging
  - Require status checks to pass before merging
  - Require branches to be up to date before merging

## Branch Policies
1. Feature branches should be short-lived
2. Rebase feature branches regularly against develop
3. Delete branches after merging
4. No direct commits to protected branches
5. Keep commits focused and atomic

## Version Control Best Practices
1. Commit frequently with clear messages
2. Keep commits focused on a single change
3. Pull/rebase frequently to stay up-to-date
4. Use issues for tracking work
5. Link commits and PRs to issues
6. Review code thoroughly before approval
7. Maintain a clean commit history

## Versioning Strategy
We follow Semantic Versioning (SemVer):
- Format: MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: Add functionality in a backwards-compatible manner
- PATCH: Backwards-compatible bug fixes

## Issue Templates
- Bug Report
- Feature Request
- Documentation Update
- Performance Issue
- Security Vulnerability

## Setting Up Local Development Environment
1. Clone the repository:
   ```
   git clone https://github.com/organization/nfc-reader-writer-system.git
   ```
2. Set up git hooks for pre-commit checks:
   ```
   cd nfc-reader-writer-system
   # Instructions for setting up pre-commit hooks
   ```
3. Configure git user information:
   ```
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```
4. Create a new feature branch:
   ```
   git checkout develop
   git pull
   git checkout -b feature/your-feature-name
   ```

## Repository Access Management
- Team members will be added as collaborators with appropriate permissions
- External contributors should fork the repository and submit PRs
- Repository admins will manage access control and branch protection
- Two-factor authentication required for all collaborators
