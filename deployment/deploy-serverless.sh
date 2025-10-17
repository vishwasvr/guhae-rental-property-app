#!/bin/bash

# Guhae Rental Property App - SERVERLESS Deployment
# Ultra-low cost serverless architecture with Lambda + API Gateway
# Perfect for MVP with sporadic usage

set -e

STACK_NAME="guhae-serverless"
REGION="us-east-1"

echo "🚀 Starting SERVERLESS Guhae deployment..."
echo "💰 Estimated idle cost: $0.50-$2/month"
echo "💰 Pay only for actual usage!"

# Function to package and deploy Lambda function
package_lambda() {
    echo "📦 Packaging Lambda function..."
    
    # Create a temporary directory for Lambda package
    mkdir -p lambda-package
    cd lambda-package
    
    # Copy minimal application code
    cp -r ../../src .
    
    # Create Lambda handler that wraps our Flask app
    cat > lambda_function.py << 'EOF'
import json
import boto3
import os
import uuid
import sys
from datetime import datetime

# Add src directory to path
sys.path.insert(0, '/var/task/src')

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')
table_name = os.environ.get('DYNAMODB_TABLE_NAME')
bucket_name = os.environ.get('S3_BUCKET_NAME')

if table_name:
    table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # Get HTTP method and path
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        
        # CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Content-Type': 'application/json'
        }
        
        # Handle CORS preflight
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Import our services
        from services.properties import PropertyService
        property_service = PropertyService()
        
        # Route API requests
        if path.startswith('/api/properties'):
            if method == 'GET' and path == '/api/properties':
                properties = property_service.list_properties(limit=50)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'properties': properties})
                }
            
            elif method == 'POST' and path == '/api/properties':
                body = json.loads(event.get('body', '{}'))
                property_data = property_service.create_property(body)
                return {
                    'statusCode': 201,
                    'headers': headers,
                    'body': json.dumps({'property': property_data})
                }
            
            elif method == 'GET' and '/' in path.split('/api/properties/')[-1]:
                property_id = path.split('/')[-1]
                property_data = property_service.get_property(property_id)
                if property_data:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({'property': property_data})
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'error': 'Property not found'})
                    }
            
            elif method == 'PUT' and '/' in path.split('/api/properties/')[-1]:
                property_id = path.split('/')[-1]
                body = json.loads(event.get('body', '{}'))
                property_data = property_service.update_property(property_id, body)
                if property_data:
                    return {
                        'statusCode': 200,
                        'headers': headers,
                        'body': json.dumps({'property': property_data})
                    }
                else:
                    return {
                        'statusCode': 404,
                        'headers': headers,
                        'body': json.dumps({'error': 'Property not found'})
                    }
            
            elif method == 'DELETE' and '/' in path.split('/api/properties/')[-1]:
                property_id = path.split('/')[-1]
                success = property_service.delete_property(property_id)
                return {
                    'statusCode': 200 if success else 404,
                    'headers': headers,
                    'body': json.dumps({'success': success})
                }
        
        elif path == '/api/dashboard' and method == 'GET':
            stats = property_service.get_dashboard_stats()
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(stats)
            }
        
        elif path == '/api/health' and method == 'GET':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'version': 'serverless-1.0'
                })
            }
        
        # Default response for non-API requests
        else:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
    
    except Exception as e:
        print(f"Lambda error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }
EOF

    # Create requirements for Lambda
    cat > requirements.txt << 'EOF'
boto3==1.34.0
python-dateutil==2.8.2
EOF

    # Install dependencies
    pip install -r requirements.txt -t .
    
    # Create deployment package
    zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
    
    cd ..
    rm -rf lambda-package
    
    echo "✅ Lambda package created: lambda-deployment.zip"
}

# Function to deploy serverless infrastructure
deploy_serverless_infrastructure() {
    echo "📦 Deploying serverless infrastructure..."
    echo "   ✅ Lambda function (API backend)"
    echo "   ✅ API Gateway (REST API)"
    echo "   ✅ CloudFront (Global CDN)"
    echo "   ✅ DynamoDB (pay-per-request)"
    echo "   ✅ S3 (static hosting + storage)"
    
    # Package Lambda function first
    package_lambda
    
    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file cloudformation-serverless.yaml \
        --stack-name $STACK_NAME \
        --parameter-overrides NotificationEmail=admin@guhae.com \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region $REGION
    
    echo "✅ Serverless infrastructure deployed!"
    
    # Update Lambda function code
    echo "⬆️ Uploading Lambda function code..."
    LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION
    
    # Get deployment URLs
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
        --output text)
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`StorageBucketName`].OutputValue' \
        --output text)
    
    echo "✅ Serverless deployment complete!"
    echo ""
    echo "📋 Deployment Information:"
    echo "   🔗 API URL: $API_URL"
    echo "   🌐 Website URL: $CLOUDFRONT_URL"
    echo "   💾 S3 Bucket: $S3_BUCKET"
    echo ""
    echo "🧪 Test your API:"
    echo "   curl $API_URL/api/health"
    echo "   curl $API_URL/api/properties"
    
    # Clean up deployment package
    rm -f lambda-deployment.zip
}

# Function to upload static website files
upload_static_files() {
    echo "📤 Uploading static website files..."
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`StorageBucketName`].OutputValue' \
        --output text)
    
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    # Create a simple static website
    mkdir -p static-site
    
    # Create index.html
    cat > static-site/index.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guhae - Rental Property Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="#"><i class="fas fa-home"></i> Guhae</a>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                <h1>Welcome to Guhae</h1>
                <p class="lead">Your serverless rental property management solution</p>
                
                <div class="card">
                    <div class="card-header">
                        <h5>Properties</h5>
                    </div>
                    <div class="card-body">
                        <div id="properties-list">
                            <p>Loading properties...</p>
                        </div>
                        <button class="btn btn-primary" onclick="addProperty()">Add Property</button>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5>Dashboard</h5>
                    </div>
                    <div class="card-body">
                        <div id="dashboard-stats">
                            <p>Loading stats...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = '${API_URL}';
        
        // Load dashboard stats
        fetch(API_BASE + '/api/dashboard')
            .then(response => response.json())
            .then(data => {
                document.getElementById('dashboard-stats').innerHTML = \`
                    <p><strong>Total Properties:</strong> \${data.total_properties}</p>
                    <p><strong>Active Properties:</strong> \${data.active_properties}</p>
                \`;
            })
            .catch(error => {
                document.getElementById('dashboard-stats').innerHTML = '<p class="text-danger">Error loading stats</p>';
            });
        
        // Load properties
        fetch(API_BASE + '/api/properties')
            .then(response => response.json())
            .then(data => {
                const propertiesList = document.getElementById('properties-list');
                if (data.properties && data.properties.length > 0) {
                    propertiesList.innerHTML = data.properties.map(property => \`
                        <div class="border p-3 mb-3 rounded">
                            <h6>\${property.title || 'Untitled Property'}</h6>
                            <p>\${property.description || 'No description'}</p>
                            <small class="text-muted">Address: \${property.address || 'Not specified'}</small><br>
                            <small class="text-muted">Price: $\${property.price || 0}</small>
                        </div>
                    \`).join('');
                } else {
                    propertiesList.innerHTML = '<p>No properties found. Add your first property!</p>';
                }
            })
            .catch(error => {
                document.getElementById('properties-list').innerHTML = '<p class="text-danger">Error loading properties</p>';
            });
        
        // Add property function
        function addProperty() {
            const title = prompt('Property Title:');
            const description = prompt('Description:');
            const address = prompt('Address:');
            const price = parseFloat(prompt('Price:') || '0');
            
            if (title) {
                fetch(API_BASE + '/api/properties', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title: title,
                        description: description,
                        address: address,
                        price: price
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert('Property added successfully!');
                    location.reload();
                })
                .catch(error => {
                    alert('Error adding property');
                });
            }
        }
    </script>
</body>
</html>
EOF

    # Upload static files to S3
    aws s3 cp static-site/ s3://$S3_BUCKET/static/ --recursive --acl public-read
    aws s3 cp static-site/index.html s3://$S3_BUCKET/index.html --acl public-read
    
    # Clean up
    rm -rf static-site
    
    echo "✅ Static website uploaded!"
}

# Main deployment logic
case "$1" in
    "infrastructure")
        deploy_serverless_infrastructure
        ;;
    "website")
        upload_static_files
        ;;
    "all")
        deploy_serverless_infrastructure
        echo ""
        echo "🌐 Uploading static website..."
        upload_static_files
        
        CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
            --output text)
        
        echo ""
        echo "🎉 Serverless deployment complete!"
        echo "🌐 Your app is live at: $CLOUDFRONT_URL"
        echo "⏰ Note: CloudFront may take 5-10 minutes to fully deploy"
        ;;
    "test")
        # Test the API
        API_URL=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
            --output text)
        
        echo "🧪 Testing API endpoints..."
        echo "Health check:"
        curl -s "$API_URL/api/health" | python3 -m json.tool
        echo ""
        echo "Properties list:"
        curl -s "$API_URL/api/properties" | python3 -m json.tool
        ;;
    "cleanup")
        echo "🧹 Cleaning up serverless resources..."
        aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
        echo "🗑️ CloudFormation stack deletion initiated"
        ;;
    *)
        echo "Usage: $0 {infrastructure|website|all|test|cleanup}"
        echo ""
        echo "🚀 Serverless Deployment Options:"
        echo "  $0 infrastructure  # Deploy Lambda + API Gateway + DynamoDB"
        echo "  $0 website        # Upload static website to S3/CloudFront"
        echo "  $0 all            # Complete serverless deployment"
        echo "  $0 test           # Test API endpoints"
        echo "  $0 cleanup        # Remove all resources"
        echo ""
        echo "💰 SERVERLESS COST COMPARISON:"
        echo "  • EC2 Minimal: $9.11/month idle"
        echo "  • Serverless: $0.50/month idle + usage"
        echo ""
        echo "  📊 Serverless Pricing:"
        echo "    • Lambda: $0.0000166667/request + $0.0000000021/MB-ms"
        echo "    • API Gateway: $3.50/million requests"
        echo "    • CloudFront: $0.085/GB + $0.0075/10k requests"
        echo "    • DynamoDB: $0.25/million reads, $1.25/million writes"
        echo "    • S3: $0.023/GB storage + $0.0004/1k requests"
        echo ""
        echo "  🎯 Example Usage Costs (per month):"
        echo "    • 1,000 page views: ~$0.50"
        echo "    • 10,000 page views: ~$2.00"
        echo "    • 100,000 page views: ~$15.00"
        echo ""
        echo "📋 Prerequisites:"
        echo "  • AWS CLI configured"
        echo "  • Python 3.9+ installed"
        echo "  • pip install boto3"
        exit 1
        ;;
esac

echo "✨ Serverless operation completed!"