# Testing Helpers Guide

This guide explains how to use the testing helpers to efficiently create test resources via ORM when testing routes that require existing resources.

## Overview

The `test_helpers.py` module provides helper functions to quickly create test resources directly via ORM without making HTTP round-trips. This is particularly useful when:

1. Testing routes that require existing resources (e.g., testing connection creation that requires existing users and devices)
2. Testing validator logic without HTTP overhead
3. Setting up complex test scenarios that involve multiple related resources
4. Creating multiple resources for bulk operation testing

## Available Helpers

The following helper functions are available:

- `create_test_user(db, ...)` - Create a test user
- `create_test_device(db, ...)` - Create a test device
- `create_test_connection(db, ...)` - Create a test connection
- `create_test_nfc_tag(db, ...)` - Create a test NFC tag
- `create_test_nfc_record(db, ...)` - Create a test NFC record
- `create_related_resources(db, ...)` - Create multiple related resources in a single operation

## When to Use Helpers vs. HTTP Requests

### Use Helpers When:

- Setting up **prerequisite resources** for the feature you're actually testing
- Testing complex scenarios that require a specific state with multiple resources
- Validating internal logic without HTTP overhead
- Bulk creating resources for performance testing
- You need precise control over resource properties

### Use HTTP Requests When:

- Testing the actual API endpoint being implemented
- Validating HTTP-specific behavior (status codes, headers, etc.)
- Testing the complete request/response cycle including serialization/deserialization
- Testing authentication and authorization flows

## Best Practices

1. **Keep Tests Focused**: Use helpers to set up prerequisites, but test only one thing per test function.

2. **Commit When Needed**: All helpers have a `commit=True` parameter by default. Set to `False` if you're creating multiple resources and want to commit them all at once for better performance.

3. **Transaction Management**: The `test_db_session` fixture already handles transaction rollback between tests, so you don't need to worry about cleaning up resources.

4. **Direct Validation**: For testing validator logic directly, import the validator functions and test them with the session:

   ```python
   from server.api.validators.connection import validate_connection_creation
   
   # Test validator directly
   result = validate_connection_creation(test_db_session, connection_data)
   assert result["is_valid"] is True
   ```

5. **Mix and Match**: You can combine ORM-based resource creation with HTTP requests in the same test when appropriate.

## Example Usage

See `test_helpers_usage_example.py` for complete examples showing how to use these helpers in different testing scenarios.

```python
# Quick example: Create resources and test API
user = create_test_user(test_db_session)
device = create_test_device(test_db_session)

# Now test an API that requires these resources
response = await async_client.post("/api/connection/", json={
    "device_id": str(device.id),
    "user_id": str(user.id),
    # ... other fields
})

assert response.status_code == 201
```

## Extending the Helpers

If you need to create additional types of test resources:

1. Add a new helper function to `test_helpers.py`
2. Follow the same pattern as existing helpers
3. Include default values for common fields
4. Add the `commit` parameter to control transaction behavior
5. Update the `create_related_resources` function if needed

## Troubleshooting

- **Resource Not Found**: Make sure you've committed the transaction if using `commit=False`
- **Relationship Errors**: Check that you're creating resources in the correct order (e.g., create a device before creating a connection that references it)
- **UUID Conversion**: Remember to convert UUID objects to strings when sending to API endpoints
