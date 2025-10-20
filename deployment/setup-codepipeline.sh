#!/bin/bash

# AWS CodePipeline Deployment Script for Guhae Rental Property App
# Sets up complete CI/CD pipeline from GitHub to production

set -euo pipefail

# Configuration
STACK_NAME="${CODEPIPELINE_STACK_NAME:-guhae-codepipeline}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
GITHUB_OWNER="${GITHUB_OWNER:-vishwasvr}"
GITHUB_REPO="${GITHUB_REPO:-guhae-rental-property-app}"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
NOTIFICATION_EMAIL="${NOTIFICATION_EMAIL:-admin@guhae.com}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

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

# Validate prerequisites
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

    # Check if CodeStar Connection exists
    if [[ -z "${CODESTAR_CONNECTION_ARN:-}" ]]; then
        log_warning "CodeStar Connection ARN not provided"
        log_info "You'll need to create a CodeStar Connection for GitHub after running this script"
        CODESTAR_CONNECTION_MISSING=true
    else
        CODESTAR_CONNECTION_MISSING=false
    fi

    log_success "Prerequisites validated"
}

# Create AWS CodeStar Connection for GitHub
create_codestar_connection() {
    log_info "Setting up AWS CodeStar Connection for GitHub..."

    echo "You'll need to create a CodeStar Connection to connect AWS to your GitHub repository."
    echo "This is FREE and replaces the need for Secrets Manager."
    echo ""
    echo "Follow these steps:"
    echo "1. Run this command to create the connection:"
    echo "   aws codestar-connections create-connection \\"
    echo "     --provider-type GitHub \\"
    echo "     --connection-name guhae-github-connection \\"
    echo "     --region $REGION"
    echo ""
    echo "2. After creating, copy the ConnectionArn from the output"
    echo "3. Go to the AWS Console: https://console.aws.amazon.com/codesuite/settings/connections"
    echo "4. Find your connection and click 'Update pending connection'"
    echo "5. Authorize AWS to access your GitHub account"
    echo "6. Set CODESTAR_CONNECTION_ARN environment variable and re-run this script:"
    echo "   export CODESTAR_CONNECTION_ARN='arn:aws:codestar-connections:...'"
    echo "   ./setup-codepipeline.sh"
    echo ""
    read -p "Press Enter after you've created and authorized the connection..."
}

# Deploy CodePipeline
deploy_codepipeline() {
    log_info "Deploying AWS CodePipeline..."

    # Check if CodeStar Connection ARN is provided
    if [[ -z "${CODESTAR_CONNECTION_ARN:-}" ]]; then
        log_error "CODESTAR_CONNECTION_ARN environment variable is required"
        log_info "Please create a CodeStar Connection first and set the ARN"
        exit 1
    fi

    # Deploy CloudFormation stack
    aws cloudformation deploy \
        --template-file codepipeline.yaml \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --parameter-overrides \
            GitHubOwner="$GITHUB_OWNER" \
            GitHubRepo="$GITHUB_REPO" \
            GitHubBranch="$GITHUB_BRANCH" \
            CodeStarConnectionArn="$CODESTAR_CONNECTION_ARN" \
            NotificationEmail="$NOTIFICATION_EMAIL" \
        --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
        --no-fail-on-empty-changeset

    log_success "CodePipeline deployed successfully"
}

# Get pipeline information
get_pipeline_info() {
    log_info "Retrieving CodePipeline information..."

    # Get stack outputs
    PIPELINE_NAME=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineName`].OutputValue' \
        --output text)

    PIPELINE_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`PipelineUrl`].OutputValue' \
        --output text)

    ARTIFACT_BUCKET=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ArtifactBucket`].OutputValue' \
        --output text)

    echo
    log_success "CodePipeline Setup Complete!"
    echo
    echo "📋 Pipeline Information:"
    echo "   🏗️  Pipeline Name: $PIPELINE_NAME"
    echo "   🌐 Pipeline URL: $PIPELINE_URL"
    echo "   📦 Artifact Bucket: $ARTIFACT_BUCKET"
    echo "   📧 Notifications: $NOTIFICATION_EMAIL"
    echo
    echo "🔄 Pipeline Stages:"
    echo "   1. Source: GitHub ($GITHUB_OWNER/$GITHUB_REPO)"
    echo "   2. Test: CodeBuild (linting, testing, packaging)"
    echo "   3. DeployToDev: Deploy to development environment"
    echo "   4. ManualApproval: Wait for approval to production"
    echo "   5. DeployToProd: Deploy to production environment"
    echo
    echo "🚀 How it works:"
    echo "   • Push to GitHub → Automatic dev deployment"
    echo "   • Manual approval → Production deployment"
    echo "   • All deployments use your existing scripts"
}

# Show usage
show_usage() {
    cat << EOF
AWS CodePipeline Setup for Guhae Rental Property App

USAGE:
    $0 [OPTIONS]

DESCRIPTION:
    Sets up a complete AWS CodePipeline for CI/CD from GitHub to production.
    The pipeline includes testing, development deployment, manual approval,
    and production deployment.

OPTIONS:
    -s, --stack-name NAME     CodePipeline stack name (default: guhae-codepipeline)
    -r, --region REGION       AWS region (default: us-east-1)
    -o, --github-owner OWNER  GitHub repository owner (default: vishwasvr)
    -R, --github-repo REPO    GitHub repository name (default: guhae-rental-property-app)
    -b, --github-branch BRANCH GitHub branch (default: main)
    -e, --email EMAIL         Notification email (default: admin@guhae.com)
    -h, --help               Show this help message

ENVIRONMENT VARIABLES:
    CODEPIPELINE_STACK_NAME   Override default stack name
    AWS_DEFAULT_REGION        Override default region
    GITHUB_OWNER             Override GitHub owner
    GITHUB_REPO              Override GitHub repo
    GITHUB_BRANCH            Override GitHub branch
    NOTIFICATION_EMAIL       Override notification email

EXAMPLES:
    # Basic setup
    $0

    # Custom configuration
    $0 -o myorg -R my-repo -b develop -e admin@mycompany.com

    # Using environment variables
    GITHUB_OWNER=myorg GITHUB_REPO=my-app $0

PREREQUISITES:
    • AWS CLI configured with appropriate permissions
    • GitHub repository access
    • AWS CodeStar Connection for GitHub (will be guided through setup)

EOF
}

# Parse command line arguments
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
        -o|--github-owner)
            GITHUB_OWNER="$2"
            shift 2
            ;;
        -R|--github-repo)
            GITHUB_REPO="$2"
            shift 2
            ;;
        -b|--github-branch)
            GITHUB_BRANCH="$2"
            shift 2
            ;;
        -e|--email)
            NOTIFICATION_EMAIL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log_info "Starting AWS CodePipeline setup for Guhae Rental Property App"
    log_info "Configuration: $GITHUB_OWNER/$GITHUB_REPO ($GITHUB_BRANCH) → $REGION"

    validate_prerequisites

    if [[ "$CODESTAR_CONNECTION_MISSING" == "true" ]]; then
        create_codestar_connection
    fi

    deploy_codepipeline
    get_pipeline_info

    echo
    log_success "🎉 CodePipeline setup complete!"
    echo
    echo "Next steps:"
    echo "1. Push changes to GitHub to trigger the pipeline"
    echo "2. Monitor deployments at: $PIPELINE_URL"
    echo "3. Approve production deployments when ready"
    echo
    echo "Your existing deployment scripts are still available for:"
    echo "• Local development testing"
    echo "• Emergency manual deployments"
    echo "• Custom deployment scenarios"
}

# Execute main function
main "$@"