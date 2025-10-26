# Testing Guide

This project includes comprehensive unit testing with 90% minimum code coverage requirements.

## Test Structure

```
tests/
├── conftest.py          # Shared test fixtures and configuration
├── unit/
│   ├── test_lambda_function.py  # Lambda function endpoint tests
│   ├── test_utils.py           # Utility function tests
│   └── test_services.py        # Database and property service tests
└── integration/         # Integration tests (future)
```

## Running Tests Locally

### Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

### Run Specific Test Files

```bash
pytest tests/unit/test_lambda_function.py
pytest tests/unit/test_utils.py
pytest tests/unit/test_services.py
```

### Run Tests with Different Markers

```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests (when available)
pytest -m "not slow"    # Skip slow tests
```

## Test Coverage Requirements

- **Minimum Coverage**: 90% of all code must be covered by tests
- **Coverage Reports**: Generated in HTML format (`htmlcov/`) and XML (`coverage.xml`)
- **CI/CD Enforcement**: Pipeline fails if coverage drops below 90%

## Test Categories

### Unit Tests

- **Lambda Functions**: All API endpoints and handlers
- **Utilities**: Validators, AWS helpers, data transformations
- **Services**: Database operations, property management

### Integration Tests

- End-to-end API workflows
- Database and external service interactions

## Writing New Tests

### Test File Naming

- Unit tests: `test_*.py`
- Integration tests: `test_*_integration.py`

### Test Function Naming

```python
def test_descriptive_name():
    """Test description"""
    # Arrange
    # Act
    # Assert
```

### Using Fixtures

```python
def test_example(mock_lambda_environment, sample_property_data):
    """Example test using fixtures"""
    # Test implementation
```

## Key Fixtures Available

- `aws_credentials`: Mock AWS credentials
- `dynamodb_mock`: Mock DynamoDB service
- `s3_mock`: Mock S3 service
- `cognito_mock`: Mock Cognito service
- `test_table`: Pre-configured test DynamoDB table
- `test_bucket`: Test S3 bucket
- `sample_property_data`: Sample property data
- `sample_user_data`: Sample user data
- `valid_jwt_token`: Mock JWT token
- `api_headers`: Standard API headers

## Mocking Strategy

- **AWS Services**: Use `moto` library for comprehensive AWS mocking
- **External APIs**: Mock with `unittest.mock`
- **Environment Variables**: Set in test fixtures
- **Database Operations**: Mock table operations

## Coverage Exclusions

The following are excluded from coverage requirements:

- `__init__.py` files
- Test files themselves
- Cache directories
- Migration files
- Lines marked with `# pragma: no cover`

## CI/CD Integration

Tests run automatically on every push to `develop` branch:

1. Install dependencies
2. Run linting (flake8)
3. Security scanning (bandit)
4. Custom security audit
5. **Unit tests with coverage** (fails if <90%)
6. CloudFormation validation
7. Deploy to development environment

## Debugging Failed Tests

### View Coverage Gaps

```bash
pytest --cov=src --cov-report=term-missing
```

### Run Single Failing Test

```bash
pytest tests/unit/test_lambda_function.py::TestLambdaHandler::test_lambda_handler_health -v
```

### Debug with PDB

```bash
pytest --pdb tests/unit/test_lambda_function.py
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Mock External Dependencies**: Don't rely on real AWS services
3. **Descriptive Names**: Test names should explain what they test
4. **Arrange-Act-Assert**: Follow this pattern in all tests
5. **Edge Cases**: Test error conditions and edge cases
6. **Documentation**: Add docstrings to complex test functions

## Adding New Test Files

1. Create test file in appropriate directory
2. Import required modules and fixtures
3. Write comprehensive test cases
4. Run tests to ensure they pass
5. Check coverage to ensure new code is covered

## Troubleshooting

### Import Errors

- Ensure `PYTHONPATH` includes `src/` directory
- Check that all dependencies are installed

### AWS Mocking Issues

- Use `aws_credentials` fixture first
- Ensure all AWS clients are created after mocking

### Coverage Issues

- Check `.coveragerc` configuration
- Ensure test files are in `tests/` directory
- Verify source paths in coverage configuration
