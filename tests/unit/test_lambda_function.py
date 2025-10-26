import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal
from botocore.exceptions import ClientError

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import lambda_function


class TestLambdaHandler:
    """Test the main Lambda handler function"""

    @patch('lambda_function.table')
    def test_lambda_handler_with_none_context(self, mock_table):
        """Test lambda_handler with None context"""
        mock_table.scan.return_value = {'Items': []}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/health',
            'headers': {}
        }
        response = lambda_function.lambda_handler(event, None)
        assert response['statusCode'] == 200  # Health check should still work

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

    @patch('lambda_function.handle_login')
    def test_lambda_handler_login_route(self, mock_handle_login):
        """Test routing to login endpoint"""
        mock_handle_login.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'POST',
            'path': '/api/auth/login',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_handle_login.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.handle_register')
    def test_lambda_handler_register_route(self, mock_handle_register):
        """Test routing to register endpoint"""
        mock_handle_register.return_value = {'statusCode': 201, 'body': '{}'}
        
        event = {
            'httpMethod': 'POST',
            'path': '/api/auth/register',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_handle_register.assert_called_once()
        assert response['statusCode'] == 201

    @patch('lambda_function.get_profile')
    def test_lambda_handler_get_profile_route(self, mock_get_profile):
        """Test routing to get profile endpoint"""
        mock_get_profile.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/profile',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_get_profile.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.update_profile')
    def test_lambda_handler_update_profile_route(self, mock_update_profile):
        """Test routing to update profile endpoint"""
        mock_update_profile.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'PUT',
            'path': '/api/profile',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_update_profile.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.list_properties')
    def test_lambda_handler_list_properties_route(self, mock_list_properties):
        """Test routing to list properties endpoint"""
        mock_list_properties.return_value = {'statusCode': 200, 'body': '[]'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_list_properties.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.create_property')
    def test_lambda_handler_create_property_route(self, mock_create_property):
        """Test routing to create property endpoint"""
        mock_create_property.return_value = {'statusCode': 201, 'body': '{}'}
        
        event = {
            'httpMethod': 'POST',
            'path': '/api/properties',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_create_property.assert_called_once()
        assert response['statusCode'] == 201

    @patch('lambda_function.get_property_finance')
    def test_lambda_handler_get_property_finance_route(self, mock_get_finance):
        """Test routing to get property finance endpoint"""
        mock_get_finance.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties/test-id/finance',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_get_finance.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.update_property_finance')
    def test_lambda_handler_update_property_finance_route(self, mock_update_finance):
        """Test routing to update property finance endpoint"""
        mock_update_finance.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'PUT',
            'path': '/api/properties/test-id/finance',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_update_finance.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.add_property_loan')
    def test_lambda_handler_add_property_loan_route(self, mock_add_loan):
        """Test routing to add property loan endpoint"""
        mock_add_loan.return_value = {'statusCode': 201, 'body': '{}'}
        
        event = {
            'httpMethod': 'POST',
            'path': '/api/properties/test-id/loans',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_add_loan.assert_called_once()
        assert response['statusCode'] == 201

    @patch('lambda_function.update_property_loan')
    def test_lambda_handler_update_property_loan_route(self, mock_update_loan):
        """Test routing to update property loan endpoint"""
        mock_update_loan.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'PUT',
            'path': '/api/properties/test-id/loans/loan-id',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_update_loan.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.delete_property_loan')
    def test_lambda_handler_delete_property_loan_route(self, mock_delete_loan):
        """Test routing to delete property loan endpoint"""
        mock_delete_loan.return_value = {'statusCode': 204, 'body': ''}
        
        event = {
            'httpMethod': 'DELETE',
            'path': '/api/properties/test-id/loans/loan-id',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_delete_loan.assert_called_once()
        assert response['statusCode'] == 204

    @patch('lambda_function.get_property')
    def test_lambda_handler_get_property_route(self, mock_get_property):
        """Test routing to get property endpoint"""
        mock_get_property.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties/test-id',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_get_property.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.update_property')
    def test_lambda_handler_update_property_route(self, mock_update_property):
        """Test routing to update property endpoint"""
        mock_update_property.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'PUT',
            'path': '/api/properties/test-id',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_update_property.assert_called_once()
        assert response['statusCode'] == 200

    @patch('lambda_function.delete_property')
    def test_lambda_handler_delete_property_route(self, mock_delete_property):
        """Test routing to delete property endpoint"""
        mock_delete_property.return_value = {'statusCode': 204, 'body': ''}
        
        event = {
            'httpMethod': 'DELETE',
            'path': '/api/properties/test-id',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_delete_property.assert_called_once()
        assert response['statusCode'] == 204

    @patch('lambda_function.get_dashboard_stats')
    def test_lambda_handler_dashboard_route(self, mock_get_dashboard):
        """Test routing to dashboard endpoint"""
        mock_get_dashboard.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/dashboard',
            'headers': {}
        }

        response = lambda_function.lambda_handler(event, {})
        
        mock_get_dashboard.assert_called_once()
        assert response['statusCode'] == 200

    def test_lambda_handler_exception_handling(self):
        """Test exception handling in lambda_handler"""
        # Create an event that will cause an exception
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties',  # This should work but we'll mock an exception
            'headers': {}
        }
        
        # Mock the list_properties function to raise an exception
        with patch('lambda_function.list_properties', side_effect=Exception('Test exception')):
            response = lambda_function.lambda_handler(event, {})
            
            assert response['statusCode'] == 500
            body = json.loads(response['body'])
            assert 'error' in body
            assert body['error'] == 'Test exception'


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


class TestLoginHandler:
    """Test login handler function"""

    @patch('lambda_function.cognito_client')
    @patch('lambda_function.table')
    def test_handle_login_success(self, mock_table, mock_cognito):
        """Test successful login"""
        # Mock Cognito responses
        mock_cognito.admin_initiate_auth.return_value = {
            'AuthenticationResult': {
                'AccessToken': 'test-access-token',
                'IdToken': 'test-id-token',
                'RefreshToken': 'test-refresh-token'
            }
        }
        mock_cognito.admin_get_user.return_value = {
            'UserAttributes': [
                {'Name': 'email', 'Value': 'test@example.com'},
                {'Name': 'given_name', 'Value': 'Test'},
                {'Name': 'family_name', 'Value': 'User'}
            ]
        }
        
        # Mock DynamoDB profile fetch
        mock_table.get_item.return_value = {
            'Item': {
                'firstName': 'Test',
                'lastName': 'User',
                'phone': '123-456-7890'
            }
        }
        
        event = {
            'body': json.dumps({
                'username': 'test@example.com',
                'password': 'password123'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_login(event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] == True
        assert 'tokens' in body
        assert 'access_token' in body['tokens']
        assert 'user' in body

    @patch('lambda_function.cognito_client')
    def test_handle_login_invalid_json(self, mock_cognito):
        """Test handle_login with invalid JSON"""
        event = {
            'body': 'invalid json'
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_login(event, headers)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.cognito_client')
    def test_handle_login_cognito_error(self, mock_cognito):
        """Test login with Cognito authentication error"""
        mock_cognito.admin_initiate_auth.side_effect = ClientError({'Error': {'Code': 'NotAuthorizedException', 'Message': 'Invalid credentials'}}, 'AdminInitiateAuth')
        
        event = {
            'body': json.dumps({
                'username': 'test@example.com',
                'password': 'wrongpassword'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_login(event, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert body['success'] == False


class TestGetProperty:
    """Test get_property function"""

    @patch('lambda_function.get_authenticated_user_id')
    def test_get_property_unauthenticated(self, mock_get_auth):
        """Test get_property without authentication"""
        mock_get_auth.return_value = None
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property('test-id', {}, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_get_property_success(self, mock_get_auth, mock_table):
        """Test successful get_property"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'test@example.com'
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property('test-id', {}, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['property']['id'] == 'test-id'

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_get_property_access_denied(self, mock_get_auth, mock_table):
        """Test get_property access denied"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'other@example.com'
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property('test-id', {}, headers)
        
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_get_property_not_found(self, mock_get_auth, mock_table):
        """Test get_property not found"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {}  # No Item
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property('test-id', {}, headers)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body

class TestUpdateProperty:
    """Test update_property function"""

    @patch('lambda_function.get_authenticated_user_id')
    def test_update_property_unauthenticated(self, mock_get_auth):
        """Test update_property without authentication"""
        mock_get_auth.return_value = None
        
        event = {
            'body': json.dumps({
                'title': 'Updated Title'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property('test-id', event, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_update_property_success(self, mock_get_auth, mock_table):
        """Test successful update_property"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'test@example.com'
            }
        }
        mock_table.update_item.return_value = {
            'Attributes': {
                'id': 'test-id',
                'title': 'Updated Title',
                'owner_id': 'test@example.com'
            }
        }
        
        event = {
            'body': json.dumps({
                'title': 'Updated Title'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property('test-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'property' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_update_property_access_denied(self, mock_get_auth, mock_table):
        """Test update_property access denied"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'other@example.com'
            }
        }
        
        event = {
            'body': json.dumps({
                'title': 'Updated Title'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property('test-id', event, headers)
        
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_update_property_not_found(self, mock_get_auth, mock_table):
        """Test update_property not found"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {}  # No Item
        
        event = {
            'body': json.dumps({
                'title': 'Updated Title'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property('test-id', event, headers)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body

class TestDeleteProperty:
    """Test delete_property function"""

    @patch('lambda_function.get_authenticated_user_id')
    def test_delete_property_unauthenticated(self, mock_get_auth):
        """Test delete_property without authentication"""
        mock_get_auth.return_value = None
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.delete_property('test-id', headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_delete_property_success(self, mock_get_auth, mock_table):
        """Test successful delete_property"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'test@example.com'
            }
        }
        mock_table.delete_item.return_value = {}
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.delete_property('test-id', headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'message' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_delete_property_access_denied(self, mock_get_auth, mock_table):
        """Test delete_property access denied"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {
            'Item': {
                'id': 'test-id',
                'title': 'Test Property',
                'owner_id': 'other@example.com'
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.delete_property('test-id', headers)
        
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_delete_property_not_found(self, mock_get_auth, mock_table):
        """Test delete_property not found"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.get_item.return_value = {}  # No Item
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.delete_property('test-id', headers)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body

class TestListProperties:
    """Test list_properties function"""

    @patch('lambda_function.get_authenticated_user_id')
    def test_list_properties_unauthenticated(self, mock_get_auth):
        """Test list_properties without authentication"""
        mock_get_auth.return_value = None
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.list_properties({}, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_list_properties_success(self, mock_get_auth, mock_table):
        """Test successful list_properties"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.query.return_value = {
            'Items': [
                {
                    'pk': 'PROPERTY#test-id',
                    'sk': 'METADATA',
                    'id': 'test-id',
                    'title': 'Test Property',
                    'owner_id': 'test@example.com'
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.list_properties({}, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'properties' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_list_properties_fallback_scan(self, mock_get_auth, mock_table):
        """Test list_properties fallback to scan"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.query.side_effect = Exception("GSI not found")
        mock_table.scan.return_value = {
            'Items': [
                {
                    'pk': 'PROPERTY#test-id',
                    'sk': 'METADATA',
                    'id': 'test-id',
                    'title': 'Test Property',
                    'owner_id': 'test@example.com'
                }
            ]
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.list_properties({}, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'properties' in body

class TestGetDashboardStats:
    """Test get_dashboard_stats function"""

    @patch('lambda_function.get_authenticated_user_id')
    def test_get_dashboard_stats_unauthenticated(self, mock_get_auth):
        """Test get_dashboard_stats without authentication"""
        mock_get_auth.return_value = None
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_dashboard_stats({}, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    @patch('lambda_function.get_authenticated_user_id')
    def test_get_dashboard_stats_success(self, mock_get_auth, mock_table):
        """Test successful get_dashboard_stats"""
        mock_get_auth.return_value = 'test@example.com'
        
        mock_table.query.return_value = {'Items': [{'count': 5}]}
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_dashboard_stats({}, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'total_properties' in body

    @patch('lambda_function.get_authenticated_user_id')
    @patch('lambda_function.table')
    def test_create_property_invalid_data(self, mock_table, mock_get_auth):
        """Test create_property with invalid data"""
        mock_get_auth.return_value = 'test@example.com'
        
        event = {
            'body': json.dumps({
                'title': '',  # Invalid: empty title
                'price': 100000
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.create_property(event, headers)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.get_authenticated_user_id')
    @patch('lambda_function.table')
    def test_create_property_negative_price(self, mock_table, mock_get_auth):
        """Test create_property with negative price"""
        mock_get_auth.return_value = 'test@example.com'
        
        event = {
            'body': json.dumps({
                'title': 'Test Property',
                'price': -1000  # Invalid: negative price
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.create_property(event, headers)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.get_authenticated_user_id')
    def test_create_property_invalid_json(self, mock_get_auth):
        """Test create_property with invalid JSON"""
        mock_get_auth.return_value = 'test@example.com'
        
        event = {
            'body': 'invalid json'
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.create_property(event, headers)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.get_authenticated_user_id')
    def test_create_property_unauthenticated(self, mock_get_auth):
        """Test create_property without authentication"""
        mock_get_auth.return_value = None
        
        event = {
            'body': json.dumps({
                'title': 'Test Property',
                'price': 100000
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.create_property(event, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.cognito_client')
    @patch('lambda_function.table')
    def test_handle_register_success(self, mock_table, mock_cognito):
        """Test successful registration"""
        # Mock Cognito responses
        mock_cognito.admin_create_user.return_value = {
            'User': {
                'Username': 'test@example.com'
            }
        }
        mock_cognito.admin_set_user_password.return_value = {}
        
        # Mock DynamoDB
        mock_table.put_item.return_value = {}
        
        event = {
            'body': json.dumps({
                'username': 'test@example.com',
                'email': 'test@example.com',
                'password': 'password123',
                'firstName': 'Test',
                'lastName': 'User'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_register(event, headers)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['success'] == True
        assert 'user' in body

    @patch('lambda_function.cognito_client')
    def test_handle_register_missing_fields(self, mock_cognito):
        """Test registration with missing required fields"""
        event = {
            'body': json.dumps({
                'email': 'test@example.com'
                # missing password and names
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_register(event, headers)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] == False


class TestProfileHandlers:
    """Test profile handler functions"""

    @patch('lambda_function.table')
    def test_get_profile_success(self, mock_table, valid_jwt_token):
        """Test successful profile retrieval"""
        mock_table.scan.return_value = {
            'Items': [{
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'phone': '123-456-7890'
            }]
        }
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_profile(event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['profile']['firstName'] == 'Test'
        assert body['profile']['lastName'] == 'User'

    @patch('lambda_function.table')
    def test_get_profile_unauthenticated(self, mock_table):
        """Test profile retrieval without authentication"""
        event = {
            'headers': {}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_profile(event, headers)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'message' in body

    @patch('lambda_function.table')
    def test_update_profile_success(self, mock_table, valid_jwt_token):
        """Test successful profile update"""
        mock_table.update_item.return_value = {
            'Attributes': {
                'first_name': 'Updated',
                'last_name': 'User',
                'email': 'test@example.com',
                'updated_at': '2024-01-01T00:00:00Z'
            }
        }
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'},
            'body': json.dumps({
                'firstName': 'Updated',
                'lastName': 'User',
                'phone': '123-456-7890'
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_profile(event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['profile']['firstName'] == 'Updated'


class TestPropertyFinanceHandlers:
    """Test property finance handler functions"""

    @patch('lambda_function.table')
    def test_get_property_finance_success(self, mock_table, valid_jwt_token):
        """Test successful property finance retrieval"""
        # Mock property ownership check first, then finance data
        mock_table.get_item.side_effect = [
            {
                'Item': {
                    'owner_id': 'test@example.com',
                    'title': 'Test Property'
                }
            },
            {
                'Item': {
                    'property_id': 'test-id',
                    'purchase_price': 250000,
                    'financing': {
                        'down_payment': 50000,
                        'loan_amount': 200000,
                        'interest_rate': 3.5
                    }
                }
            }
        ]
        mock_table.query.return_value = {'Items': [{'pk': 'PROPERTY#test-id', 'sk': 'LOAN#1', 'loan_amount': 200000}]}
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property_finance('test-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'finance' in body
        assert 'purchaseInfo' in body['finance']
        assert 'purchasePrice' in body['finance']['purchaseInfo']

    @patch('lambda_function.table')
    def test_get_property_finance_format_exception(self, mock_table, valid_jwt_token):
        """Test format_finance_data exception handling"""
        # Mock property ownership check first, then finance data
        mock_table.get_item.side_effect = [
            {
                'Item': {
                    'owner_id': 'test@example.com',
                    'title': 'Test Property'
                }
            },
            {
                'Item': {
                    'property_id': 'test-id',
                    'purchase_price': 250000
                }
            }
        ]
        mock_table.query.side_effect = Exception("Query failed")
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property_finance('test-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'finance' in body

    @patch('lambda_function.table')
    def test_get_property_finance_unauthorized(self, mock_table, valid_jwt_token):
        """Test property finance access by unauthorized user"""
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'other@example.com',  # Different owner
                'purchase_price': 250000
            }
        }
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property_finance('test-id', event, headers)
        
        assert response['statusCode'] == 403
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('lambda_function.table')
    def test_update_property_finance_success(self, mock_table, valid_jwt_token):
        """Test successful property finance update"""
        # Mock property ownership check
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'test@example.com',
                'title': 'Test Property'
            }
        }
        mock_table.put_item.return_value = {}
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'},
            'body': json.dumps({
                'ownershipType': 'joint',
                'purchasePrice': 300000
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property_finance('test-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'finance' in body


class TestLoanHandlers:
    """Test loan handler functions"""

    @patch('lambda_function.table')
    def test_add_property_loan_success(self, mock_table, valid_jwt_token):
        """Test successful loan addition"""
        # Mock property ownership check
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'test@example.com',
                'title': 'Test Property'
            }
        }
        
        # Mock loan creation
        mock_table.put_item.return_value = {}
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'},
            'body': json.dumps({
                'loan_amount': 200000,
                'interest_rate': 3.5,
                'term_years': 30
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.add_property_loan('test-id', event, headers)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert 'loan' in body
        assert 'id' in body['loan']

    @patch('lambda_function.table')
    def test_update_property_loan_success(self, mock_table, valid_jwt_token):
        """Test successful loan update"""
        # Mock loan ownership check
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'test@example.com',
                'loan_amount': 200000
            }
        }
        
        # Mock loan update
        mock_table.update_item.return_value = {
            'Attributes': {
                'loan_amount': 210000,
                'updated_at': '2024-01-01T00:00:00Z'
            }
        }
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'},
            'body': json.dumps({
                'originalAmount': 210000
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property_loan('test-id', 'loan-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['loan']['originalAmount'] == 210000

    @patch('lambda_function.table')
    def test_delete_property_loan_success(self, mock_table, valid_jwt_token):
        """Test successful loan deletion"""
        # Mock loan ownership check
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'test@example.com',
                'loan_amount': 200000
            }
        }
        
        # Mock loan deletion
        mock_table.delete_item.return_value = {}
        
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {valid_jwt_token}'}
        
        response = lambda_function.delete_property_loan('test-id', 'loan-id', headers)
        
        assert response['statusCode'] == 204


class TestLambdaHandlerIntegration:
    """Integration tests for lambda_handler with various scenarios"""

    @patch('lambda_function.list_properties')
    def test_lambda_handler_list_properties_integration(self, mock_list_properties):
        """Test full integration of list properties through lambda_handler"""
        mock_list_properties.return_value = {'statusCode': 200, 'body': '[]'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties',
            'headers': {'Authorization': 'Bearer test-token'}
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        mock_list_properties.assert_called_once()

    @patch('lambda_function.create_property')
    def test_lambda_handler_create_property_integration(self, mock_create_property):
        """Test full integration of create property through lambda_handler"""
        mock_create_property.return_value = {'statusCode': 201, 'body': '{}'}
        
        event = {
            'httpMethod': 'POST',
            'path': '/api/properties',
            'headers': {'Authorization': 'Bearer test-token'},
            'body': '{"title": "Test Property"}'
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 201
        mock_create_property.assert_called_once()

    @patch('lambda_function.get_property')
    def test_lambda_handler_get_property_integration(self, mock_get_property):
        """Test full integration of get property through lambda_handler"""
        mock_get_property.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/properties/test-id',
            'headers': {'Authorization': 'Bearer test-token'}
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        mock_get_property.assert_called_once()

    @patch('lambda_function.update_property')
    def test_lambda_handler_update_property_integration(self, mock_update_property):
        """Test full integration of update property through lambda_handler"""
        mock_update_property.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'PUT',
            'path': '/api/properties/test-id',
            'headers': {'Authorization': 'Bearer test-token'},
            'body': '{"title": "Updated Title"}'
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        mock_update_property.assert_called_once()

    @patch('lambda_function.delete_property')
    def test_lambda_handler_delete_property_integration(self, mock_delete_property):
        """Test full integration of delete property through lambda_handler"""
        mock_delete_property.return_value = {'statusCode': 204, 'body': ''}
        
        event = {
            'httpMethod': 'DELETE',
            'path': '/api/properties/test-id',
            'headers': {'Authorization': 'Bearer test-token'}
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 204
        mock_delete_property.assert_called_once()

    @patch('lambda_function.get_dashboard_stats')
    def test_lambda_handler_dashboard_integration(self, mock_get_dashboard):
        """Test full integration of dashboard through lambda_handler"""
        mock_get_dashboard.return_value = {'statusCode': 200, 'body': '{}'}
        
        event = {
            'httpMethod': 'GET',
            'path': '/api/dashboard',
            'headers': {'Authorization': 'Bearer test-token'}
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 200
        mock_get_dashboard.assert_called_once()

    def test_lambda_handler_malformed_json(self):
        """Test lambda_handler with malformed JSON in request body"""
        event = {
            'httpMethod': 'POST',
            'path': '/api/properties',
            'headers': {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciJ9.test'},
            'body': 'invalid json'
        }
        
        # This should trigger exception handling in various functions
        response = lambda_function.lambda_handler(event, {})
        
        # Should get a 500 error due to JSON parsing failure
        assert response['statusCode'] == 500

    def test_lambda_handler_missing_event_fields(self):
        """Test lambda_handler with missing required event fields"""
        # Missing httpMethod
        event = {
            'path': '/api/properties',
            'headers': {}
        }
        
        response = lambda_function.lambda_handler(event, {})
        assert response['statusCode'] == 500

    def test_lambda_handler_not_found(self):
        """Test lambda_handler with unknown endpoint"""
        event = {
            'httpMethod': 'GET',
            'path': '/api/unknown',
            'headers': {}
        }
        
        response = lambda_function.lambda_handler(event, {})
        assert response['statusCode'] == 404

    def test_lambda_handler_empty_body_handling(self):
        """Test lambda_handler with empty or None body"""
        event = {
            'httpMethod': 'POST',
            'path': '/api/properties',
            'headers': {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciJ9.test'},
            'body': None
        }
        
        response = lambda_function.lambda_handler(event, {})
        assert response['statusCode'] == 500

    def test_lambda_handler_case_insensitive_headers(self):
        """Test lambda_handler with case-insensitive header handling"""
        event = {
            'httpMethod': 'OPTIONS',
            'path': '/api/properties',
            'headers': {'authorization': 'Bearer test-token'}  # lowercase
        }
        
        response = lambda_function.lambda_handler(event, {})
        assert response['statusCode'] == 200  # CORS should work

    def test_lambda_handler_complex_path_parsing(self):
        """Test lambda_handler with complex path parsing for loans"""
        # Test loan update path parsing
        event = {
            'httpMethod': 'PUT',
            'path': '/api/properties/complex-id-123/loans/loan-id-456',
            'headers': {'Authorization': 'Bearer test-token'}
        }
        
        # Mock the function to avoid actual execution
        with patch('lambda_function.update_property_loan') as mock_update:
            mock_update.return_value = {'statusCode': 200, 'body': '{}'}
            response = lambda_function.lambda_handler(event, {})
            assert response['statusCode'] == 200

    def test_lambda_handler_path_edge_cases(self):
        """Test lambda_handler with various path edge cases"""
        test_cases = [
            # Empty path segments
            ('/api/properties//finance', 'GET'),
            # Very long property IDs
            (f'/api/properties/{"a" * 100}', 'GET'),
            # Special characters in IDs
            ('/api/properties/test_id-with-dashes', 'GET'),
            # Multiple slashes
            ('/api/properties/test///finance', 'GET'),
        ]
        
        for path, method in test_cases:
            event = {
                'httpMethod': method,
                'path': path,
                'headers': {'Authorization': 'Bearer test-token'}
            }
            
            # Should not crash, should return 404 or handle gracefully
            response = lambda_function.lambda_handler(event, {})
            assert 'statusCode' in response


class TestErrorConditions:
    """Test various error conditions to improve coverage"""

    def test_lambda_handler_with_none_event(self):
        """Test lambda_handler with None event"""
        response = lambda_function.lambda_handler(None, {})
        assert response['statusCode'] == 500

    def test_lambda_handler_with_empty_event(self):
        """Test lambda_handler with empty event dict"""
        response = lambda_function.lambda_handler({}, {})
        assert response['statusCode'] == 500

    def test_lambda_handler_with_none_context(self):
        """Test lambda_handler with None context"""
        with patch('lambda_function.table') as mock_table:
            mock_table.scan.return_value = {'Items': []}
            
            event = {
                'httpMethod': 'GET',
                'path': '/api/health',
                'headers': {}
            }
            response = lambda_function.lambda_handler(event, None)
            assert response['statusCode'] == 200  # Health check should still work

    @patch('lambda_function.table')
    def test_health_check_database_error(self, mock_table):
        """Test health check when database is unavailable"""
        mock_table.scan.side_effect = Exception('DynamoDB unavailable')
        
        response = lambda_function.get_health_status({})
        assert response['statusCode'] == 503
        body = json.loads(response['body'])
        assert body['status'] == 'unhealthy'

    def test_convert_floats_edge_cases(self):
        """Test convert_floats_to_decimals with various data types"""
        # Test with None
        result = lambda_function.convert_floats_to_decimals(None)
        assert result is None
        
        # Test with string
        result = lambda_function.convert_floats_to_decimals("string")
        assert result == "string"
        
        # Test with integer
        result = lambda_function.convert_floats_to_decimals(42)
        assert result == 42
        
        # Test with boolean
        result = lambda_function.convert_floats_to_decimals(True)
        assert result == True

    @patch('lambda_function.table')
    def test_format_property_with_missing_fields(self, mock_table):
        """Test format_property with item missing expected fields"""
        item = {
            'pk': 'PROPERTY#test',
            'sk': 'METADATA',
            'title': 'Test Property'
            # Missing many expected fields
        }
        
        formatted = lambda_function.format_property(item)
        assert 'id' in formatted
        assert 'title' in formatted
        # Should handle missing fields gracefully

    @patch('lambda_function.table')
    def test_format_property_with_none_item(self, mock_table):
        """Test format_property with None item"""
        formatted = lambda_function.format_property(None)
        expected = {
            'id': 'unknown',
            'title': 'Unknown Property',
            'description': '',
            'propertyType': 'unknown',
            'status': 'active',
            'createdAt': '',
            'updatedAt': '',
            'images': [],
            'rent': 0,
            'bedrooms': 0,
            'bathrooms': 0,
            'squareFeet': None,
            'garageType': '',
            'garageCars': 0,
            'address': {
                'streetAddress': '',
                'city': '',
                'county': '',
                'state': '',
                'zipCode': '',
                'country': 'US'
            }
        }
        assert formatted == expected

    def test_get_authenticated_user_id_edge_cases(self):
        """Test get_authenticated_user_id with various edge cases"""
        # No headers
        result = lambda_function.get_authenticated_user_id({}, {})
        assert result is None
        
        # Empty headers
        result = lambda_function.get_authenticated_user_id({'headers': {}}, {})
        assert result is None
        
        # Authorization header without Bearer
        event = {'headers': {'Authorization': 'Basic token'}}
        result = lambda_function.get_authenticated_user_id(event, {})
        assert result is None
        
        # Bearer without token
        event = {'headers': {'Authorization': 'Bearer '}}
        result = lambda_function.get_authenticated_user_id(event, {})
        assert result is None
        
        # Case insensitive header
        event = {'headers': {'authorization': 'Bearer test'}}
        result = lambda_function.get_authenticated_user_id(event, {})
        assert result is None  # Will fail JWT validation but tests the header access

    @patch('lambda_function.table')
    def test_list_properties_with_scan_fallback(self, mock_table):
        """Test list_properties when GSI query fails and falls back to scan"""
        # Mock GSI query failure
        mock_table.query.side_effect = Exception('GSI not ready')
        
        # Mock scan success
        mock_table.scan.return_value = {
            'Items': [
                {
                    'pk': 'PROPERTY#1',
                    'sk': 'METADATA',
                    'title': 'Property 1',
                    'owner_id': 'test@example.com'
                }
            ]
        }
        
        event = {'headers': {'Authorization': 'Bearer test'}}
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.list_properties(event, headers)
            assert response['statusCode'] == 200

    @patch('lambda_function.table')
    def test_list_properties_scan_failure(self, mock_table):
        """Test list_properties when both query and scan fail"""
        mock_table.query.side_effect = Exception('GSI error')
        mock_table.scan.side_effect = Exception('Scan error')
        
        event = {'headers': {'Authorization': 'Bearer test'}}
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.list_properties(event, headers)
            assert response['statusCode'] == 500

    @patch('lambda_function.table')
    def test_create_property_validation_error(self, mock_table):
        """Test create_property with invalid data"""
        event = {
            'body': json.dumps({
                'title': '',  # Invalid empty title
                'price': 'not-a-number'  # Invalid price
            })
        }
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.create_property(event, headers)
            # Should handle validation gracefully
            assert 'statusCode' in response

    @patch('lambda_function.table')
    def test_get_property_not_found(self, mock_table):
        """Test get_property when property doesn't exist"""
        mock_table.get_item.return_value = {}  # No Item
        
        event = {'headers': {'Authorization': 'Bearer test'}}
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.get_property('nonexistent', event, headers)
            assert response['statusCode'] == 404

    @patch('lambda_function.table')
    def test_update_property_partial_update(self, mock_table):
        """Test update_property with partial field updates"""
        # Mock existing property
        mock_table.get_item.return_value = {
            'Item': {
                'owner_id': 'test@example.com',
                'title': 'Original Title',
                'price': 200000
            }
        }
        
        # Mock update
        mock_table.update_item.return_value = {
            'Attributes': {
                'title': 'Updated Title',
                'updated_at': '2024-01-01T00:00:00Z'
            }
        }
        
        event = {
            'headers': {'Authorization': 'Bearer test'},
            'body': json.dumps({'title': 'Updated Title'})
        }
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.update_property('test-id', event, headers)
            assert response['statusCode'] == 200

    def test_delete_property_unauthorized(self):
        """Test delete_property with unauthorized user"""
        headers = {}
        
        # Mock unauthorized access
        with patch('lambda_function.get_authenticated_user_id', return_value=None):
            response = lambda_function.delete_property('test-id', headers)
            assert response['statusCode'] == 401

    @patch('lambda_function.table')
    def test_get_dashboard_stats_with_data(self, mock_table):
        """Test get_dashboard_stats with various property statuses"""
        mock_table.scan.return_value = {
            'Items': [
                {'status': 'active', 'title': 'Active Property'},
                {'status': 'inactive', 'title': 'Inactive Property'},
                {'status': 'sold', 'title': 'Sold Property'},
                {'status': 'active', 'title': 'Another Active'}
            ]
        }
        
        event = {'headers': {'Authorization': 'Bearer test'}}
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.get_dashboard_stats(event, headers)
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert 'total_properties' in body
            assert 'active_properties' in body

    @patch('lambda_function.table')
    def test_get_dashboard_stats_empty(self, mock_table):
        """Test get_dashboard_stats with no properties"""
        mock_table.scan.return_value = {'Items': []}
        
        event = {'headers': {'Authorization': 'Bearer test'}}
        headers = {}
        
        with patch('lambda_function.get_authenticated_user_id', return_value='test@example.com'):
            response = lambda_function.get_dashboard_stats(event, headers)
            assert response['statusCode'] == 200
            body = json.loads(response['body'])
            assert body['total_properties'] == 0

    def test_get_authenticated_user_id_edge_cases(self):
        """Test get_authenticated_user_id with various edge cases"""
        # No headers
        result = lambda_function.get_authenticated_user_id({}, {})
        assert result is None
        
        # No Authorization header
        result = lambda_function.get_authenticated_user_id({'headers': {}}, {})
        assert result is None
        
        # Invalid Authorization header
        result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Invalid'}}, {})
        assert result is None

    @patch('lambda_function.requests.get')
    @patch('lambda_function.jwt')
    def test_get_authenticated_user_id_jwt_decoding(self, mock_jwt, mock_requests):
        """Test JWT decoding in get_authenticated_user_id"""
        # Temporarily set UNIT_TEST_MODE to 0
        with patch.dict(os.environ, {'UNIT_TEST_MODE': '0'}):
            mock_requests.return_value.json.return_value = {'keys': [{'kid': 'test'}]}
            mock_jwt.get_unverified_header.return_value = {'kid': 'test', 'alg': 'RS256'}
            mock_jwt.algorithms.RSAAlgorithm.from_jwk.return_value = MagicMock()
            mock_jwt.decode.return_value = {'sub': 'test@example.com'}
            
            result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Bearer valid-token'}}, {})
            assert result == 'test@example.com'

    @patch('lambda_function.requests.get')
    @patch('lambda_function.jwt')
    def test_get_authenticated_user_id_jwt_exception(self, mock_jwt, mock_requests):
        """Test JWT decoding exception in get_authenticated_user_id"""
        # Temporarily set UNIT_TEST_MODE to 0
        with patch.dict(os.environ, {'UNIT_TEST_MODE': '0'}):
            mock_requests.return_value.json.return_value = {'keys': [{'kid': 'test'}]}
            mock_jwt.get_unverified_header.return_value = {'kid': 'test', 'alg': 'RS256'}
            mock_jwt.algorithms.RSAAlgorithm.from_jwk.return_value = MagicMock()
            mock_jwt.decode.side_effect = Exception("Invalid token")
            
            result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Bearer invalid-token'}}, {})
            assert result is None

    @patch('lambda_function.requests.get')
    @patch('lambda_function.jwt')
    def test_get_authenticated_user_id_jwks_exception(self, mock_jwt, mock_requests):
        """Test JWKS fetch exception in get_authenticated_user_id"""
        # Temporarily set UNIT_TEST_MODE to 0
        with patch.dict(os.environ, {'UNIT_TEST_MODE': '0'}):
            mock_requests.side_effect = Exception("Network error")
            
            result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Bearer token'}}, {})
            assert result is None

    @patch('lambda_function.requests.get')
    @patch('lambda_function.jwt')
    def test_get_authenticated_user_id_jwt_no_user_id(self, mock_jwt, mock_requests):
        """Test JWT decoding with no user identifier"""
        # Temporarily set UNIT_TEST_MODE to 0
        with patch.dict(os.environ, {'UNIT_TEST_MODE': '0'}):
            mock_requests.return_value.json.return_value = {'keys': [{'kid': 'test'}]}
            mock_jwt.get_unverified_header.return_value = {'kid': 'test', 'alg': 'RS256'}
            mock_jwt.algorithms.RSAAlgorithm.from_jwk.return_value = MagicMock()
            mock_jwt.decode.return_value = {'sub': None, 'email': None, 'username': None}
            
            result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Bearer valid-token'}}, {})
            assert result is None

    @patch('lambda_function.requests.get')
    @patch('lambda_function.jwt')
    def test_get_authenticated_user_id_no_matching_key(self, mock_jwt, mock_requests):
        """Test no matching key in JWKS"""
        # Temporarily set UNIT_TEST_MODE to 0
        with patch.dict(os.environ, {'UNIT_TEST_MODE': '0'}):
            mock_requests.return_value.json.return_value = {'keys': [{'kid': 'other'}]}
            mock_jwt.get_unverified_header.return_value = {'kid': 'test', 'alg': 'RS256'}
            
            result = lambda_function.get_authenticated_user_id({'headers': {'Authorization': 'Bearer token'}}, {})
            assert result is None

    def test_lambda_handler_invalid_path(self):
        """Test lambda_handler with invalid path"""
        event = {
            'httpMethod': 'GET',
            'path': '/invalid',
            'headers': {}
        }
        
        response = lambda_function.lambda_handler(event, {})
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body

