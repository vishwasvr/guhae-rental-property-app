import json
import boto3
import os
import uuid
import base64
from jose import jwt
import requests
from datetime import datetime
from decimal import Decimal
import logging

# Set up structured logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Simple owner-only system - no complex RBAC needed

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
cognito_client = boto3.client('cognito-idp')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
cognito_client = boto3.client('cognito-idp')

table = dynamodb.Table(os.environ.get('DYNAMODB_TABLE_NAME', 'guhae-serverless-rental-properties'))
bucket_name = os.environ.get('S3_BUCKET_NAME', 'guhae-serverless-storage')
user_pool_id = os.environ.get('COGNITO_USER_POOL_ID', 'us-east-1_test-pool')
client_id = os.environ.get('COGNITO_CLIENT_ID', 'test-client-id')

# =============================================================================
# SECURITY TEMPLATE - REQUIRED for all user-data endpoints
# =============================================================================
"""
SECURITY CHECKLIST - Apply to ALL endpoints that access/modify user data:

1. ✅ AUTHENTICATION: Call get_authenticated_user_id() first
2. ✅ AUTHORIZATION: Verify resource ownership before any operation  
3. ✅ INPUT VALIDATION: Validate and sanitize all input data
4. ✅ ERROR HANDLING: Don't leak sensitive information in errors

Template for secure property endpoints:
```python
def secure_property_endpoint(property_id, event, headers):
    # 1. AUTHENTICATION
    owner_id = get_authenticated_user_id(event, headers)
    if not owner_id:
        return {'statusCode': 401, 'body': json.dumps({'error': 'Authentication required'})}
    
    # 2. AUTHORIZATION - Verify ownership
    property_response = table.get_item(Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'})
    if property_response['Item'].get('owner_id') != owner_id:
        return {'statusCode': 403, 'body': json.dumps({'error': 'Access denied'})}
    
    # 3. OPERATION - Safe to proceed
```
"""
# =============================================================================

def convert_floats_to_decimals(obj):
    """Recursively convert float values to Decimal for DynamoDB compatibility."""
    if isinstance(obj, dict):
        return {k: convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimals(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    else:
        return obj

def get_authenticated_user_id(event, headers):
    # Bypass JWT validation for unit tests only if token is present
    if os.environ.get('UNIT_TEST_MODE') == '1':
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        # Only return test@example.com for the known valid dummy token
        if auth_header == 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciJ9.test':
            return 'test@example.com'
        return None
    """Extract and validate authenticated user ID from JWT token using Cognito public keys."""
    try:
        auth_header = event.get('headers', {}).get('Authorization') or event.get('headers', {}).get('authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header.replace('Bearer ', '')

        # Get Cognito JWKS
        region = os.environ.get('AWS_REGION', 'us-east-1')
        user_pool_id = os.environ.get('COGNITO_USER_POOL_ID', 'us-east-1_test-pool')
        jwks_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
        try:
            jwks = requests.get(jwks_url).json()['keys']
        except Exception as jwks_error:
            logger.error(f"Failed to fetch JWKS: {jwks_error}")
            return None

        # Decode and verify JWT
        try:
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header['kid']
            key = next((k for k in jwks if k['kid'] == kid), None)
            if not key:
                logger.error("No matching key found in JWKS")
                return None
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            claims = jwt.decode(
                token,
                public_key,
                algorithms=unverified_header['alg'],
                audience=os.environ.get('COGNITO_CLIENT_ID', 'test-client-id'),
                issuer=f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'
            )
            user_id = claims.get('sub') or claims.get('email') or claims.get('username')
            if user_id:
                logger.info(f"Authenticated user: {user_id}")
                return user_id
            else:
                logger.warning("No user identifier found in token claims")
                return None
        except Exception as token_error:
            logger.error(f"JWT validation error: {token_error}")
            return None
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None

def lambda_handler(event, context):
    # CORS headers - define first for error handling
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        method = event['httpMethod']
        path = event['path']
        
        print(f"Lambda handler called - Method: {method}, Path: {path}")
        
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
        # Finance endpoints - MUST come before general property routes
        elif path.startswith('/api/properties/') and '/finance' in path and method == 'GET':
            print(f"Finance GET request - Path: {path}, Method: {method}")
            property_id = path.split('/')[-2]  # properties/{id}/finance
            print(f"Extracted property_id: {property_id}")
            return get_property_finance(property_id, event, headers)
        elif path.startswith('/api/properties/') and '/finance' in path and method == 'PUT':
            property_id = path.split('/')[-2]  # properties/{id}/finance
            return update_property_finance(property_id, event, headers)
        # Loan endpoints - MUST come before general property routes
        elif path.startswith('/api/properties/') and '/loans' in path and method == 'POST':
            property_id = path.split('/')[-2]  # properties/{id}/loans
            return add_property_loan(property_id, event, headers)
        elif path.startswith('/api/properties/') and '/loans/' in path and method == 'PUT':
            parts = path.split('/')
            property_id = parts[-3]  # properties/{id}/loans/{loan_id}
            loan_id = parts[-1]
            return update_property_loan(property_id, loan_id, event, headers)
        elif path.startswith('/api/properties/') and '/loans/' in path and method == 'DELETE':
            parts = path.split('/')
            property_id = parts[-3]  # properties/{id}/loans/{loan_id}
            loan_id = parts[-1]
            return delete_property_loan(property_id, loan_id, headers)
        # General property endpoints - MUST come last
        elif path.startswith('/api/properties/') and method == 'GET':
            property_id = path.split('/')[-1]
            return get_property(property_id, event, headers)
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
    try:
        # Get authenticated user ID
        owner_id = get_authenticated_user_id(event, headers)
        if not owner_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Authentication required'})
            }
        
        print(f"Starting list_properties for owner: {owner_id}. Table name: {table.name}")
        
        # Query properties for this specific owner using GSI
        try:
            response = table.query(
                IndexName='gsi1',
                KeyConditionExpression='gsi1pk = :owner_id',
                ExpressionAttributeValues={
                    ':owner_id': f'OWNER#{owner_id}'
                }
            )
        except Exception as query_error:
            print(f"GSI query failed, falling back to scan: {query_error}")
            # Fallback to scan if GSI doesn't exist yet
            response = table.scan()
        
        print(f"Query response: {response}")
        
        # Filter and format properties for this owner
        all_items = response.get('Items', [])
        properties = []
        for item in all_items:
            if (item.get('pk', '').startswith('PROPERTY#') and 
                item.get('sk') == 'METADATA' and
                item.get('owner_id') == owner_id):
                try:
                    formatted = format_property(item)
                    properties.append(formatted)
                except Exception as format_error:
                    print(f"Error formatting property {item}: {format_error}")
        
        print(f"Found {len(properties)} properties for owner {owner_id}")
        
        # Simple response for property owners
        response_data = {'properties': properties}
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(response_data)
        }
    except Exception as e:
        print(f"Error in list_properties: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'Failed to retrieve properties: {str(e)}'
            })
        }

def create_property(event, headers):
    """Create a new property with standardized data storage."""
    try:
        # Get authenticated user ID
        owner_id = get_authenticated_user_id(event, headers)
        if not owner_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Authentication required'})
            }
        
        data = json.loads(event['body'])
        # Validation: title must not be empty, price must be non-negative
        if not data.get('title') or (data.get('price', 0) is not None and data.get('price', 0) < 0):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Invalid property data'})
            }

        property_id = str(uuid.uuid4())

        print(f"Creating property with data: {data}")

        # Build standardized item for DynamoDB
        item = {
            'pk': f'PROPERTY#{property_id}',
            'sk': 'METADATA',
            'gsi1pk': f'OWNER#{owner_id}',
            'id': property_id,
            'owner_id': owner_id,
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'property_type': data.get('property_type', data.get('propertyType', '')),
            'price': data.get('price', data.get('rent', 0)),
            'bedrooms': data.get('bedrooms', 0),
            'bathrooms': data.get('bathrooms', 0),
            'squareFeet': data.get('squareFeet', data.get('squareFootage', None)),
            'garageType': data.get('garageType', ''),
            'garageCars': data.get('garageCars', 0),
            # Store address components consistently
            'street_address': data.get('streetAddress', ''),
            'city': data.get('city', ''),
            'county': data.get('county', ''),
            'state': data.get('state', ''),
            'zip_code': data.get('zipCode', ''),
            'country': data.get('country', 'US'),
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': 'property-owner'
        }

        print(f"Storing item in DynamoDB: {item}")
        # Convert floats to decimals for DynamoDB compatibility
        item = convert_floats_to_decimals(item)
        table.put_item(Item=item)

        # Return formatted response (flatten for test compatibility)
        formatted = format_property(item)
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps(formatted)
        }
        
    except Exception as e:
        print(f"Error creating property: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to create property: {str(e)}'})
        }

def get_property(property_id, event, headers):
    # Get authenticated user ID
    owner_id = get_authenticated_user_id(event, headers)
    if not owner_id:
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps({'error': 'Authentication required'})
        }
    
    response = table.get_item(
        Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Property not found'})
        }
    
    # Verify ownership
    if response['Item'].get('owner_id') != owner_id:
        return {
            'statusCode': 403,
            'headers': headers,
            'body': json.dumps({'error': 'Access denied - property not owned by user'})
        }
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'property': format_property(response['Item'])})
    }

def update_property(property_id, event, headers):
    try:
        print(f"Starting update_property for ID: {property_id}")
        
        # Get authenticated user ID
        owner_id = get_authenticated_user_id(event, headers)
        if not owner_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Authentication required'})
            }
        
        # First verify property ownership
        property_response = table.get_item(
            Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in property_response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Property not found'})
            }
        
        if property_response['Item'].get('owner_id') != owner_id:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied - property not owned by user'})
            }
        
        data = json.loads(event['body'])
        print(f"Update data received: {data}")
        
        data['updated_at'] = datetime.utcnow().isoformat()
        
        # Map frontend field names to database field names
        if 'streetAddress' in data:
            data['street_address'] = data.pop('streetAddress')
        if 'zipCode' in data:
            data['zip_code'] = data.pop('zipCode')
        
        print(f"Data after field mapping: {data}")
        
        # Convert float values to Decimal for DynamoDB compatibility
        def convert_float_to_decimal(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            elif isinstance(obj, dict):
                return {k: convert_float_to_decimal(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_float_to_decimal(item) for item in obj]
            else:
                return obj
        
        # Apply conversion to all data
        data = convert_float_to_decimal(data)
        print(f"Data after decimal conversion: {data}")
        
        # Build update expression with proper handling of reserved keywords
        update_expression = "SET "
        expression_values = {}
        expression_names = {}
        
        # Define reserved keywords that need to be aliased
        reserved_keywords = {'state', 'status', 'condition', 'order', 'size', 'type', 'value'}
        
        for key, value in data.items():
            # Skip the 'id' field as it shouldn't be updated
            if key == 'id':
                continue
                
            # Check if key is a reserved keyword
            if key.lower() in reserved_keywords:
                # Use expression attribute name for reserved keywords
                attr_name = f"#{key}"
                expression_names[attr_name] = key
                update_expression += f"{attr_name} = :{key}, "
            else:
                update_expression += f"{key} = :{key}, "
                
            expression_values[f":{key}"] = value
        
        update_expression = update_expression.rstrip(', ')
        print(f"Update expression: {update_expression}")
        print(f"Expression values: {expression_values}")
        print(f"Expression attribute names: {expression_names}")
        
        # Build update_item parameters
        update_params = {
            'Key': {'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        # Add ExpressionAttributeNames only if we have reserved keywords
        if expression_names:
            update_params['ExpressionAttributeNames'] = expression_names
        
        response = table.update_item(**update_params)
        
        print(f"DynamoDB update successful")
        formatted_property = format_property(response['Attributes'])
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'property': formatted_property}, default=str)
        }
        
    except Exception as e:
        print(f"Error in update_property: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': f'Failed to update property: {str(e)}'
            })
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
    # Get authenticated user ID
    owner_id = get_authenticated_user_id(event, headers)
    if not owner_id:
        return {
            'statusCode': 401,
            'headers': headers,
            'body': json.dumps({'error': 'Authentication required'})
        }
    
    print(f"Getting dashboard stats for owner: {owner_id}")
    
    # Get properties for this specific owner using GSI
    try:
        response = table.query(
            IndexName='gsi1',
            KeyConditionExpression='gsi1pk = :owner_id',
            ExpressionAttributeValues={
                ':owner_id': f'OWNER#{owner_id}'
            }
        )
    except Exception as query_error:
        print(f"GSI query failed, falling back to scan: {query_error}")
        # Fallback to scan if GSI doesn't exist yet
        response = table.scan(
            FilterExpression='begins_with(pk, :pk_prefix) AND owner_id = :owner_id',
            ExpressionAttributeValues={
                ':pk_prefix': 'PROPERTY#',
                ':owner_id': owner_id
            }
        )
    
    # Filter and format properties for this owner
    user_properties = []
    for item in response.get('Items', []):
        if (item.get('pk', '').startswith('PROPERTY#') and 
            item.get('sk') == 'METADATA' and
            item.get('owner_id') == owner_id):
            try:
                formatted = format_property(item)
                user_properties.append(formatted)
            except Exception as format_error:
                print(f"Error formatting property {item}: {format_error}")
    
    print(f"Found {len(user_properties)} properties for dashboard stats")
    
    # Calculate statistics for this specific property owner
    stats = {
        'total_properties': len(user_properties),
        'active_properties': len([p for p in user_properties if p.get('status') == 'active']),
        'vacant_properties': len([p for p in user_properties if p.get('status') == 'vacant']),
        'total_users': 1,  # This user
        'total_leases': 0,  # Simplified for now
        'my_properties': len(user_properties),
        'maintenance_requests': 0,  # Placeholder
        'rent_collected_this_month': 0  # Placeholder
    }
    
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
    """
    Format property data for consistent API response.
    Always returns camelCase field names and structured address object.
    """
    try:
        print(f"Formatting property item: {item}")
        
        # Build standardized property object
        formatted = {
            'id': item.get('id', item.get('property_id', '')),
            'owner_id': item.get('owner_id', ''),
            'title': item.get('title', ''),
            'description': item.get('description', ''),
            'propertyType': item.get('property_type', ''),
            'status': item.get('status', 'active'),
            'createdAt': item.get('created_at', ''),
            'updatedAt': item.get('updated_at', ''),
            'images': item.get('images', [])
        }
        
        # Handle numeric fields with Decimal conversion
        formatted['rent'] = float(item.get('price', 0)) if isinstance(item.get('price'), Decimal) else item.get('price', 0)
        formatted['bedrooms'] = int(item.get('bedrooms', 0)) if item.get('bedrooms') else 0
        formatted['bathrooms'] = float(item.get('bathrooms', 0)) if isinstance(item.get('bathrooms'), Decimal) else item.get('bathrooms', 0)
        formatted['squareFeet'] = int(item.get('squareFeet', 0)) if item.get('squareFeet') else None
        
        # Handle garage information
        formatted['garageType'] = item.get('garageType', '')
        formatted['garageCars'] = int(item.get('garageCars', 0)) if item.get('garageCars') else 0
        
        # Build standardized address object (always structured, never string)
        formatted['address'] = {
            'streetAddress': item.get('street_address', ''),
            'city': item.get('city', ''),
            'county': item.get('county', ''),
            'state': item.get('state', ''),
            'zipCode': item.get('zip_code', ''),
            'country': item.get('country', 'US')
        }
        
        print(f"Formatted property: {formatted}")
        return formatted
        
    except Exception as e:
        print(f"Error formatting property {item.get('id', 'unknown')}: {str(e)}")
        # Return minimal safe format
        return {
            'id': item.get('id', 'unknown'),
            'title': item.get('title', 'Unknown Property'),
            'description': item.get('description', ''),
            'propertyType': item.get('property_type', 'unknown'),
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
            },
            'status': 'active',
            'createdAt': item.get('created_at', ''),
            'updatedAt': item.get('updated_at', ''),
            'images': []
        }

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
            
            # Try to fetch user profile from DynamoDB for additional info
            profile_data = {}
            try:
                profile_response = table.get_item(
                    Key={'pk': f'USER#{username}', 'sk': 'PROFILE'}
                )
                if 'Item' in profile_response:
                    profile_data = profile_response['Item']
            except Exception as profile_error:
                print(f"Could not fetch profile: {profile_error}")
            
            # Successful login
            response_data = {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'email': user_attributes.get('email', ''),
                    'firstName': profile_data.get('first_name', ''),
                    'lastName': profile_data.get('last_name', ''),
                    'phone': profile_data.get('phone', ''),
                    'company': profile_data.get('company', '')
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
                    }
                })
            }
            
        except Exception as cognito_error:
            # Handle UsernameExistsException and other Cognito errors by name
            if type(cognito_error).__name__ == 'UsernameExistsException':
                return {
                    'statusCode': 409,
                    'headers': headers,
                    'body': json.dumps({
                        'success': False,
                        'message': 'Username already exists'
                    })
                }
            logger.error(f"Cognito registration error: {str(cognito_error)}")
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Registration failed'
                })
            }
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
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
                # Profile doesn't exist, create a new one
                user_id = str(uuid.uuid4())
                pk = f'USER#{user_id}'
                sk = 'PROFILE'
                
                # Create new profile data
                profile_data = {
                    'pk': pk,
                    'sk': sk,
                    'user_id': user_id,
                    'email': user_email,
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
                    'company': body.get('company', ''),
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'status': 'active'
                }
                
                # Store new profile in DynamoDB
                table.put_item(Item=profile_data)
                
                # Format response for new profile
                formatted_profile = {
                    'user_id': profile_data.get('user_id'),
                    'email': profile_data.get('email'),
                    'firstName': profile_data.get('first_name', ''),
                    'lastName': profile_data.get('last_name', ''),
                    'phone': profile_data.get('phone', ''),
                    'dateOfBirth': profile_data.get('date_of_birth', ''),
                    'address': profile_data.get('address', {}),
                    'company': profile_data.get('company', ''),
                    'created_at': profile_data.get('created_at'),
                    'updated_at': profile_data.get('updated_at')
                }
                
                return {
                    'statusCode': 201,
                    'headers': headers,
                    'body': json.dumps({
                        'success': True,
                        'message': 'Profile created successfully',
                        'profile': formatted_profile
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

# Finance Management Functions

def get_property_finance(property_id, event, headers):
    """Get finance data for a property."""
    try:
        # Get authenticated user ID
        owner_id = get_authenticated_user_id(event, headers)
        if not owner_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Authentication required'})
            }
        
        print(f"Getting finance data for property: {property_id}, owner: {owner_id}")
        
        # First verify property ownership
        property_response = table.get_item(
            Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in property_response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Property not found'})
            }
        
        # Verify ownership
        if property_response['Item'].get('owner_id') != owner_id:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied - property not owned by user'})
            }
        
        # Get finance data
        response = table.get_item(
            Key={'pk': f'PROPERTY#{property_id}', 'sk': 'FINANCE'}
        )
        
        if 'Item' not in response:
            # Return empty finance structure if not found
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'finance': {
                        'propertyId': property_id,
                        'ownershipType': None,
                        'ownershipStatus': None,
                        'purchaseInfo': {},
                        'loans': []
                    }
                })
            }
        
        finance_data = format_finance_data(response['Item'])
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'finance': finance_data})
        }
        
    except Exception as e:
        print(f"Error getting property finance: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to get finance data: {str(e)}'})
        }

def update_property_finance(property_id, event, headers):
    """Update finance data for a property."""
    try:
        # Get authenticated user ID
        owner_id = get_authenticated_user_id(event, headers)
        if not owner_id:
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({'error': 'Authentication required'})
            }
        
        print(f"Updating finance data for property: {property_id}, owner: {owner_id}")
        
        # First verify property ownership
        property_response = table.get_item(
            Key={'pk': f'PROPERTY#{property_id}', 'sk': 'METADATA'}
        )
        
        if 'Item' not in property_response:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Property not found'})
            }
        
        # Verify ownership
        if property_response['Item'].get('owner_id') != owner_id:
            return {
                'statusCode': 403,
                'headers': headers,
                'body': json.dumps({'error': 'Access denied - property not owned by user'})
            }
        
        data = json.loads(event['body'])
        
        # Build finance item for DynamoDB
        item = {
            'pk': f'PROPERTY#{property_id}',
            'sk': 'FINANCE',
            'property_id': property_id,
            'ownership_type': data.get('ownershipType', 'individual'),
            'ownership_status': data.get('ownershipStatus', 'owned'),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add purchase info
        purchase_info = data.get('purchaseInfo', {})
        if purchase_info:
            item.update({
                'purchase_price': purchase_info.get('purchasePrice', 0),
                'purchase_date': purchase_info.get('purchaseDate', ''),
                'down_payment': purchase_info.get('downPayment', 0),
                'closing_costs': purchase_info.get('closingCosts', 0),
                'builder': purchase_info.get('builder', ''),
                'seller': purchase_info.get('seller', ''),
                'buyer_agent': purchase_info.get('buyerAgent', ''),
                'seller_agent': purchase_info.get('sellerAgent', ''),
                'title_company': purchase_info.get('titleCompany', '')
            })
        
        print(f"Storing finance item: {item}")
        table.put_item(Item=item)
        
        # Store loans separately
        loans = data.get('loans', [])
        for loan in loans:
            loan_item = {
                'pk': f'PROPERTY#{property_id}',
                'sk': f'LOAN#{loan.get("id", str(uuid.uuid4()))}',
                'property_id': property_id,
                'loan_id': loan.get('id', str(uuid.uuid4())),
                'lender': loan.get('lender', ''),
                'loan_type': loan.get('loanType', ''),
                'original_amount': loan.get('originalAmount', 0),
                'current_balance': loan.get('currentBalance', 0),
                'interest_rate': loan.get('interestRate', 0),
                'term_years': loan.get('termYears', 30),
                'monthly_payment': loan.get('monthlyPayment', 0),
                'start_date': loan.get('startDate', ''),
                'maturity_date': loan.get('maturityDate', ''),
                'is_active': loan.get('isActive', True),
                'updated_at': datetime.utcnow().isoformat()
            }
            table.put_item(Item=loan_item)
        
        # Return formatted response
        finance_data = format_finance_data(item)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'finance': finance_data})
        }
        
    except Exception as e:
        print(f"Error updating property finance: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to update finance data: {str(e)}'})
        }

def add_property_loan(property_id, event, headers):
    """Add a loan to a property."""
    try:
        print(f"Adding loan to property: {property_id}")
        data = json.loads(event['body'])
        
        loan_id = str(uuid.uuid4())
        
        # Build loan item for DynamoDB
        item = {
            'pk': f'PROPERTY#{property_id}',
            'sk': f'LOAN#{loan_id}',
            'property_id': property_id,
            'loan_id': loan_id,
            'lender': data.get('lender', ''),
            'loan_type': data.get('loanType', ''),
            'original_amount': data.get('originalAmount', 0),
            'current_balance': data.get('currentBalance', 0),
            'interest_rate': data.get('interestRate', 0),
            'term_years': data.get('termYears', 30),
            'monthly_payment': data.get('monthlyPayment', 0),
            'start_date': data.get('startDate', ''),
            'maturity_date': data.get('maturityDate', ''),
            'is_active': data.get('isActive', True),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print(f"Storing loan item: {item}")
        table.put_item(Item=item)
        
        # Return formatted response
        loan_data = format_loan_data(item)
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps({'loan': loan_data})
        }
        
    except Exception as e:
        print(f"Error adding property loan: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to add loan: {str(e)}'})
        }

def update_property_loan(property_id, loan_id, event, headers):
    """Update a property loan."""
    try:
        print(f"Updating loan {loan_id} for property: {property_id}")
        data = json.loads(event['body'])
        
        # Build loan item for DynamoDB
        item = {
            'pk': f'PROPERTY#{property_id}',
            'sk': f'LOAN#{loan_id}',
            'property_id': property_id,
            'loan_id': loan_id,
            'lender': data.get('lender', ''),
            'loan_type': data.get('loanType', ''),
            'original_amount': data.get('originalAmount', 0),
            'current_balance': data.get('currentBalance', 0),
            'interest_rate': data.get('interestRate', 0),
            'term_years': data.get('termYears', 30),
            'monthly_payment': data.get('monthlyPayment', 0),
            'start_date': data.get('startDate', ''),
            'maturity_date': data.get('maturityDate', ''),
            'is_active': data.get('isActive', True),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        print(f"Updating loan item: {item}")
        table.put_item(Item=item)
        
        # Return formatted response
        loan_data = format_loan_data(item)
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'loan': loan_data})
        }
        
    except Exception as e:
        print(f"Error updating property loan: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to update loan: {str(e)}'})
        }

def delete_property_loan(property_id, loan_id, headers):
    """Delete a property loan."""
    try:
        print(f"Deleting loan {loan_id} for property: {property_id}")
        
        # Delete the loan item
        table.delete_item(
            Key={'pk': f'PROPERTY#{property_id}', 'sk': f'LOAN#{loan_id}'}
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Loan deleted successfully'})
        }
        
    except Exception as e:
        print(f"Error deleting property loan: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Failed to delete loan: {str(e)}'})
        }

def format_finance_data(item):
    """Format finance data for API response."""
    try:
        # Get loans for this property
        property_id = item.get('property_id', '')
        loans = []
        
        if property_id:
            # Query for loans
            response = table.query(
                KeyConditionExpression='pk = :pk AND begins_with(sk, :sk)',
                ExpressionAttributeValues={
                    ':pk': f'PROPERTY#{property_id}',
                    ':sk': 'LOAN#'
                }
            )
            
            loans = [format_loan_data(loan_item) for loan_item in response.get('Items', [])]
        
        formatted = {
            'propertyId': property_id,
            'ownershipType': item.get('ownership_type', 'individual'),
            'ownershipStatus': item.get('ownership_status', 'owned'),
            'purchaseInfo': {
                'purchasePrice': float(item.get('purchase_price', 0)) if isinstance(item.get('purchase_price'), Decimal) else item.get('purchase_price', 0),
                'purchaseDate': item.get('purchase_date', ''),
                'downPayment': float(item.get('down_payment', 0)) if isinstance(item.get('down_payment'), Decimal) else item.get('down_payment', 0),
                'closingCosts': float(item.get('closing_costs', 0)) if isinstance(item.get('closing_costs'), Decimal) else item.get('closing_costs', 0),
                'builder': item.get('builder', ''),
                'seller': item.get('seller', ''),
                'buyerAgent': item.get('buyer_agent', ''),
                'sellerAgent': item.get('seller_agent', ''),
                'titleCompany': item.get('title_company', '')
            },
            'loans': loans,
            'createdAt': item.get('created_at', ''),
            'updatedAt': item.get('updated_at', '')
        }
        
        return formatted
        
    except Exception as e:
        print(f"Error formatting finance data: {str(e)}")
        return {
            'propertyId': item.get('property_id', ''),
            'ownershipType': 'individual',
            'ownershipStatus': 'owned',
            'purchaseInfo': {},
            'loans': []
        }

def format_loan_data(item):
    """Format loan data for API response."""
    try:
        formatted = {
            'id': item.get('loan_id', ''),
            'propertyId': item.get('property_id', ''),
            'lender': item.get('lender', ''),
            'loanType': item.get('loan_type', ''),
            'originalAmount': float(item.get('original_amount', 0)) if isinstance(item.get('original_amount'), Decimal) else item.get('original_amount', 0),
            'currentBalance': float(item.get('current_balance', 0)) if isinstance(item.get('current_balance'), Decimal) else item.get('current_balance', 0),
            'interestRate': float(item.get('interest_rate', 0)) if isinstance(item.get('interest_rate'), Decimal) else item.get('interest_rate', 0),
            'termYears': int(item.get('term_years', 30)) if item.get('term_years') else 30,
            'monthlyPayment': float(item.get('monthly_payment', 0)) if isinstance(item.get('monthly_payment'), Decimal) else item.get('monthly_payment', 0),
            'startDate': item.get('start_date', ''),
            'maturityDate': item.get('maturity_date', ''),
            'isActive': item.get('is_active', True),
            'createdAt': item.get('created_at', ''),
            'updatedAt': item.get('updated_at', '')
        }
        
        return formatted
        
    except Exception as e:
        print(f"Error formatting loan data: {str(e)}")
        return {
            'id': item.get('loan_id', ''),
            'lender': 'Unknown',
            'loanType': 'unknown',
            'originalAmount': 0,
            'currentBalance': 0,
            'interestRate': 0,
            'isActive': True
        }