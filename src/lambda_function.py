import json
import boto3
import os
import uuid
from datetime import datetime

# Import RBAC utilities
import sys
sys.path.append('/opt/python')  # For Lambda layers
sys.path.append('.')  # For local development
try:
    from utils.rbac import (
        get_user_from_token, has_permission, can_access_resource,
        filter_properties_by_role, add_rbac_context, require_permission
    )
except ImportError:
    # Fallback if RBAC module is not available
    def get_user_from_token(event):
        return {'accountType': 'owner', 'id': 'default'}
    def has_permission(user_data, permission):
        return True
    def can_access_resource(user_data, resource_type, resource_id, action='read'):
        return True
    def filter_properties_by_role(properties, user_data):
        return properties
    def add_rbac_context(response_data, user_data, resource_type=None):
        return response_data
    def require_permission(permission):
        def decorator(func):
            return func
        return decorator

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
cognito_client = boto3.client('cognito-idp')

table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
bucket_name = os.environ['S3_BUCKET_NAME']
user_pool_id = os.environ['COGNITO_USER_POOL_ID']
client_id = os.environ['COGNITO_CLIENT_ID']

def lambda_handler(event, context):
    # CORS headers - define first for error handling
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        method = event['httpMethod']
        path = event['path']
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Route API requests only
        if path == '/api/auth/login' and method == 'POST':
            return handle_login(event, headers)
        elif path == '/api/auth/register' and method == 'POST':
            return handle_register(event, headers)
        elif path == '/api/profile' and method == 'GET':
            return get_profile(event, headers)
        elif path == '/api/profile' and method == 'PUT':
            return update_profile(event, headers)
        elif path == '/api/properties' and method == 'GET':
            return list_properties(event, headers)
        elif path == '/api/properties' and method == 'POST':
            return create_property(event, headers)
        elif path.startswith('/api/properties/') and method == 'GET':
            property_id = path.split('/')[-1]
            return get_property(property_id, headers)
        elif path.startswith('/api/properties/') and method == 'PUT':
            property_id = path.split('/')[-1]
            return update_property(property_id, event, headers)
        elif path.startswith('/api/properties/') and method == 'DELETE':
            property_id = path.split('/')[-1]
            return delete_property(property_id, headers)
        elif path == '/api/dashboard' and method == 'GET':
            return get_dashboard_stats(event, headers)
        elif path == '/api/health' and method == 'GET':
            return get_health_status(headers)
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }

def list_properties(event, headers):
    # Get user data for RBAC filtering
    user_data = get_user_from_token(event)
    
    # Check if user has permission to read properties
    if not has_permission(user_data, 'property.read') and not has_permission(user_data, 'property.read.public'):
        return {
            'statusCode': 403,
            'headers': headers,
            'body': json.dumps({'error': 'Insufficient permissions to view properties'})
        }
    
    response = table.scan(
        FilterExpression='begins_with(pk, :pk_prefix)',
        ExpressionAttributeValues={':pk_prefix': 'PROPERTY#'},
        Limit=50
    )
    
    properties = [format_property(item) for item in response.get('Items', [])]
    
    # Filter properties based on user role
    filtered_properties = filter_properties_by_role(properties, user_data)
    
    # Add RBAC context to response
    response_data = {'properties': filtered_properties}
    response_data = add_rbac_context(response_data, user_data, 'property')
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(response_data)
    }

def create_property(event, headers):
    # Get user data and check permissions
    user_data = get_user_from_token(event)
    
    if not has_permission(user_data, 'property.create'):
        return {
            'statusCode': 403,
            'headers': headers,
            'body': json.dumps({'error': 'Insufficient permissions to create properties'})
        }
    
    data = json.loads(event['body'])
    property_id = str(uuid.uuid4())
    
    # Set owner_id from authenticated user
    owner_id = user_data.get('id', user_data.get('user_id', 'default-owner'))
    
    item = {
        'pk': f'PROPERTY#{property_id}',
        'sk': 'METADATA',
        'gsi1pk': f'OWNER#{owner_id}',
        'id': property_id,
        'owner_id': owner_id,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'address': data.get('address', ''),
        'price': data.get('price', 0),
        'property_type': data.get('property_type', 'residential'),
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'created_by': user_data.get('email', 'unknown'),
        'role_created_by': user_data.get('accountType', 'unknown')
    }
    
    table.put_item(Item=item)
    
    # Add RBAC context to response
    response_data = {'property': format_property(item)}
    response_data = add_rbac_context(response_data, user_data, 'property')
    
    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps(response_data)
    }

def get_property(property_id, headers):
    response = table.get_item(
        Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Property not found'})
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'property': format_property(response['Item'])})
    }

def update_property(property_id, event, headers):
    data = json.loads(event['body'])
    data['updated_at'] = datetime.utcnow().isoformat()
    
    # Build update expression
    update_expression = "SET "
    expression_values = {}
    
    for key, value in data.items():
        update_expression += f"{key} = :{key}, "
        expression_values[f":{key}"] = value
    
    update_expression = update_expression.rstrip(', ')
    
    response = table.update_item(
        Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues='ALL_NEW'
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'property': format_property(response['Attributes'])})
    }

def delete_property(property_id, headers):
    table.delete_item(
        Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'message': 'Property deleted'})
    }

def get_dashboard_stats(event, headers):
    # Get user data for role-based stats
    user_data = get_user_from_token(event)
    
    if not has_permission(user_data, 'property.read') and not has_permission(user_data, 'property.read.own'):
        return {
            'statusCode': 403,
            'headers': headers,
            'body': json.dumps({'error': 'Insufficient permissions to view dashboard'})
        }
    
    # Get properties count (filtered by role)
    response = table.scan(
        FilterExpression='begins_with(pk, :pk_prefix)',
        ExpressionAttributeValues={':pk_prefix': 'PROPERTY#'},
    )
    
    all_properties = [format_property(item) for item in response.get('Items', [])]
    filtered_properties = filter_properties_by_role(all_properties, user_data)
    
    # Calculate role-based statistics
    stats = {
        'total_properties': len(filtered_properties),
        'active_properties': len([p for p in filtered_properties if p.get('status') == 'active']),
        'total_users': 1,  # Simplified for now
        'total_leases': 0,  # Simplified for now
        'user_role': user_data.get('accountType', 'guest') if user_data else 'guest'
    }
    
    # Add role-specific stats
    user_role = user_data.get('accountType', 'guest') if user_data else 'guest'
    
    if user_role in ['owner', 'property_manager']:
        stats.update({
            'my_properties': len(filtered_properties),
            'vacant_properties': len([p for p in filtered_properties if p.get('status') == 'vacant']),
            'maintenance_requests': 0,  # Placeholder
            'rent_collected_this_month': 0  # Placeholder
        })
    elif user_role == 'tenant':
        stats.update({
            'my_lease_status': 'active',  # Placeholder
            'rent_due_date': None,  # Placeholder
            'maintenance_requests_open': 0,  # Placeholder
            'next_payment_amount': 0  # Placeholder
        })
    elif user_role == 'admin':
        stats.update({
            'system_health': 'healthy',
            'total_users': 1,  # Would be actual count in real system
            'total_transactions': 0,  # Placeholder
            'system_alerts': 0  # Placeholder
        })
    
    # Add RBAC context
    stats = add_rbac_context(stats, user_data, 'dashboard')
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps(stats)
    }

def get_health_status(headers):
    """Return API health status"""
    try:
        # Test DynamoDB connection
        response = table.scan(Limit=1)
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0.0',
            'services': {
                'database': 'healthy',
                'storage': 'healthy'
            }
        }
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(health_data)
        }
    except Exception as e:
        health_data = {
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'error': str(e)
        }
        return {
            'statusCode': 503,
            'headers': headers,
            'body': json.dumps(health_data)
        }

def format_property(item):
    # Remove DynamoDB keys and format for API
    formatted = {k: v for k, v in item.items() if not k.startswith(('pk', 'sk', 'gsi'))}
    formatted.setdefault('images', [])
    return formatted

def handle_login(event, headers):
    """Handle user login authentication with Cognito"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Username and password are required'
                })
            }
        
        try:
            # Authenticate with Cognito
            response = cognito_client.admin_initiate_auth(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            # Get user attributes
            user_response = cognito_client.admin_get_user(
                UserPoolId=user_pool_id,
                Username=username
            )
            
            # Extract user info
            user_attributes = {attr['Name']: attr['Value'] for attr in user_response['UserAttributes']}
            
            # Successful login
            response_data = {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'email': user_attributes.get('email', ''),
                    'role': 'user'  # You can enhance this with custom attributes
                },
                'tokens': {
                    'access_token': response['AuthenticationResult']['AccessToken'],
                    'id_token': response['AuthenticationResult']['IdToken'],
                    'refresh_token': response['AuthenticationResult']['RefreshToken']
                }
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data)
            }
            
        except cognito_client.exceptions.NotAuthorizedException:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid username or password'
                })
            }
        except cognito_client.exceptions.UserNotFoundException:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'User not found'
                })
            }
        except Exception as cognito_error:
            print(f"Cognito error: {str(cognito_error)}")
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Authentication failed'
                })
            }
            
    except Exception as e:
        print(f"Login error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Login error occurred',
                'error': str(e)
            })
        }

def handle_register(event, headers):
    """Handle user registration with Cognito and profile storage"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        email = body.get('email', '').strip()
        profile = body.get('profile', {})
        
        if not username or not password or not email:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Username, password, and email are required'
                })
            }
        
        try:
            # Create user attributes for Cognito
            user_attributes = [
                {
                    'Name': 'email',
                    'Value': email
                },
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
            
            # Add profile attributes if provided
            if profile.get('firstName'):
                user_attributes.append({
                    'Name': 'given_name',
                    'Value': profile['firstName']
                })
            
            if profile.get('lastName'):
                user_attributes.append({
                    'Name': 'family_name',
                    'Value': profile['lastName']
                })
                
            if profile.get('phone'):
                # Clean phone number for Cognito (must be in E.164 format)
                phone = profile['phone'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('.', '')
                if not phone.startswith('+'):
                    phone = '+1' + phone  # Assume US number
                user_attributes.append({
                    'Name': 'phone_number',
                    'Value': phone
                })
            
            # Create user in Cognito
            response = cognito_client.admin_create_user(
                UserPoolId=user_pool_id,
                Username=username,
                MessageAction='SUPPRESS',  # Don't send welcome email
                TemporaryPassword=password,
                UserAttributes=user_attributes
            )
            
            # Set permanent password
            cognito_client.admin_set_user_password(
                UserPoolId=user_pool_id,
                Username=username,
                Password=password,
                Permanent=True
            )
            
            # Store extended profile in DynamoDB
            user_id = str(uuid.uuid4())
            profile_data = {
                'pk': f'USER#{user_id}',
                'sk': 'PROFILE',
                'user_id': user_id,
                'cognito_username': username,
                'email': email,
                'first_name': profile.get('firstName', ''),
                'last_name': profile.get('lastName', ''),
                'phone': profile.get('phone', ''),
                'date_of_birth': profile.get('dateOfBirth', ''),
                'address': profile.get('address', {}),
                'account_type': profile.get('accountType', 'tenant'),
                'company': profile.get('company', ''),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            # Store profile in DynamoDB
            table.put_item(Item=profile_data)
            
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'User registered successfully',
                    'user': {
                        'user_id': user_id,
                        'username': username,
                        'email': email,
                        'first_name': profile.get('firstName', ''),
                        'last_name': profile.get('lastName', ''),
                        'account_type': profile.get('accountType', 'tenant')
                    }
                })
            }
            
        except cognito_client.exceptions.UsernameExistsException:
            return {
                'statusCode': 409,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Username already exists'
                })
            }
        except Exception as cognito_error:
            print(f"Cognito registration error: {str(cognito_error)}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Registration failed'
                })
            }
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Registration error occurred',
                'error': str(e)
            })
        }

def get_profile(event, headers):
    """Get user profile information"""
    try:
        # Get user ID from JWT token (simplified for now)
        # In production, decode and validate JWT token
        user_email = event.get('requestContext', {}).get('authorizer', {}).get('claims', {}).get('email')
        
        if not user_email:
            # For now, get from query parameters or headers as fallback
            user_email = event.get('queryStringParameters', {}).get('email') if event.get('queryStringParameters') else None
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Authentication required'
                })
            }
        
        # Query DynamoDB for user profile
        try:
            response = table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': user_email}
            )
            
            if not response['Items']:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Profile not found'
                    })
                }
            
            profile = response['Items'][0]
            
            # Format profile response
            profile_data = {
                'user_id': profile.get('user_id'),
                'email': profile.get('email'),
                'firstName': profile.get('first_name', ''),
                'lastName': profile.get('last_name', ''),
                'phone': profile.get('phone', ''),
                'dateOfBirth': profile.get('date_of_birth', ''),
                'address': profile.get('address', {}),
                'accountType': profile.get('account_type', 'tenant'),
                'company': profile.get('company', ''),
                'status': profile.get('status', 'active'),
                'created_at': profile.get('created_at'),
                'updated_at': profile.get('updated_at')
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'profile': profile_data
                })
            }
            
        except Exception as db_error:
            print(f"Database error: {str(db_error)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to retrieve profile'
                })
            }
            
    except Exception as e:
        print(f"Profile retrieval error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Profile retrieval error occurred',
                'error': str(e)
            })
        }

def update_profile(event, headers):
    """Update user profile information"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Get user email (in production, extract from JWT)
        user_email = body.get('email') or event.get('queryStringParameters', {}).get('email')
        
        if not user_email:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Authentication required'
                })
            }
        
        # Find existing profile
        try:
            response = table.scan(
                FilterExpression='email = :email',
                ExpressionAttributeValues={':email': user_email}
            )
            
            if not response['Items']:
                return {
                    'statusCode': 404,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Profile not found'
                    })
                }
            
            existing_profile = response['Items'][0]
            pk = existing_profile['pk']
            sk = existing_profile['sk']
            
            # Prepare update data
            update_data = {
                'first_name': body.get('firstName', ''),
                'last_name': body.get('lastName', ''),
                'phone': body.get('phone', ''),
                'date_of_birth': body.get('dateOfBirth', ''),
                'address': {
                    'street': body.get('streetAddress', ''),
                    'city': body.get('city', ''),
                    'state': body.get('state', ''),
                    'zipCode': body.get('zipCode', '')
                },
                'account_type': body.get('accountType', 'tenant'),
                'company': body.get('company', ''),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Build update expression
            update_expression = "SET "
            expression_values = {}
            
            for key, value in update_data.items():
                update_expression += f"{key} = :{key}, "
                expression_values[f":{key}"] = value
            
            update_expression = update_expression.rstrip(', ')
            
            # Update profile in DynamoDB
            updated_response = table.update_item(
                Key={'pk': pk, 'sk': sk},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_values,
                ReturnValues='ALL_NEW'
            )
            
            updated_profile = updated_response['Attributes']
            
            # Format response
            profile_data = {
                'user_id': updated_profile.get('user_id'),
                'email': updated_profile.get('email'),
                'firstName': updated_profile.get('first_name', ''),
                'lastName': updated_profile.get('last_name', ''),
                'phone': updated_profile.get('phone', ''),
                'dateOfBirth': updated_profile.get('date_of_birth', ''),
                'address': updated_profile.get('address', {}),
                'accountType': updated_profile.get('account_type', 'tenant'),
                'company': updated_profile.get('company', ''),
                'updated_at': updated_profile.get('updated_at')
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': profile_data
                })
            }
            
        except Exception as db_error:
            print(f"Database update error: {str(db_error)}")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Failed to update profile'
                })
            }
            
    except Exception as e:
        print(f"Profile update error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Profile update error occurred',
                'error': str(e)
            })
        }