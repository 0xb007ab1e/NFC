# NFC Reader/Writer System PC Server Tests

This directory contains tests for the NFC Reader/Writer System PC Server.

## Test Structure

- `api/` - API route tests
- `integration/` - Integration tests
- `unit/` - Unit tests
- `conftest.py` - Test fixtures and configuration
- `test_helpers.py` - Helper functions for creating test resources
- `test_helpers_usage_example.py` - Examples showing how to use the test helpers
- `test_helpers_guide.md` - Guide for using test helpers effectively

## Test Helpers

The `test_helpers.py` module provides functions to quickly create test resources via ORM when testing routes that require existing resources. This approach is faster than creating resources via HTTP requests and gives more precise control over the test state.

Available helpers include:

- Creating users, devices, connections, NFC tags, and records
- Creating related resources in a single operation
- Support for both committed and uncommitted transactions

See `test_helpers_guide.md` for detailed guidance on when and how to use these helpers.

## Running Tests

To run all tests:

```bash
pytest
```

To run API tests:

```bash
pytest tests/api
```

To run specific API test modules:

```bash
pytest tests/api/test_validators.py
pytest tests/api/test_user_routes.py
pytest tests/api/test_device_routes.py
pytest tests/api/test_connection_routes.py
```

To run tests with increased verbosity:

```bash
pytest -v
```

To run tests with coverage reporting:

```bash
pytest --cov=server --cov-report=html
```

## Fixtures

Common test fixtures are defined in `conftest.py`, including:

- `test_db_session` - Provides a fresh database session for each test
- `async_client` - Provides an async test client for API testing
- Various data fixtures for common test data

## Best Practices

1. Keep tests focused on a single aspect of functionality
2. Use helpers to set up prerequisites, but test only one thing per test function
3. For complex test scenarios, use `create_related_resources` to set up related resources
4. Test validator logic directly without HTTP overhead when possible
5. For the actual API endpoint being tested, use HTTP requests to validate the complete request/response cycle
