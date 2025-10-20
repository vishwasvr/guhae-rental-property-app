import pytest
import os
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def set_env_vars():
    """Automatically set required environment variables for all tests"""
    env_vars = {
        'DYNAMODB_TABLE_NAME': 'test-table',
        'S3_BUCKET_NAME': 'test-bucket',
        'COGNITO_USER_POOL_ID': 'test-pool-id',
        'COGNITO_CLIENT_ID': 'test-client-id',
        'AWS_REGION': 'us-east-1'
    }
    with patch.dict(os.environ, env_vars):
        yield

@pytest.fixture
def mock_boto3():
    """Mock boto3 clients and resources"""
    with patch('boto3.resource') as mock_resource, \
         patch('boto3.client') as mock_client:
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_resource.return_value.Table.return_value = mock_table
        
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        
        # Mock Cognito client
        mock_cognito = MagicMock()
        mock_client.return_value = mock_cognito
        
        # Patch the table object in lambda_function module
        from lambda_function import table
        table.scan = mock_table.scan
        table.get_item = mock_table.get_item
        table.put_item = mock_table.put_item
        table.update_item = mock_table.update_item
        table.delete_item = mock_table.delete_item
        table.query = mock_table.query
        
        # Patch cognito_client
        from lambda_function import cognito_client
        cognito_client.admin_create_user = mock_cognito.admin_create_user
        cognito_client.admin_initiate_auth = mock_cognito.admin_initiate_auth
        cognito_client.admin_get_user = mock_cognito.admin_get_user
        cognito_client.admin_set_user_password = mock_cognito.admin_set_user_password
        
        yield mock_resource, mock_client, mock_table, mock_s3, mock_cognito

@pytest.fixture
def mock_requests():
    """Mock requests module"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield mock_get, mock_post

@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        'user_id': 'test-user-123',
        'email': 'test@example.com',
        'name': 'Test User',
        'created_at': '2023-01-01T00:00:00Z'
    }

@pytest.fixture
def sample_property():
    """Sample property data for testing"""
    return {
        'property_id': 'prop-123',
        'user_id': 'test-user-123',
        'address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'zip_code': '12345',
        'rent_amount': 1500.00,
        'created_at': '2023-01-01T00:00:00Z'
    }

@pytest.fixture
def mock_requests():
    """Mock requests library for HTTP calls"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield mock_get, mock_post