import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lambda_function import lambda_handler

class TestAPIFlows:
    """Integration tests for complete API flows"""

    @pytest.fixture
    def mock_aws_services(self, mock_env):
        """Set up mocked AWS services for integration tests"""
        with patch('boto3.resource') as mock_resource, \
             patch('boto3.client') as mock_client, \
             patch('requests.get') as mock_get:
            
            # Mock DynamoDB
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table
            
            # Mock Cognito
            mock_cognito = MagicMock()
            mock_client.return_value = mock_cognito
            
            # Mock S3
            mock_s3 = MagicMock()
            mock_client.return_value = mock_s3
            
            # Mock Cognito keys request
            mock_keys_response = MagicMock()
            mock_keys_response.json.return_value = {
                'keys': [{
                    'kid': 'test-key-id',
                    'kty': 'RSA',
                    'n': 'test-modulus',
                    'e': 'AQAB'
                }]
            }
            mock_get.return_value = mock_keys_response
            
            yield mock_table, mock_cognito, mock_s3

    def test_user_registration_flow(self, mock_aws_services, mock_requests):
        """Test complete user registration flow"""
        mock_table, mock_cognito, _ = mock_aws_services
        _, mock_post = mock_requests
        
        # Mock Cognito user creation
        mock_cognito.admin_create_user.return_value = {
            'User': {'Username': 'test@example.com'}
        }
        
        # Mock DB operations
        mock_table.put_item.return_value = {}
        mock_table.get_item.return_value = {'Item': {'id': 'user-123'}}
        
        # Registration request
        event = {
            'httpMethod': 'POST',
            'path': '/api/auth/register',
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123!',
                'name': 'Test User'
            }),
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'user_id' in body

    def test_user_login_flow(self, mock_aws_services):
        """Test complete user login flow"""
        mock_table, mock_cognito, _ = mock_aws_services
        
        # Mock Cognito authentication
        mock_cognito.admin_initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token'
            }
        }
        
        # Login request
        event = {
            'httpMethod': 'POST',
            'path': '/api/auth/login',
            'body': json.dumps({
                'email': 'test@example.com',
                'password': 'TestPass123!'
            }),
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'access_token' in body
        assert 'id_token' in body

    def test_property_creation_flow(self, mock_aws_services):
        """Test property creation with authentication"""
        mock_table, mock_cognito, _ = mock_aws_services
        
        # Mock JWT verification
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            # Mock DB operations
            mock_table.put_item.return_value = {}
            
            # Property creation request
            event = {
                'httpMethod': 'POST',
                'path': '/api/properties',
                'headers': {'Authorization': 'Bearer valid.jwt.token'},
                'body': json.dumps({
                    'address': '123 Test Street',
                    'city': 'Test City',
                    'state': 'TS',
                    'zip_code': '12345',
                    'rent_amount': 1500.00
                })
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 201
            body = json.loads(response['body'])
            assert 'id' in body
            assert body['address'] == '123 Test Street'

    def test_property_listing_flow(self, mock_aws_services):
        """Test property listing with authentication"""
        mock_table, mock_cognito, _ = mock_aws_services
        
        # Mock JWT verification
        with patch('lambda_function.verify_jwt_token') as mock_verify:
            mock_verify.return_value = {'sub': 'user-123'}
            
            # Mock DB query
            mock_properties = [
                {'id': 'prop-1', 'address': '123 St'},
                {'id': 'prop-2', 'address': '456 St'}
            ]
            mock_table.query.return_value = {'Items': mock_properties}
            
            # Property listing request
            event = {
                'httpMethod': 'GET',
                'path': '/api/properties',
                'headers': {'Authorization': 'Bearer valid.jwt.token'},
                'queryStringParameters': {}
            }
            
            response = lambda_handler(event, {})
            
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert len(body) == 2
            assert body[0]['address'] == '123 St'

    def test_health_check_flow(self, mock_aws_services):
        """Test health check endpoint"""
        mock_table, _, _ = mock_aws_services
        
        # Mock DB scan
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

    def test_cors_preflight_flow(self, mock_aws_services):
        """Test CORS preflight request"""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/api/properties',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'

    def test_unauthorized_access_flow(self, mock_aws_services):
        """Test accessing protected endpoint without auth"""
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    def test_invalid_method_flow(self, mock_aws_services):
        """Test invalid HTTP method"""
        event = {
            'httpMethod': 'PATCH',
            'path': '/api/health',
            'headers': {}
        }
        
        response = lambda_handler(event, {})
        
        assert response['statusCode'] == 405