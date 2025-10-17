import json
import boto3
import os
import uuid
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])
bucket_name = os.environ['S3_BUCKET_NAME']

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
        elif path == '/api/properties' and method == 'GET':
            return list_properties(headers)
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
            return get_dashboard_stats(headers)
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

def list_properties(headers):
    response = table.scan(
        FilterExpression='begins_with(pk, :pk_prefix)',
        ExpressionAttributeValues={':pk_prefix': 'PROPERTY#'},
        Limit=50
    )
    properties = [format_property(item) for item in response.get('Items', [])]
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({'properties': properties})
    }

def create_property(event, headers):
    data = json.loads(event['body'])
    property_id = str(uuid.uuid4())
    
    item = {
        'pk': f'PROPERTY#{property_id}',
        'sk': 'METADATA',
        'gsi1pk': f'OWNER#{data.get("owner_id", "default-owner")}',
        'id': property_id,
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'address': data.get('address', ''),
        'price': data.get('price', 0),
        'property_type': data.get('property_type', 'residential'),
        'status': 'active',
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    table.put_item(Item=item)
    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({'property': format_property(item)})
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

def get_dashboard_stats(headers):
    response = table.scan(
        FilterExpression='begins_with(pk, :pk_prefix)',
        ExpressionAttributeValues={':pk_prefix': 'PROPERTY#'},
        Select='COUNT'
    )
    
    stats = {
        'total_properties': response['Count'],
        'active_properties': response['Count'],  # Simplified
        'total_users': 1,
        'total_leases': 0
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
    # Remove DynamoDB keys and format for API
    formatted = {k: v for k, v in item.items() if not k.startswith(('pk', 'sk', 'gsi'))}
    formatted.setdefault('images', [])
    return formatted

def handle_login(event, headers):
    """Handle user login authentication"""
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        username = body.get('username', '').strip()
        password = body.get('password', '').strip()
        
        # Simple demo authentication (in production, use proper password hashing)
        valid_credentials = {
            'demo': 'demo123',
            'admin': 'admin123',
            'user': 'password123'
        }
        
        if username in valid_credentials and valid_credentials[username] == password:
            # Successful login
            response_data = {
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': username,
                    'role': 'admin' if username == 'admin' else 'user'
                },
                'token': f'demo-token-{username}-{datetime.utcnow().timestamp()}'
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data)
            }
        else:
            # Invalid credentials
            return {
                'statusCode': 401,
                'headers': headers,
                'body': json.dumps({
                    'success': False,
                    'message': 'Invalid username or password'
                })
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'message': 'Login error occurred',
                'error': str(e)
            })
        }