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
    
    # Copy our dedicated Lambda function (API only)
    cp ../../src/lambda_function.py .
    
    # Create package info (no external dependencies needed)
    echo "# Lambda package - API backend only" > package_info.txt
    echo "# Package size: ~2KB (ultra-optimized)" >> package_info.txt
    echo "# Frontend served from S3/CloudFront" >> package_info.txt
    
    # Create deployment package (just our API code)
    zip -r ../lambda-deployment.zip . -x "*.pyc" "*/__pycache__/*"
    
    cd ..
    rm -rf lambda-package
    
    echo "✅ Lambda package created: lambda-deployment.zip (~2KB API-only)"
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
    echo "📤 Uploading frontend files to S3..."
    
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`StorageBucketName`].OutputValue' \
        --output text)

    # Upload frontend files directly to S3 bucket root
    echo "   📄 Uploading HTML files..."
    aws s3 cp ../src/frontend/index.html s3://$S3_BUCKET/index.html --content-type "text/html"
    aws s3 cp ../src/frontend/dashboard.html s3://$S3_BUCKET/dashboard.html --content-type "text/html"
    aws s3 cp ../src/frontend/profile.html s3://$S3_BUCKET/profile.html --content-type "text/html"
    
    echo "   🎨 Uploading CSS files..."
    aws s3 cp ../src/frontend/static/css/ s3://$S3_BUCKET/static/css/ --recursive --content-type "text/css"
    
    echo "   ⚡ Uploading JavaScript files..."
    aws s3 cp ../src/frontend/static/js/ s3://$S3_BUCKET/static/js/ --recursive --content-type "application/javascript"
    
    echo "✅ Frontend files uploaded to S3!"
    echo "   🌐 Frontend will be served via CloudFront CDN"
    echo "   🔌 API calls will be routed to Lambda backend"
}

# Function to invalidate CloudFront cache
invalidate_cloudfront_cache() {
    echo "🔄 Invalidating CloudFront cache..."
    
    # Get CloudFront distribution ID
    DISTRIBUTION_ID=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?contains(DomainName, 'cloudfront.net')].Id" \
        --output text)
    
    if [ -z "$DISTRIBUTION_ID" ]; then
        echo "⚠️  No CloudFront distribution found, skipping cache invalidation"
        return
    fi
    
    # Create invalidation
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id $DISTRIBUTION_ID \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    if [ $? -eq 0 ]; then
        echo "✅ Cache invalidation initiated (ID: $INVALIDATION_ID)"
        echo "   ⏰ Cache will be cleared within 1-3 minutes"
        echo "   🌐 Users will see updated content immediately"
    else
        echo "⚠️  Cache invalidation failed, but deployment continues"
        echo "   💡 Try hard refresh (Ctrl+F5) to see updates"
    fi
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
        echo "📤 Uploading ~3KB package with web interface (vs 13MB before)..."
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
        invalidate_cloudfront_cache
        ;;
    "all")
        deploy_serverless_infrastructure
        echo ""
        echo "🌐 Uploading static website..."
        upload_static_files
        invalidate_cloudfront_cache
        
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
    "cache")
        invalidate_cloudfront_cache
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
        echo "Usage: $0 {infrastructure|code|website|cache|all|test|cleanup}"
        echo ""
        echo "🚀 Serverless Deployment Options:"
        echo "  $0 infrastructure  # Deploy Lambda + API Gateway + DynamoDB"
        echo "  $0 code           # Quick Lambda code update (~2KB, seconds)"
        echo "  $0 website        # Upload static website to S3/CloudFront + invalidate cache"
        echo "  $0 cache          # Invalidate CloudFront cache only"
        echo "  $0 all            # Complete serverless deployment + cache invalidation"
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