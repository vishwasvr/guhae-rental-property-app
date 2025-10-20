#!/bin/bash

# Guhae Rental Property App - Custom Domain Deployment
# Extends the serverless deployment with custom domain support

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}" >&2; }

# Configuration
STACK_NAME="${STACK_NAME:-guhae-serverless}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Custom domain configuration
CUSTOM_DOMAIN=""
SSL_CERTIFICATE_ARN=""

# Help function
show_help() {
    cat << EOF
Guhae Rental Property App - Custom Domain Deployment

Usage: $0 [OPTIONS] COMMAND

COMMANDS:
  infrastructure    Deploy with custom domain
  website          Update website files
  all              Complete deployment with custom domain

OPTIONS:
  -d, --domain DOMAIN       Custom domain name (e.g., app.yourdomain.com)
  -c, --certificate ARN     SSL certificate ARN from ACM (us-east-1 region)
  -s, --stack-name NAME     CloudFormation stack name (default: guhae-serverless)
  -r, --region REGION       AWS region (default: us-east-1)
  -h, --help               Show this help message

EXAMPLES:
  # Deploy with custom domain
  $0 -d app.mycompany.com -c arn:aws:acm:us-east-1:123456789012:certificate/abc123 all
  
  # Update existing deployment with domain
  $0 -d rental.mydomain.com -c arn:aws:acm:us-east-1:123456789012:certificate/xyz789 infrastructure

NOTES:
  - SSL certificate must be in us-east-1 region for CloudFront
  - Domain must be validated and certificate issued before deployment
  - After deployment, update your DNS to point to CloudFront distribution

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            CUSTOM_DOMAIN="$2"
            shift 2
            ;;
        -c|--certificate)
            SSL_CERTIFICATE_ARN="$2"
            shift 2
            ;;
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            COMMAND="$1"
            shift
            ;;
    esac
done

# Validate command
if [[ -z "${COMMAND:-}" ]]; then
    log_error "No command specified"
    show_help
    exit 1
fi

# Validate custom domain parameters
if [[ -n "$CUSTOM_DOMAIN" && -z "$SSL_CERTIFICATE_ARN" ]]; then
    log_error "SSL certificate ARN required when using custom domain"
    exit 1
fi

if [[ -n "$SSL_CERTIFICATE_ARN" && -z "$CUSTOM_DOMAIN" ]]; then
    log_error "Custom domain required when providing SSL certificate"
    exit 1
fi

# Deploy infrastructure with custom domain
deploy_infrastructure() {
    log_info "Deploying serverless infrastructure with custom domain support..."
    
    # Build CloudFormation parameters
    PARAMETERS=(
        "ParameterKey=CustomDomain,ParameterValue=$CUSTOM_DOMAIN"
        "ParameterKey=SSLCertificateArn,ParameterValue=$SSL_CERTIFICATE_ARN"
    )
    
    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file cloudformation-serverless.yaml \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --parameter-overrides "${PARAMETERS[@]}" \
        --no-fail-on-empty-changeset
    
    log_success "Infrastructure deployed successfully"
    
    # Get outputs
    get_stack_outputs
}

# Get CloudFormation stack outputs
get_stack_outputs() {
    log_info "Retrieving deployment information..."
    
    # Get stack outputs
    OUTPUTS=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs' \
        --output json)
    
    API_URL=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="ApiGatewayUrl") | .OutputValue')
    CLOUDFRONT_URL=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="CloudFrontUrl") | .OutputValue')
    DISTRIBUTION_ID=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="CloudFrontDistributionId") | .OutputValue')
    S3_BUCKET=$(echo "$OUTPUTS" | jq -r '.[] | select(.OutputKey=="StorageBucketName") | .OutputValue')
    
    echo
    log_success "Deployment Information:"
    echo "   🏗️  Stack Name: $STACK_NAME"
    echo "   🌍 Region: $REGION"
    echo "   🔗 API URL: $API_URL"
    
    if [[ -n "$CUSTOM_DOMAIN" ]]; then
        echo "   🌐 Custom Domain: https://$CUSTOM_DOMAIN"
        echo "   📋 CloudFront Distribution: $DISTRIBUTION_ID"
        echo
        log_warning "DNS Configuration Required:"
        echo "   Create CNAME record: $CUSTOM_DOMAIN → $CLOUDFRONT_URL"
        echo "   Create CNAME record: www.$CUSTOM_DOMAIN → $CLOUDFRONT_URL"
    else
        echo "   🌐 Website URL: $CLOUDFRONT_URL"
    fi
    
    echo "   💾 S3 Bucket: $S3_BUCKET"
}

# Deploy website files
deploy_website() {
    log_info "Uploading frontend files to S3..."
    
    # Get S3 bucket name
    S3_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`StorageBucketName`].OutputValue' \
        --output text)
    
    # Sync frontend files
    aws s3 sync ../src/frontend/ "s3://$S3_BUCKET/" \
        --delete \
        --cache-control "public, max-age=31536000" \
        --exclude "*.html" \
        --exclude "*.json"
    
    # Upload HTML files with shorter cache
    aws s3 sync ../src/frontend/ "s3://$S3_BUCKET/" \
        --cache-control "public, max-age=300" \
        --include "*.html" \
        --include "*.json"
    
    log_success "Frontend files uploaded successfully"
    
    # Invalidate CloudFront cache
    DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
        --output text)
    
    log_info "Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" > /dev/null
    
    log_success "Cache invalidation initiated"
}

# Main execution
case "${COMMAND}" in
    infrastructure)
        deploy_infrastructure
        ;;
    website)
        deploy_website
        ;;
    all)
        deploy_infrastructure
        deploy_website
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

echo
log_success "Deployment completed successfully!"

if [[ -n "$CUSTOM_DOMAIN" ]]; then
    echo
    log_info "Next Steps:"
    echo "1. Configure DNS records as shown above"
    echo "2. Wait for DNS propagation (5-60 minutes)"
    echo "3. Test your custom domain: https://$CUSTOM_DOMAIN"
fi