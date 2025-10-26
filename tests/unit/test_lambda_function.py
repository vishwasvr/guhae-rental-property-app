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
        assert 'accessToken' in body
        assert 'user' in body

    @patch('lambda_function.cognito_client')
    def test_handle_login_missing_credentials(self, mock_cognito):
        """Test login with missing credentials"""
        event = {
            'body': json.dumps({})
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.handle_login(event, headers)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] == False
        assert 'required' in body['message']

    @patch('lambda_function.cognito_client')
    def test_handle_login_cognito_error(self, mock_cognito):
        """Test login with Cognito authentication error"""
        mock_cognito.admin_initiate_auth.side_effect = Exception('Invalid credentials')
        
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


class TestRegisterHandler:
    """Test register handler function"""

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
        mock_table.get_item.return_value = {
            'Item': {
                'firstName': 'Test',
                'lastName': 'User',
                'email': 'test@example.com',
                'phone': '123-456-7890'
            }
        }
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_profile(event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['firstName'] == 'Test'
        assert body['lastName'] == 'User'

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
        assert 'error' in body

    @patch('lambda_function.table')
    def test_update_profile_success(self, mock_table, valid_jwt_token):
        """Test successful profile update"""
        mock_table.update_item.return_value = {
            'Attributes': {
                'firstName': 'Updated',
                'lastName': 'User',
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
        assert body['firstName'] == 'Updated'


class TestPropertyFinanceHandlers:
    """Test property finance handler functions"""

    @patch('lambda_function.table')
    def test_get_property_finance_success(self, mock_table, valid_jwt_token):
        """Test successful property finance retrieval"""
        mock_table.get_item.return_value = {
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
        
        event = {
            'headers': {'Authorization': f'Bearer {valid_jwt_token}'}
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.get_property_finance('test-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert 'purchase_price' in body
        assert 'financing' in body

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
        assert 'loan_id' in body

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
                'loan_amount': 210000
            })
        }
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.update_property_loan('test-id', 'loan-id', event, headers)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['loan_amount'] == 210000

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
        
        headers = {'Content-Type': 'application/json'}
        
        response = lambda_function.delete_property_loan('test-id', 'loan-id', headers)
        
        assert response['statusCode'] == 204