#!/bin/bash

# Cleanup AWS CodePipeline resources
# Use with caution - this will delete the entire CI/CD pipeline

set -euo pipefail

# Configuration
STACK_NAME="${CODEPIPELINE_STACK_NAME:-guhae-codepipeline}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
FORCE="${FORCE:-false}"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

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

# Confirm destructive action
confirm_cleanup() {
    if [[ "$FORCE" != "true" ]]; then
        echo
        log_warning "This will permanently delete the CodePipeline and all associated resources!"
        echo
        echo "Resources to be deleted:"
        echo "  • CodePipeline: $STACK_NAME"
        echo "  • CodeBuild project"
        echo "  • S3 artifact bucket"
        echo "  • IAM roles and policies"
        echo "  • SNS topic and subscriptions"
        echo
        read -p "Are you sure you want to continue? (type 'yes' to confirm): " CONFIRM
        if [[ "$CONFIRM" != "yes" ]]; then
            log_info "Cleanup cancelled"
            exit 0
        fi
    fi
}

# Stop any running pipeline executions
stop_pipeline_executions() {
    log_info "Stopping any running pipeline executions..."

    # Get running executions
    RUNNING_EXECUTIONS=$(aws codepipeline list-pipeline-executions \
        --pipeline-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'pipelineExecutionSummaries[?status==`InProgress`].pipelineExecutionId' \
        --output text)

    if [[ -n "$RUNNING_EXECUTIONS" && "$RUNNING_EXECUTIONS" != "None" ]]; then
        for EXECUTION_ID in $RUNNING_EXECUTIONS; do
            log_info "Stopping execution: $EXECUTION_ID"
            aws codepipeline stop-pipeline-execution \
                --pipeline-name "$STACK_NAME" \
                --pipeline-execution-id "$EXECUTION_ID" \
                --region "$REGION" \
                --abandon || true
        done
        log_success "Pipeline executions stopped"
    else
        log_info "No running pipeline executions found"
    fi
}

# Delete CloudFormation stack
delete_pipeline_stack() {
    log_info "Deleting CodePipeline CloudFormation stack..."

    if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &> /dev/null; then
        aws cloudformation delete-stack \
            --stack-name "$STACK_NAME" \
            --region "$REGION"

        log_info "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete \
            --stack-name "$STACK_NAME" \
            --region "$REGION"

        log_success "CodePipeline stack deleted"
    else
        log_warning "Stack $STACK_NAME not found"
    fi
}

# Clean up S3 artifacts (optional)
cleanup_artifacts() {
    if [[ "$FORCE" == "true" ]]; then
        log_info "Cleaning up S3 artifacts..."

        ARTIFACT_BUCKET="${STACK_NAME}-artifacts-$(aws sts get-caller-identity --query Account --output text)"

        if aws s3 ls "s3://$ARTIFACT_BUCKET" &> /dev/null; then
            aws s3 rm "s3://$ARTIFACT_BUCKET" --recursive
            aws s3 rb "s3://$ARTIFACT_BUCKET" || true
            log_success "Artifact bucket cleaned up"
        else
            log_info "Artifact bucket not found or already deleted"
        fi
    fi
}

# Clean up GitHub token (optional)
cleanup_github_token() {
    if [[ "$FORCE" == "true" ]]; then
        log_info "Removing GitHub token from Secrets Manager..."

        aws secretsmanager delete-secret \
            --secret-id guhae-github-token \
            --region "$REGION" \
            --force-delete-without-recovery || true

        log_success "GitHub token removed"
    fi
}

# Show usage
show_usage() {
    cat << EOF
AWS CodePipeline Cleanup Script

USAGE:
    $0 [OPTIONS]

DESCRIPTION:
    Deletes the AWS CodePipeline and associated resources.
    Use with extreme caution - this action cannot be undone!

OPTIONS:
    -s, --stack-name NAME     CodePipeline stack name (default: guhae-codepipeline)
    -r, --region REGION       AWS region (default: us-east-1)
    -f, --force              Skip confirmation prompts
    --cleanup-artifacts      Also delete S3 artifact bucket
    --cleanup-token          Also delete GitHub token from Secrets Manager
    -h, --help               Show this help

EXAMPLES:
    # Interactive cleanup
    $0

    # Force cleanup everything
    $0 --force --cleanup-artifacts --cleanup-token

    # Custom stack
    $0 --stack-name my-pipeline

WARNING:
    This will permanently delete:
    • CodePipeline and all execution history
    • CodeBuild project and build history
    • IAM roles and policies
    • SNS topics and subscriptions
    • S3 artifact bucket (--cleanup-artifacts)
    • GitHub token (--cleanup-token)

EOF
}

# Parse arguments
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
        -f|--force)
            FORCE="true"
            shift
            ;;
        --cleanup-artifacts)
            CLEANUP_ARTIFACTS="true"
            shift
            ;;
        --cleanup-token)
            CLEANUP_TOKEN="true"
            shift
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
    log_warning "AWS CodePipeline Cleanup Utility"
    log_warning "Stack: $STACK_NAME | Region: $REGION"

    confirm_cleanup
    stop_pipeline_executions
    delete_pipeline_stack

    if [[ "${CLEANUP_ARTIFACTS:-false}" == "true" ]]; then
        cleanup_artifacts
    fi

    if [[ "${CLEANUP_TOKEN:-false}" == "true" ]]; then
        cleanup_github_token
    fi

    log_success "CodePipeline cleanup completed!"
    echo
    log_info "Note: Your application environments (dev/prod) are still running."
    log_info "Use your deployment scripts if you need to modify or delete them."
}

# Execute main function
main "$@"