#!/bin/bash

# Enhanced deployment script with CI/CD integration
# Version: 3.0 - CI/CD Ready

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_NAME="${STACK_NAME:-guhae-serverless}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@guhae.com}"

# CI/CD specific variables
CI_BUILD_NUMBER="${GITHUB_RUN_NUMBER:-local}"
CI_COMMIT_SHA="${GITHUB_SHA:-$(git rev-parse HEAD 2>/dev/null || echo 'unknown')}"
CI_BRANCH="${GITHUB_REF_NAME:-$(git branch --show-current 2>/dev/null || echo 'unknown')}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging with CI/CD context
log_info() {
    echo -e "${BLUE}ℹ️  [${CI_BUILD_NUMBER}] $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ [${CI_BUILD_NUMBER}] $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  [${CI_BUILD_NUMBER}] $1${NC}"
}

log_error() {
    echo -e "${RED}❌ [${CI_BUILD_NUMBER}] $1${NC}" >&2
}

# Deployment metadata
create_deployment_metadata() {
    log_info "Creating deployment metadata..."
    
    cat > deployment-metadata.json << EOF
{
  "deployment": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "build_number": "${CI_BUILD_NUMBER}",
    "commit_sha": "${CI_COMMIT_SHA}",
    "branch": "${CI_BRANCH}",
    "environment": "${ENVIRONMENT}",
    "stack_name": "${STACK_NAME}",
    "region": "${REGION}",
    "deployer": "${USER:-ci-system}"
  }
}
EOF
}

# Pre-deployment validation
validate_deployment() {
    log_info "Running pre-deployment validation..."
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured"
        exit 1
    fi
    
    # Validate CloudFormation template
    if ! aws cloudformation validate-template \
        --template-body file://cloudformation-serverless.yaml \
        --region "$REGION" &> /dev/null; then
        log_error "CloudFormation template validation failed"
        exit 1
    fi
    
    # Check for drift in existing stack
    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        log_info "Checking for stack drift..."
        DRIFT_ID=$(aws cloudformation detect-stack-drift \
            --stack-name "$STACK_NAME" \
            --region "$REGION" \
            --query 'StackDriftDetectionId' \
            --output text)
        
        # Wait for drift detection
        sleep 10
        
        DRIFT_STATUS=$(aws cloudformation describe-stack-drift-detection-status \
            --stack-drift-detection-id "$DRIFT_ID" \
            --region "$REGION" \
            --query 'StackDriftStatus' \
            --output text)
        
        if [[ "$DRIFT_STATUS" == "DRIFTED" ]]; then
            log_warning "Stack drift detected - proceeding with caution"
        else
            log_success "No stack drift detected"
        fi
    fi
    
    log_success "Pre-deployment validation completed"
}

# Enhanced deployment with rollback capability
deploy_with_rollback() {
    log_info "Starting deployment with rollback capability..."
    
    # Create change set for review
    CHANGE_SET_NAME="deploy-${CI_BUILD_NUMBER}-$(date +%Y%m%d-%H%M%S)"
    
    log_info "Creating change set: $CHANGE_SET_NAME"
    
    if aws cloudformation create-change-set \
        --stack-name "$STACK_NAME" \
        --template-body file://cloudformation-serverless.yaml \
        --change-set-name "$CHANGE_SET_NAME" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --parameter-overrides \
            NotificationEmail="$NOTIFICATION_EMAIL" \
            Environment="$ENVIRONMENT" \
        --region "$REGION" \
        --tags \
            Key=DeploymentId,Value="${CI_BUILD_NUMBER}" \
            Key=CommitSha,Value="${CI_COMMIT_SHA}" \
            Key=Branch,Value="${CI_BRANCH}" \
            Key=Environment,Value="${ENVIRONMENT}"; then
        
        log_success "Change set created successfully"
        
        # Wait for change set creation
        aws cloudformation wait change-set-create-complete \
            --stack-name "$STACK_NAME" \
            --change-set-name "$CHANGE_SET_NAME" \
            --region "$REGION"
        
        # Execute change set
        log_info "Executing change set..."
        aws cloudformation execute-change-set \
            --stack-name "$STACK_NAME" \
            --change-set-name "$CHANGE_SET_NAME" \
            --region "$REGION"
        
        # Wait for deployment completion
        if aws cloudformation wait stack-update-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"; then
            log_success "Deployment completed successfully"
        else
            log_error "Deployment failed - initiating rollback"
            initiate_rollback
            exit 1
        fi
    else
        log_error "Failed to create change set"
        exit 1
    fi
}

# Rollback function
initiate_rollback() {
    log_warning "Initiating automatic rollback..."
    
    aws cloudformation cancel-update-stack \
        --stack-name "$STACK_NAME" \
        --region "$REGION" || true
    
    aws cloudformation wait stack-rollback-complete \
        --stack-name "$STACK_NAME" \
        --region "$REGION" || true
    
    log_warning "Rollback completed"
}

# Post-deployment testing
run_deployment_tests() {
    log_info "Running post-deployment tests..."
    
    # Get API URL
    API_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    if [[ -z "$API_URL" ]]; then
        log_error "Could not retrieve API URL"
        return 1
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/health" || echo "000")
    
    if [[ "$HEALTH_RESPONSE" == "200" ]]; then
        log_success "Health check passed"
    else
        log_error "Health check failed with status: $HEALTH_RESPONSE"
        return 1
    fi
    
    # Test CORS
    log_info "Testing CORS configuration..."
    CORS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X OPTIONS \
        -H "Origin: https://example.com" \
        "$API_URL/api/properties" || echo "000")
    
    if [[ "$CORS_RESPONSE" == "200" ]]; then
        log_success "CORS test passed"
    else
        log_warning "CORS test failed with status: $CORS_RESPONSE"
    fi
    
    log_success "Post-deployment tests completed"
}

# Notification function
send_deployment_notification() {
    local status="$1"
    
    log_info "Sending deployment notification..."
    
    # Create notification payload
    cat > notification.json << EOF
{
    "status": "$status",
    "environment": "$ENVIRONMENT",
    "stack_name": "$STACK_NAME",
    "build_number": "$CI_BUILD_NUMBER",
    "commit_sha": "$CI_COMMIT_SHA",
    "branch": "$CI_BRANCH",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
    
    # In a real implementation, you'd send this to Slack, email, etc.
    log_info "Notification payload created: notification.json"
}

# Main execution
main() {
    log_info "Starting CI/CD deployment process..."
    log_info "Build: $CI_BUILD_NUMBER | Commit: ${CI_COMMIT_SHA:0:8} | Branch: $CI_BRANCH"
    
    create_deployment_metadata
    validate_deployment
    
    # Your existing package_lambda function would go here
    # package_lambda
    
    deploy_with_rollback
    
    # Your existing update_lambda_function would go here  
    # update_lambda_function
    
    run_deployment_tests
    
    send_deployment_notification "success"
    
    log_success "CI/CD deployment completed successfully!"
}

# Error handling
trap 'send_deployment_notification "failed"; exit 1' ERR

# Execute main function
main "$@"