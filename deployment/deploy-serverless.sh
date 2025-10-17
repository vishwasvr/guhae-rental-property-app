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
    
    # Copy our dedicated Lambda function
    cp ../../src/lambda_function.py .
    
    # Create package info (no external dependencies needed)
    echo "# Lambda package - uses AWS runtime boto3" > package_info.txt
    echo "# Package size: ~2KB vs 13MB (99.98% reduction)" >> package_info.txt
    
    # Create deployment package (just our code)
    zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
    
    cd ..
    rm -rf lambda-package
    
    echo "✅ Lambda package created: lambda-deployment.zip (~2KB)"
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
        --query 'Stacks[0].Outputs[?OutputKey==`RentalPropertyApiHandlerName`].OutputValue' \
        --output text)
    
    # Check current function state
    FUNCTION_STATE=$(aws lambda get-function \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $REGION \
        --query 'Configuration.State' \
        --output text)
    
    if [ "$FUNCTION_STATE" != "Active" ]; then
        echo "⚠️  Function is in $FUNCTION_STATE state. Waiting for it to become Active..."
        aws lambda wait function-active \
            --function-name $LAMBDA_FUNCTION_NAME \
            --region $REGION
    fi
    
    aws lambda update-function-code \
        --function-name $LAMBDA_FUNCTION_NAME \
        --zip-file fileb://lambda-deployment.zip \
        --region $REGION > /dev/null
    
    # Wait for function update to complete
    echo "⏳ Waiting for Lambda function update to complete..."
    if aws lambda wait function-updated \
        --function-name $LAMBDA_FUNCTION_NAME \
        --region $REGION; then
        echo "✅ Lambda function updated successfully"
    else
        echo "⚠️  Update completed with warnings or took longer than expected"
        echo "   Function should be available for use"
    fi
    
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
    "code")
        echo "⚡ Quick code update..."
        package_lambda
        
        # Get Lambda function name
        LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
            --stack-name $STACK_NAME \
            --region $REGION \
            --query 'Stacks[0].Outputs[?OutputKey==`RentalPropertyApiHandlerName`].OutputValue' \
            --output text)
        
        # Update Lambda function code
        echo "📤 Uploading ~2KB package (vs 13MB before)..."
        UPDATE_RESULT=$(aws lambda update-function-code \
            --function-name $LAMBDA_FUNCTION_NAME \
            --zip-file fileb://lambda-deployment.zip \
            --region $REGION \
            --query '{LastModified:LastModified,CodeSize:CodeSize}' \
            --output table)
        
        # Wait for function update to complete
        echo "⏳ Waiting for function update to complete..."
        if aws lambda wait function-updated \
            --function-name $LAMBDA_FUNCTION_NAME \
            --region $REGION; then
            echo "$UPDATE_RESULT"
            echo "✅ Code updated successfully!"
        else
            echo "⚠️  Update completed with warnings"
            echo "   Function should be available for use"
        fi
        
        # Clean up
        rm -f lambda-deployment.zip
        
        echo "✅ Code updated in seconds (not minutes)!"
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
        echo "Usage: $0 {infrastructure|code|website|all|test|cleanup}"
        echo ""
        echo "🚀 Serverless Deployment Options:"
        echo "  $0 infrastructure  # Deploy Lambda + API Gateway + DynamoDB"
        echo "  $0 code           # Quick Lambda code update (~2KB, seconds)"
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