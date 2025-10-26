# 🧪 Testing Strategy

This document describes the comprehensive testing approach for the Guhae rental property management application.

## Goals

- Ensure all code is covered by automated tests before deployment
- Catch regressions and edge cases early
- Provide confidence in production releases

## Test Types

- **Unit Tests**: Validate individual functions, classes, and endpoints. Located in `tests/unit/`.
- **Integration Tests**: Validate interactions between components and AWS services. Located in `tests/integration/`.
- **Fixtures**: Shared test data and mocks in `tests/fixtures/`.

## Coverage Enforcement

- 100% coverage required for all code in `src/` (see `pytest.ini`)
- CI/CD pipeline blocks deployment if coverage drops below 100%

## Mocking & Isolation

- AWS services (DynamoDB, S3, Cognito) are mocked using `moto` and `unittest.mock.patch`
- No real AWS calls are made during unit tests

## Negative & Edge Case Testing

- All endpoints and services are tested for error handling, invalid input, and edge cases
- Tests assert correct status codes and error messages

## How to Run Tests

```bash
pytest
```

## How to Check Coverage

```bash
pytest --cov=src --cov-report=term-missing
```

## Continuous Integration

- GitHub Actions and other CI tools run all tests and enforce coverage on every push
- See `.github/workflows/` for pipeline config

## Related Docs

- [API Reference](API.md)
- [Development Guide](DEVELOPMENT.md)
- [Deployment Guide](DEPLOYMENT.md)
