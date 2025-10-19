#!/bin/bash

# Guhae Rental Property App - IMPROVED SERVERLESS Deployment
# Following DevOps and AWS deployment best practices
# Version: 2.0 - Production Ready

set -euo pipefail  # Strict error handling

# Configuration with environment override support
STACK_NAME="${STACK_NAME:-guhae-serverless}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@guhae.com}"

# Colors for better output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

# Validation functions
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.9+."
        exit 1
    fi
    
    # Check required files
    local required_files=(
        "cloudformation-serverless.yaml"
        "../src/lambda_function.py"
        "../src/utils"
        "../src/frontend"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -e "$file" ]]; then
            log_error "Required file/directory not found: $file"
            exit 1
        fi
    done
    
    log_success "Prerequisites validated"
}

validate_parameters() {
    # Validate stack name
    if [[ ! "$STACK_NAME" =~ ^[a-zA-Z][a-zA-Z0-9-]*$ ]]; then
        log_error "Invalid stack name. Must start with letter and contain only letters, numbers, and hyphens."
        exit 1
    fi
    
    # Validate region
    if ! aws ec2 describe-regions --region-names "$REGION" &> /dev/null; then
        log_error "Invalid AWS region: $REGION"
        exit 1
    fi
    
    # Validate email
    if [[ ! "$NOTIFICATION_EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        log_error "Invalid email format: $NOTIFICATION_EMAIL"
        exit 1
    fi
    
    log_success "Parameters validated"
}

# Enhanced package function with error handling
package_lambda() {
    log_info "Packaging Lambda function..."
    
    local temp_dir="lambda-package-$$"
    
    # Cleanup function that doesn't rely on variables outside its scope
    cleanup_lambda_package() {
        # Use pattern matching instead of variable
        if [[ -d lambda-package-* ]]; then
            rm -rf lambda-package-*
        fi
        if [[ -f "lambda-deployment.zip" ]]; then
            rm -f "lambda-deployment.zip"
        fi
    }
    
    # Set trap for cleanup
    trap cleanup_lambda_package EXIT
    
    # Create temporary directory
    mkdir -p "$temp_dir"
    
    # Copy source files with error handling
    if ! cp "../src/lambda_function.py" "$temp_dir/"; then
        log_error "Failed to copy lambda_function.py"
        exit 1
    fi
    
    if ! cp -r "../src/utils" "$temp_dir/"; then
        log_error "Failed to copy utils directory"
        exit 1
    fi
    
    # Create package metadata
    cat > "$temp_dir/deployment_info.json" << EOF
{
    "deployment_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "$ENVIRONMENT",
    "stack_name": "$STACK_NAME",
    "region": "$REGION",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "package_size": "~3KB"
}
EOF
    
    # Create deployment package
    (
        cd "$temp_dir"
        if ! zip -r "../lambda-deployment.zip" . -x "*.pyc" "*/__pycache__/*" "*.DS_Store"; then
            log_error "Failed to create deployment package"
            exit 1
        fi
    )
    
    # Get package size
    local package_size
    package_size=$(du -h lambda-deployment.zip | cut -f1)
    
    log_success "Lambda package created: lambda-deployment.zip ($package_size)"
}

# Enhanced infrastructure deployment
deploy_serverless_infrastructure() {
    log_info "Deploying serverless infrastructure..."
    log_info "Stack: $STACK_NAME | Region: $REGION | Environment: $ENVIRONMENT"
    
    # Package Lambda function first
    package_lambda
    
    # Check if stack exists
    local stack_exists=false
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        stack_exists=true
        log_info "Stack exists, performing update..."
    else
        log_info "Creating new stack..."
    fi
    
    # Deploy CloudFormation stack with proper error handling
    if aws cloudformation deploy \
        --template-file cloudformation-serverless.yaml \
        --stack-name "$STACK_NAME" \
        --parameter-overrides \
            NotificationEmail="$NOTIFICATION_EMAIL" \
            Environment="$ENVIRONMENT" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --region "$REGION" \
        --no-fail-on-empty-changeset; then
        
        if $stack_exists; then
            log_success "Infrastructure updated successfully"
        else
            log_success "Infrastructure created successfully"
        fi
    else
        log_error "CloudFormation deployment failed"
        exit 1
    fi
    
    # Update Lambda function code with retry logic
    update_lambda_function
    
    # Display deployment information
    display_deployment_info
}

# Enhanced Lambda function update with retry logic
update_lambda_function() {
    log_info "Updating Lambda function code..."
    
    local lambda_function_name
    lambda_function_name=$(get_stack_output "RentalPropertyApiHandlerName")
    
    if [[ -z "$lambda_function_name" ]]; then
        log_error "Could not retrieve Lambda function name from stack outputs"
        exit 1
    fi
    
    # Wait for function to be active
    wait_for_function_active "$lambda_function_name"
    
    # Update function with retry
    local max_retries=3
    local retry_count=0
    
    while (( retry_count < max_retries )); do
        if aws lambda update-function-code \
            --function-name "$lambda_function_name" \
            --zip-file fileb://lambda-deployment.zip \
            --region "$REGION" > /dev/null; then
            
            log_info "Waiting for function update to complete..."
            if aws lambda wait function-updated \
                --function-name "$lambda_function_name" \
                --region "$REGION"; then
                log_success "Lambda function updated successfully"
                return 0
            fi
        fi
        
        ((retry_count++))
        log_warning "Update attempt $retry_count failed, retrying..."
        sleep 10
    done
    
    log_error "Failed to update Lambda function after $max_retries attempts"
    exit 1
}

# Utility functions
get_stack_output() {
    local output_key="$1"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query "Stacks[0].Outputs[?OutputKey=='$output_key'].OutputValue" \
        --output text
}

wait_for_function_active() {
    local function_name="$1"
    
    local function_state
    function_state=$(aws lambda get-function \
        --function-name "$function_name" \
        --region "$REGION" \
        --query 'Configuration.State' \
        --output text)
    
    if [[ "$function_state" != "Active" ]]; then
        log_info "Function is in $function_state state. Waiting for it to become Active..."
        aws lambda wait function-active \
            --function-name "$function_name" \
            --region "$REGION"
    fi
}

display_deployment_info() {
    log_info "Retrieving deployment information..."
    
    local api_url cloudfront_url s3_bucket
    api_url=$(get_stack_output "ApiGatewayUrl")
    cloudfront_url=$(get_stack_output "CloudFrontUrl")
    s3_bucket=$(get_stack_output "StorageBucketName")
    
    echo ""
    log_success "Serverless deployment complete!"
    echo ""
    echo "📋 Deployment Information:"
    echo "   🏗️  Stack Name: $STACK_NAME"
    echo "   🌍 Region: $REGION"
    echo "   🏷️  Environment: $ENVIRONMENT"
    echo "   🔗 API URL: $api_url"
    echo "   🌐 Website URL: $cloudfront_url"
    echo "   💾 S3 Bucket: $s3_bucket"
    echo ""
    echo "🧪 Test Commands:"
    echo "   curl \"$api_url/api/health\""
    echo "   curl \"$api_url/api/properties\""
}

# Enhanced static file upload
upload_static_files() {
    log_info "Uploading frontend files to S3..."
    
    local s3_bucket
    s3_bucket=$(get_stack_output "StorageBucketName")
    
    if [[ -z "$s3_bucket" ]]; then
        log_error "Could not retrieve S3 bucket name from stack outputs"
        exit 1
    fi
    
    # Validate frontend directory
    if [[ ! -d "../src/frontend" ]]; then
        log_error "Frontend directory not found: ../src/frontend"
        exit 1
    fi
    
    # Upload with proper cache control headers
    log_info "Syncing frontend files to s3://$s3_bucket/"
    
    if aws s3 sync "../src/frontend/" "s3://$s3_bucket/" \
        --delete \
        --exclude "*.DS_Store" \
        --exclude "*.tmp" \
        --exclude "node_modules/*" \
        --exclude ".git/*" \
        --cache-control "text/html:no-cache,text/css:max-age=31536000,application/javascript:max-age=31536000,image/*:max-age=31536000"; then
        
        log_success "Frontend files uploaded successfully"
    else
        log_error "Failed to upload frontend files"
        exit 1
    fi
}

# Enhanced CloudFront cache invalidation
invalidate_cloudfront_cache() {
    log_info "Invalidating CloudFront cache..."
    
    # Get CloudFront distribution ID from stack outputs (more reliable)
    local distribution_id
    distribution_id=$(get_stack_output "CloudFrontDistributionId")
    
    if [[ -z "$distribution_id" ]]; then
        log_warning "CloudFront distribution ID not found in outputs, trying alternative method..."
        
        # Fallback method
        distribution_id=$(aws cloudfront list-distributions \
            --query "DistributionList.Items[?contains(Comment, '$STACK_NAME')].Id" \
            --output text | head -1)
    fi
    
    if [[ -z "$distribution_id" ]]; then
        log_warning "No CloudFront distribution found, skipping cache invalidation"
        return 0
    fi
    
    # Create invalidation
    local invalidation_id
    if invalidation_id=$(aws cloudfront create-invalidation \
        --distribution-id "$distribution_id" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text); then
        
        log_success "Cache invalidation initiated (ID: $invalidation_id)"
        log_info "Cache will be cleared within 1-3 minutes"
    else
        log_warning "Cache invalidation failed, but deployment continues"
        log_info "Try hard refresh (Ctrl+F5) to see updates"
    fi
}

# Test API endpoints
test_api() {
    log_info "Testing API endpoints..."
    
    local api_url
    api_url=$(get_stack_output "ApiGatewayUrl")
    
    if [[ -z "$api_url" ]]; then
        log_error "Could not retrieve API URL from stack outputs"
        exit 1
    fi
    
    echo ""
    echo "🧪 Health Check:"
    if curl -sf "$api_url/api/health" | python3 -m json.tool 2>/dev/null; then
        log_success "Health check passed"
    else
        log_warning "Health check failed or returned non-JSON response"
    fi
    
    echo ""
    echo "🧪 Properties Endpoint:"
    if curl -sf "$api_url/api/properties" | python3 -m json.tool 2>/dev/null; then
        log_success "Properties endpoint accessible"
    else
        log_warning "Properties endpoint failed or returned non-JSON response"
    fi
}

# Cleanup resources
cleanup_resources() {
    log_info "Cleaning up serverless resources..."
    
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"
        log_info "CloudFormation stack deletion initiated: $STACK_NAME"
        log_info "Resources will be removed in the background"
    else
        log_warning "Stack $STACK_NAME not found or already deleted"
    fi
}

# Show usage information
show_usage() {
    cat << 'EOF'
Usage: ./deploy-serverless-improved.sh [OPTIONS] COMMAND

COMMANDS:
  infrastructure    Deploy Lambda + API Gateway + DynamoDB + CloudFront
  code             Quick Lambda code update (seconds, not minutes)
  website          Upload static website to S3/CloudFront + cache invalidation
  cache            Invalidate CloudFront cache only
  all              Complete deployment (infrastructure + website + cache)
  test             Test API endpoints
  cleanup          Remove all AWS resources

OPTIONS:
  -s, --stack-name NAME     CloudFormation stack name (default: guhae-serverless)
  -r, --region REGION       AWS region (default: us-east-1)
  -e, --environment ENV     Environment (dev/staging/prod) (default: dev)
  -m, --email EMAIL         Notification email (default: admin@guhae.com)
  -h, --help               Show this help message

ENVIRONMENT VARIABLES:
  STACK_NAME               Override default stack name
  AWS_DEFAULT_REGION       Override default region
  ENVIRONMENT              Override default environment
  NOTIFICATION_EMAIL       Override default notification email

EXAMPLES:
  ./deploy-serverless-improved.sh all
  ./deploy-serverless-improved.sh -e prod -r us-west-2 infrastructure
  ENVIRONMENT=staging ./deploy-serverless-improved.sh website
  ./deploy-serverless-improved.sh --stack-name my-rental-app code

COST INFORMATION:
  Serverless Idle Cost: ~$0.50-2/month
  Traditional EC2: ~$9.11/month minimum

  Usage-based pricing:
  • 1,000 page views/month: ~$0.50
  • 10,000 page views/month: ~$2.00
  • 100,000 page views/month: ~$15.00

PREREQUISITES:
  • AWS CLI configured with valid credentials
  • Python 3.9+ installed
  • Required source files in ../src/
EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -s|--stack-name)
                STACK_NAME="$2"
                shift 2
                ;;
            -r|--region)
                REGION="$2"
                shift 2
                ;;
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -m|--email)
                NOTIFICATION_EMAIL="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            infrastructure|code|website|cache|all|test|cleanup)
                COMMAND="$1"
                shift
                ;;
            *)
                log_error "Unknown argument: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Main execution
main() {
    local COMMAND=""
    
    echo "🚀 Guhae Serverless Deployment Script v2.0"
    echo "💰 Ultra-low cost serverless architecture"
    echo ""
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate command
    if [[ -z "$COMMAND" ]]; then
        log_error "No command specified"
        show_usage
        exit 1
    fi
    
    # Run validations
    validate_prerequisites
    validate_parameters
    
    # Execute command
    case "$COMMAND" in
        infrastructure)
            deploy_serverless_infrastructure
            ;;
        code)
            log_info "Quick code update..."
            package_lambda
            update_lambda_function
            log_success "Code updated in seconds!"
            ;;
        website)
            upload_static_files
            invalidate_cloudfront_cache
            ;;
        cache)
            invalidate_cloudfront_cache
            ;;
        all)
            deploy_serverless_infrastructure
            echo ""
            upload_static_files
            invalidate_cloudfront_cache
            
            local cloudfront_url
            cloudfront_url=$(get_stack_output "CloudFrontUrl")
            
            echo ""
            log_success "Complete deployment finished!"
            echo "🌐 Your app is live at: $cloudfront_url"
            log_info "CloudFront may take 5-10 minutes to fully deploy"
            ;;
        test)
            test_api
            ;;
        cleanup)
            cleanup_resources
            ;;
    esac
    
    # Cleanup deployment artifacts
    if [[ -f "lambda-deployment.zip" ]]; then
        rm -f "lambda-deployment.zip"
    fi
    
    log_success "Operation completed successfully!"
}

# Execute main function with all arguments
main "$@"