import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import lambda_function


class TestLambdaHandler:
    """Test the main Lambda handler function"""

    def test_lambda_handler_health_endpoint(self, mock_lambda_environment, test_table):
        """Test health endpoint returns correct response"""
        with patch('lambda_function.table', test_table):
            event = {
                'httpMethod': 'GET',
                'path': '/api/health',
                'headers': {}
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['status'] == 'healthy'
            body = json.loads(response['body'])
            assert body['status'] == 'healthy'
            assert 'timestamp' in body

    def test_lambda_handler_cors_preflight(self, cors_headers):
        """Test CORS preflight request handling"""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/api/properties',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})

        assert response['statusCode'] == 200
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'

    def test_lambda_handler_invalid_path(self):
        """Test handling of invalid paths"""
        event = {
            'httpMethod': 'GET',
            'path': '/api/invalid',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body

    def test_lambda_handler_invalid_method(self):
        """Test handling of invalid HTTP methods"""
        event = {
            'httpMethod': 'PATCH',
            'path': '/api/properties',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})

        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body


class TestAuthentication:
    """Test authentication functions"""

    def test_get_authenticated_user_id_valid_token(self, valid_jwt_token):
        """Test extracting user ID from valid JWT token"""
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }

        user_id = lambda_function.get_authenticated_user_id(event, {})
        assert user_id == 'test@example.com'

    def test_get_authenticated_user_id_no_token(self):
        """Test handling when no authorization token is provided"""
        event = {'headers': {}}

        user_id = lambda_function.get_authenticated_user_id(event, {})

        assert user_id is None

    def test_get_authenticated_user_id_invalid_token(self, valid_jwt_token):
        """Test handling of invalid JWT token"""
        event = {
            'headers': {'Authorization': 'Bearer invalid.token.value'}
        }

        user_id = lambda_function.get_authenticated_user_id(event, {})
        assert user_id is None


class TestPropertyOperations:
    """Test property CRUD operations"""

    def test_list_properties_success(self, mock_lambda_environment, test_table, sample_property_data, mock_property_item, api_headers):
        """Test successful property listing"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'query', return_value={'Items': [mock_property_item]}):
            event = {
                'httpMethod': 'GET',
                'path': '/api/properties',
                'headers': api_headers
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert isinstance(body, list) or isinstance(body, dict)

    def test_list_properties_unauthenticated(self, mock_lambda_environment):
        """Test property listing without authentication"""
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})

        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    def test_create_property_success(self, mock_lambda_environment, test_table, sample_property_data, api_headers):
        """Test successful property creation"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
                 patch('lambda_function.uuid.uuid4', return_value='test-property-id'):

            event = {
                'httpMethod': 'POST',
                'path': '/api/properties',
                'headers': api_headers,
                'body': json.dumps(sample_property_data)
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 201
            body = json.loads(response['body'])
            assert body['id'] == 'test-property-id'
            assert body['owner_id'] == 'test@example.com'

    def test_create_property_validation_error(self, mock_lambda_environment, api_headers):
        """Test property creation with validation errors"""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "price": -100  # Negative price should fail
        }

        event = {
            'httpMethod': 'POST',
            'path': '/api/properties',
            'headers': api_headers,
            'body': json.dumps(invalid_data)
        }

        response = lambda_function.lambda_handler(event, {})

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body

    def test_get_property_success(self, mock_lambda_environment, test_table, mock_property_item, api_headers):
        """Test successful property retrieval"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'get_item', return_value={'Item': mock_property_item}):
            event = {
                'httpMethod': 'GET',
                'path': '/api/properties/test-property-id',
                'pathParameters': {'property_id': 'test-property-id'},
                'headers': api_headers
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'id' in body or 'property' in body

    def test_get_property_not_found(self, mock_lambda_environment, test_table, api_headers):
        """Test property retrieval when property doesn't exist"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'get_item', return_value={}):
            event = {
                'httpMethod': 'GET',
                'path': '/api/properties/nonexistent',
                'pathParameters': {'property_id': 'nonexistent'},
                'headers': api_headers
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 404
            body = json.loads(response['body'])
            assert 'error' in body

    def test_update_property_success(self, mock_lambda_environment, test_table, mock_property_item, api_headers):
        """Test successful property update"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'get_item', return_value={'Item': mock_property_item}):
            update_data = {
                'title': 'Updated Property Title',
                'price': 300000
            }
            event = {
                'httpMethod': 'PUT',
                'path': '/api/properties/test-property-id',
                'pathParameters': {'property_id': 'test-property-id'},
                'headers': api_headers,
                'body': json.dumps(update_data)
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'id' in body or 'property' in body

    def test_update_property_unauthorized(self, mock_lambda_environment, test_table, mock_property_item, api_headers):
        """Test property update by unauthorized user"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='different@example.com'), \
             patch.object(test_table, 'get_item', return_value={'Item': mock_property_item}):
            update_data = {'title': 'Updated Title'}
            event = {
                'httpMethod': 'PUT',
                'path': '/api/properties/test-property-id',
                'pathParameters': {'property_id': 'test-property-id'},
                'headers': api_headers,
                'body': json.dumps(update_data)
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 403
            body = json.loads(response['body'])
            assert 'error' in body

    def test_delete_property_success(self, mock_lambda_environment, test_table, mock_property_item, api_headers):
        """Test successful property deletion"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'get_item', return_value={'Item': mock_property_item}):
            event = {
                'httpMethod': 'DELETE',
                'path': '/api/properties/test-property-id',
                'pathParameters': {'property_id': 'test-property-id'},
                'headers': api_headers
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['message'] == 'Property deleted'


class TestDashboardStats:
    """Test dashboard statistics functionality"""

    def test_get_dashboard_stats_success(self, mock_lambda_environment, test_table, api_headers):
        """Test successful dashboard stats retrieval"""
        with patch('lambda_function.table', test_table), \
             patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'), \
             patch.object(test_table, 'query', return_value={'Items': [{'count': 5}]}):
            event = {
                'httpMethod': 'GET',
                'path': '/api/dashboard',
                'headers': api_headers
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'total_properties' in body


class TestUserOperations:
    """Test user authentication and profile operations"""

    def test_user_login_success(self, mock_lambda_environment, test_user_pool):
        """Test successful user login"""
        with patch('lambda_function.cognito_client') as mock_cognito:
            mock_cognito.admin_initiate_auth.return_value = {
                'AuthenticationResult': {
                    'AccessToken': 'mock-access-token',
                    'RefreshToken': 'mock-refresh-token',
                    'IdToken': 'mock-id-token'
                }
            }

            login_data = {
                'username': 'test@example.com',
                'password': 'password123'
            }

            event = {
                'httpMethod': 'POST',
                'path': '/api/auth/login',
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(login_data)
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'tokens' in body
            assert 'access_token' in body['tokens']
            assert 'refresh_token' in body['tokens']

    def test_user_register_success(self, mock_lambda_environment, test_user_pool):
        """Test successful user registration"""
        with patch('lambda_function.cognito_client') as mock_cognito, \
             patch('lambda_function.table') as mock_table:
            mock_cognito.admin_create_user.return_value = {
                'User': {
                    'Username': 'test@example.com',
                    'UserStatus': 'CONFIRMED'
                }
            }
            mock_cognito.admin_set_user_password.return_value = {}
            mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

            register_data = {
                'username': 'test@example.com',
                'password': 'password123',
                'email': 'test@example.com',
                'profile': {'firstName': 'Test', 'lastName': 'User'}
            }

            event = {
                'httpMethod': 'POST',
                'path': '/api/auth/register',
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(register_data)
            }

            response = lambda_function.lambda_handler(event, {})

            assert response['statusCode'] == 201
            body = json.loads(response['body'])
            assert body['message'] == 'User registered successfully'


class TestUtilityFunctions:
    """Test utility functions"""

    def test_convert_floats_to_decimals(self):
        """Test conversion of floats to decimals in nested data"""
        test_data = {
            'price': 250000.50,
            'nested': {
                'value': 123.45,
                'list': [1.1, 2.2, 3.3]
            },
            'string': 'unchanged'
        }

        result = lambda_function.convert_floats_to_decimals(test_data)

        assert isinstance(result['price'], Decimal)
        assert isinstance(result['nested']['value'], Decimal)
        assert isinstance(result['nested']['list'][0], Decimal)
        assert result['string'] == 'unchanged'

    def test_format_property(self, mock_property_item):
        """Test property formatting for API responses"""
        formatted = lambda_function.format_property(mock_property_item)
        assert 'id' in formatted
        assert 'owner_id' in formatted
        assert 'createdAt' in formatted
        assert 'updatedAt' in formatted
        # Ensure no internal DynamoDB keys are exposed
        assert 'pk' not in formatted
        assert 'sk' not in formatted