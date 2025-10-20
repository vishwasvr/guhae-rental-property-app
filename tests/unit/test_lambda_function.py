import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Set environment variables before importing lambda_function
os.environ.setdefault('DYNAMODB_TABLE_NAME', 'test-table')
os.environ.setdefault('S3_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('COGNITO_USER_POOL_ID', 'test-pool-id')
os.environ.setdefault('COGNITO_CLIENT_ID', 'test-client-id')
os.environ.setdefault('AWS_REGION', 'us-east-1')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lambda_function import (
    verify_jwt_token,
    validate_input,
    sanitize_string,
    get_authenticated_user_id,
    lambda_handler,
    get_health_status,
    handle_register,
    handle_login,
    get_property,
    update_property,
    delete_property,
    get_profile,
    update_profile,
    get_property_finance,
    update_property_finance,
    get_dashboard_stats
)

class TestJWTVerification:
    """Test JWT token verification"""

    def test_verify_jwt_token_valid(self):
        """Test verifying a valid JWT token"""
        # Mock Cognito keys response
        mock_keys = [{
            'kid': 'test-key-id',
            'kty': 'RSA',
            'n': 'test-modulus',
            'e': 'AQAB'
        }]
        mock_response = MagicMock()
        mock_response.json.return_value = {'keys': mock_keys}
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            # Mock JWT decode
            with patch('jwt.decode') as mock_decode:
                mock_decode.return_value = {'sub': 'test-user-id', 'exp': 2000000000}
                
                with patch('jwt.get_unverified_header') as mock_header:
                    mock_header.return_value = {'kid': 'test-key-id'}
                    
                    result = verify_jwt_token('valid.jwt.token')
                    assert result is not None
                    assert result['sub'] == 'test-user-id'

    def test_verify_jwt_token_invalid_header(self):
        """Test JWT with invalid header"""
        with patch('jwt.get_unverified_header') as mock_header:
            mock_header.return_value = {}
            
            result = verify_jwt_token('invalid.jwt.token')
            assert result is None

    def test_verify_jwt_token_expired(self):
        """Test expired JWT token"""
        mock_keys = [{'kid': 'test-key-id'}]
        mock_response = MagicMock()
        mock_response.json.return_value = {'keys': mock_keys}
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = mock_response
            
            with patch('jwt.decode') as mock_decode:
                mock_decode.side_effect = Exception("Token expired")
                
                with patch('jwt.get_unverified_header') as mock_header:
                    mock_header.return_value = {'kid': 'test-key-id'}
                    
                    result = verify_jwt_token('expired.jwt.token')
                    assert result is None

class TestInputValidation:
    """Test input validation functions"""

    def test_validate_input_valid(self):
        """Test validating valid input"""
        data = {'name': 'Test', 'email': 'test@example.com'}
        required = ['name', 'email']
        
        result = validate_input(data, required)
        assert result == (True, None)

    def test_validate_input_missing_field(self):
        """Test validation with missing required field"""
        data = {'name': 'Test'}
        required = ['name', 'email']
        
        result = validate_input(data, required)
        assert result[0] == False
        assert 'email' in result[1]

    def test_validate_input_empty_value(self):
        """Test validation with empty value"""
        data = {'name': '', 'email': 'test@example.com'}
        required = ['name', 'email']
        
        result = validate_input(data, required)
        assert result[0] == False
        assert 'name' in result[1]

    def test_sanitize_string_valid(self):
        """Test sanitizing valid string"""
        result = sanitize_string("Test String")
        assert result == "Test String"

    def test_sanitize_string_too_long(self):
        """Test sanitizing string that's too long"""
        long_string = "a" * 300
        result = sanitize_string(long_string, max_length=255)
        assert len(result) == 255

    def test_sanitize_string_with_script(self):
        """Test sanitizing string with potential XSS - just strips/truncates"""
        malicious = "<script>alert('xss')</script>"
        result = sanitize_string(malicious)
        # The function only strips whitespace and truncates, doesn't remove HTML
        assert result == "<script>alert('xss')</script>"

class TestAuthentication:
    """Test authentication functions"""

    def test_get_authenticated_user_id_valid(self):
        """Test getting authenticated user ID with valid token"""
        headers = {'Authorization': 'Bearer valid.jwt.token'}
        event = {'headers': headers}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'test-user-id'}
            
            result = get_authenticated_user_id(event, headers)
            assert result == 'test-user-id'

    def test_get_authenticated_user_id_no_header(self):
        """Test getting user ID without auth header"""
        headers = {}
        event = {'headers': headers}
        
        result = get_authenticated_user_id(event, headers)
        assert result is None

    def test_get_authenticated_user_id_invalid_token(self):
        """Test getting user ID with invalid token"""
        headers = {'Authorization': 'Bearer invalid.token'}
        event = {'headers': headers}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = None
            
            result = get_authenticated_user_id(event, headers)
            assert result is None

class TestLambdaHandler:
    """Test main Lambda handler"""

    def test_lambda_handler_health_get(self, mock_boto3):
        """Test health endpoint GET request"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        mock_table.scan.return_value = {'Items': []}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/health',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'healthy'

    def test_lambda_handler_options_cors(self):
        """Test OPTIONS request for CORS"""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/api/properties',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'

    def test_lambda_handler_invalid_method(self):
        """Test invalid HTTP method - returns 404 for unrecognized routes"""
        event = {
            'httpMethod': 'PATCH',
            'path': '/api/health',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 404

class TestHealthStatus:
    """Test health status function"""

    def test_get_health_status_success(self, mock_boto3):
        """Test successful health check"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        mock_table.scan.return_value = {'Items': []}
        
        result = get_health_status({})
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['status'] == 'healthy'

class TestRegistration:
    """Test user registration"""

    def test_handle_register_success(self, mock_boto3, mock_requests):
        """Test successful user registration"""
        mock_resource, mock_client, mock_table, _, mock_cognito = mock_boto3
        _, mock_post = mock_requests
        
        # Mock Cognito signup
        mock_cognito.admin_create_user.return_value = {
            'User': {'Username': 'test@example.com'}
        }
        
        # Mock table put
        mock_table.put_item.return_value = {}
        
        event = {
            'body': json.dumps({
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'name': 'Test User'
            })
        }
        
        response = handle_register(event, {})
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'user' in body
        assert 'user_id' in body['user']

    def test_handle_register_invalid_input(self):
        """Test registration with invalid input"""
        event = {
            'body': json.dumps({
                'email': 'invalid-email',
                'password': 'short'
            })
        }
        
        response = handle_register(event, {})
        
        assert response['statusCode'] == 400

class TestLogin:
    """Test user login"""

    def test_handle_login_success(self, mock_boto3):
        """Test successful login"""
        mock_resource, mock_client, mock_table, _, mock_cognito = mock_boto3
        
        # Mock Cognito auth
        mock_cognito.admin_initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token',
                'RefreshToken': 'test-refresh-token'
            }
        }
        
        # Mock Cognito get user
        mock_cognito.admin_get_user.return_value = {
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'}
            ]
        }
        
        # Mock profile lookup
        mock_table.get_item.return_value = {}
        
        event = {
            'body': json.dumps({
                'username': 'test@example.com',
                'password': 'TestPass123!'
            })
        }
        
        response = handle_login(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'tokens' in body
        assert 'access_token' in body['tokens']

class TestPropertyOperations:
    """Test property CRUD operations"""

    def test_get_property_success(self, mock_boto3):
        """Test getting an existing property"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_property = {
            'id': 'prop-123',
            'owner_id': 'user-123',
            'address': '123 Test St'
        }
        mock_table.get_item.return_value = {'Item': mock_property}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {
                'headers': {'Authorization': 'Bearer valid.token'},
                'path': '/api/properties/prop-123'
            }
            
            response = get_property('prop-123', event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'property' in body

    def test_get_property_not_found(self, mock_boto3):
        """Test getting a non-existent property"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.get_item.return_value = {}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {'headers': {'Authorization': 'Bearer valid.token'}}
            
            response = get_property('non-existent', event, {})
            
            assert response['statusCode'] == 404

    def test_get_property_unauthorized(self, mock_boto3):
        """Test getting a property owned by another user"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_property = {
            'id': 'prop-123',
            'owner_id': 'other-user',
            'address': '123 Test St'
        }
        mock_table.get_item.return_value = {'Item': mock_property}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {'headers': {'Authorization': 'Bearer valid.token'}}
            
            response = get_property('prop-123', event, {})
            
            assert response['statusCode'] == 403

    def test_update_property_success(self, mock_boto3):
        """Test updating a property"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.update_item.return_value = {
            'Attributes': {
                'id': 'prop-123',
                'address': '456 New St',
                'updated_at': '2023-01-01T00:00:00Z'
            }
        }
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {
                'headers': {'Authorization': 'Bearer valid.token'},
                'body': json.dumps({'address': '456 New St'})
            }
            
            response = update_property('prop-123', event, {})
            
            assert response['statusCode'] == 200
            mock_table.update_item.assert_called_once()

    def test_delete_property_success(self, mock_boto3):
        """Test deleting a property"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.delete_item.return_value = {}
        
        response = delete_property('prop-123', {})
        
        assert response['statusCode'] == 200
        mock_table.delete_item.assert_called_once_with(
            Key={'pk': 'PROPERTY#prop-123', 'sk': 'METADATA'}
        )

class TestProfileOperations:
    """Test profile management operations"""

    def test_get_profile_success(self, mock_boto3):
        """Test getting user profile"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_profile = {
            'user_id': 'user-123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        mock_table.scan.return_value = {'Items': [mock_profile]}
        
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {'email': 'test@example.com'}
                }
            }
        }
        
        response = get_profile(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'profile' in body

    def test_get_profile_not_found(self, mock_boto3):
        """Test getting profile for non-existent user"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.scan.return_value = {'Items': []}
        
        event = {
            'requestContext': {
                'authorizer': {
                    'claims': {'email': 'nonexistent@example.com'}
                }
            }
        }
        
        response = get_profile(event, {})
        
        assert response['statusCode'] == 404

    def test_update_profile_success(self, mock_boto3):
        """Test updating user profile"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.update_item.return_value = {'Attributes': {}}
        
        event = {
            'body': json.dumps({
                'email': 'test@example.com',
                'firstName': 'Updated',
                'lastName': 'Name'
            })
        }
        
        response = update_profile(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True

class TestFinanceOperations:
    """Test finance-related operations"""

    def test_get_property_finance_success(self, mock_boto3):
        """Test getting property finance data"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        # Mock property ownership check
        mock_table.get_item.side_effect = [
            {'Item': {'owner_id': 'user-123'}},  # Property metadata
            {'Item': {}}  # Finance data (empty)
        ]
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {'headers': {'Authorization': 'Bearer valid.token'}}
            
            response = get_property_finance('prop-123', event, {})
            
            assert response['statusCode'] == 200

    def test_update_property_finance_success(self, mock_boto3):
        """Test updating property finance data"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        # Mock property ownership check
        mock_table.get_item.return_value = {'Item': {'owner_id': 'user-123'}}
        mock_table.update_item.return_value = {'Attributes': {}}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {
                'headers': {'Authorization': 'Bearer valid.token'},
                'body': json.dumps({'monthly_rent': 1600})
            }
            
            response = update_property_finance('prop-123', event, {})
            
            assert response['statusCode'] == 200

class TestDashboardOperations:
    """Test dashboard operations"""

    def test_get_dashboard_stats_success(self, mock_boto3):
        """Test getting dashboard statistics"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_items = [
            {'pk': 'PROPERTY#1', 'sk': 'METADATA'},
            {'pk': 'PROPERTY#2', 'sk': 'METADATA'}
        ]
        mock_table.query.return_value = {'Items': mock_items}
        
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            event = {'headers': {'Authorization': 'Bearer valid.token'}}
            
            response = get_dashboard_stats(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'total_properties' in body