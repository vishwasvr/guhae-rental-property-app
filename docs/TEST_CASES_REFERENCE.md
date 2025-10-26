# 📋 Test Cases Reference

This document explains each test case in the Guhae rental property management application for quick reference and onboarding.

## Unit Tests

### tests/unit/test_config.py

- **test_get_aws_config_returns_dict**: Ensures AWS config returns required keys.
- **test_is_feature_enabled_true/false**: Checks feature flag logic for valid/invalid features.
- **test_get_aws_config_missing_key**: Simulates missing config key.
- **test_is_feature_enabled_invalid_type**: Ensures type safety for feature flags.

### tests/unit/test_services.py

- **TestDatabaseService**: CRUD operations, user management, dashboard stats, error/exception handling.
- **TestPropertyService**: Property CRUD, dashboard stats, image upload, formatting, negative scenarios.

### tests/unit/test_utils.py

- **TestValidators**: Validates property data, email, phone; covers valid and invalid cases.
- **TestAWSHelpers**: S3 and DynamoDB helpers, success and failure cases.

### tests/unit/test_lambda_function.py

- **TestLambdaHandler**: Health, CORS, invalid path/method.
- **TestAuthentication**: JWT token validation, error cases.
- **TestPropertyOperations**: Property CRUD, unauthorized, validation error, not found.
- **TestDashboardStats**: Dashboard endpoint.
- **TestUserOperations**: Login, registration, error handling.
- **TestUtilityFunctions**: Data conversion and formatting.

## Integration & Fixtures

- See `tests/integration/` and `tests/fixtures/` for cross-service and shared data tests.

## How to Add New Tests

- Place new unit tests in `tests/unit/`
- Name test functions and classes descriptively
- Cover both positive and negative scenarios

## Related Docs

- [Testing Strategy](TESTING_STRATEGY.md)
- [API Reference](API.md)
