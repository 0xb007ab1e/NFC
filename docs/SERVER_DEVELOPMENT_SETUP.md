# NFC Reader/Writer System - Server Development Setup Guide

## Fundamental Rules (MUST BE FOLLOWED)
1. **No code writing until detailed design and implementation plan is complete**
2. **All tasks must be completed, tested, and verified before marking as complete**
3. **Progress tracking mechanism must be maintained throughout development**
4. **Each context must be seeded with these requirements**

## Prerequisites

Before setting up the development environment, ensure you have the following installed:

- Git
- Python 3.9 or higher
- pip (Python package manager)
- virtualenv or venv

### Optional Tools
- PostgreSQL (for production-like environment testing)
- Docker (for containerized development)
- IDE of your choice (PyCharm, VS Code, etc.)

## Setup Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/organization/nfc-reader-writer-system.git

# Navigate to the project directory
cd nfc-reader-writer-system
```

### 2. Create a Feature Branch

Always work on a feature branch, never directly on `main` or `develop`.

```bash
# Ensure you're on the develop branch
git checkout develop

# Create and switch to a feature branch
git checkout -b feature/your-feature-name
```

### 3. Set Up Python Virtual Environment

```bash
# Navigate to the server directory
cd server

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use any text editor
```

Important settings to configure:
- `NFC_SERVER_PORT`: The port the server will run on
- `DB_TYPE`: Database type (sqlite for development)
- `SECRET_KEY`: Change this for your development environment

### 5. Set Up the Database

```bash
# Create necessary directories
mkdir -p data logs

# The database will be automatically created when you first run the server
```

### 6. Run the Server

```bash
# Run the server
python main.py run --reload
```

The server should now be running at http://127.0.0.1:8000 (or the port you specified in .env).

The API documentation will be available at http://127.0.0.1:8000/api/docs.

## Development Workflow

### Coding Standards

All code must adhere to the project's Python coding standards as defined in [CODING_STANDARDS_PYTHON.md](../CODING_STANDARDS_PYTHON.md).

### Running Tests

```bash
# Run unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run with coverage
pytest --cov=./ --cov-report=html
```

### Linting and Formatting

```bash
# Run flake8 for linting
flake8 .

# Run black for formatting
black .

# Run mypy for type checking
mypy --ignore-missing-imports .
```

### Git Workflow

1. Create a feature branch from `develop`
2. Make changes and commit with conventional commit messages
3. Push branch to remote
4. Create a pull request to `develop`
5. Address review comments
6. Once approved, your branch will be merged

### Commit Message Format

Follow the Conventional Commits specification:

```
<type>[optional scope]: <description>
```

Types:
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Changes that do not affect code behavior
- **refactor**: Code changes that neither fix bugs nor add features
- **perf**: Performance improvements
- **test**: Adding or correcting tests
- **chore**: Changes to build process or auxiliary tools

## Project Structure

```
server/
├── api/              # API endpoint definitions
│   ├── routes/       # Route modules
│   └── app.py        # FastAPI application
├── auth/             # Authentication logic
├── comm/             # Communication modules
│   ├── usb/          # USB communication code
│   └── wifi/         # WiFi communication code
├── config/           # Configuration management
├── data/             # Data directory
├── db/               # Database models and migrations
├── logging/          # Logging framework
├── logs/             # Log files
├── tests/            # Test modules
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
├── utils/            # Utility functions
├── .env              # Environment variables
├── .env.example      # Example environment variables
├── requirements.txt  # Python dependencies
├── setup.py          # Package setup script
└── main.py           # Entry point
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Change the port in your .env file
   - Kill the process using the port: `kill $(lsof -t -i:8000)`

2. **Package installation fails**
   - Ensure you have the latest pip: `pip install --upgrade pip`
   - Install system dependencies (platform-specific)

3. **Database connection issues**
   - For SQLite, check file permissions
   - For PostgreSQL, verify connection settings and credentials

### Getting Help

If you encounter any issues that you can't resolve, please:

1. Check the existing GitHub issues
2. Contact the project lead
3. Create a new issue with detailed information about the problem

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python Testing with pytest](https://docs.pytest.org/)
- [Git Workflow Best Practices](https://www.atlassian.com/git/tutorials/comparing-workflows)
