#!/bin/bash

# Manual CodePipeline trigger script
# Useful for emergency deployments or testing

set -euo pipefail

# Configuration
PIPELINE_NAME="${PIPELINE_NAME:-guhae-codepipeline}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

# Colors
readonly BLUE='\033[0;34m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
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

# Get pipeline execution status
get_pipeline_status() {
    aws codepipeline get-pipeline-state \
        --name "$PIPELINE_NAME" \
        --region "$REGION" \
        --query 'stageStates[].{Stage: stageName, Status: latestExecution.status, Time: latestExecution.lastStatusChange}' \
        --output table
}

# Start pipeline execution
start_pipeline() {
    log_info "Starting CodePipeline execution..."

    EXECUTION_ID=$(aws codepipeline start-pipeline-execution \
        --name "$PIPELINE_NAME" \
        --region "$REGION" \
        --query 'pipelineExecutionId' \
        --output text)

    log_success "Pipeline execution started: $EXECUTION_ID"

    # Monitor execution
    monitor_execution "$EXECUTION_ID"
}

# Monitor pipeline execution
monitor_execution() {
    local execution_id="$1"
    local max_attempts=60  # 10 minutes max
    local attempt=0

    log_info "Monitoring pipeline execution..."

    while (( attempt < max_attempts )); do
        STATUS=$(aws codepipeline get-pipeline-execution \
            --pipeline-name "$PIPELINE_NAME" \
            --pipeline-execution-id "$execution_id" \
            --region "$REGION" \
            --query 'pipelineExecution.status' \
            --output text)

        case "$STATUS" in
            "InProgress")
                log_info "Pipeline execution in progress... (${attempt}/${max_attempts})"
                sleep 10
                ;;
            "Succeeded")
                log_success "Pipeline execution completed successfully!"
                return 0
                ;;
            "Failed")
                log_error "Pipeline execution failed!"
                # Get failure details
                aws codepipeline get-pipeline-execution \
                    --pipeline-name "$PIPELINE_NAME" \
                    --pipeline-execution-id "$execution_id" \
                    --region "$REGION" \
                    --query 'pipelineExecution.stageStates[?latestExecution.status==`Failed`].{Stage: stageName, Message: latestExecution.message}'
                return 1
                ;;
            "Stopped")
                log_warning "Pipeline execution was stopped"
                return 1
                ;;
            *)
                log_info "Pipeline status: $STATUS"
                sleep 10
                ;;
        esac

        ((attempt++))
    done

    log_warning "Monitoring timeout reached. Check AWS console for status."
}

# Stop pipeline execution
stop_pipeline() {
    log_info "Stopping latest pipeline execution..."

    # Get latest execution
    EXECUTION_ID=$(aws codepipeline list-pipeline-executions \
        --pipeline-name "$PIPELINE_NAME" \
        --region "$REGION" \
        --query 'pipelineExecutionSummaries[0].pipelineExecutionId' \
        --output text)

    if [[ -z "$EXECUTION_ID" || "$EXECUTION_ID" == "None" ]]; then
        log_warning "No active pipeline execution found"
        return 0
    fi

    aws codepipeline stop-pipeline-execution \
        --pipeline-name "$PIPELINE_NAME" \
        --pipeline-execution-id "$EXECUTION_ID" \
        --region "$REGION" \
        --abandon

    log_success "Pipeline execution stopped: $EXECUTION_ID"
}

# Show usage
show_usage() {
    cat << EOF
Manual CodePipeline Control Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    start      Start a new pipeline execution
    status     Show current pipeline status
    stop       Stop the latest pipeline execution
    monitor    Monitor a specific execution (requires execution ID)

OPTIONS:
    -p, --pipeline NAME     Pipeline name (default: guhae-codepipeline)
    -r, --region REGION     AWS region (default: us-east-1)
    -e, --execution-id ID   Execution ID for monitoring
    -h, --help             Show this help

EXAMPLES:
    # Start pipeline
    $0 start

    # Check status
    $0 status

    # Stop pipeline
    $0 stop

    # Monitor specific execution
    $0 monitor --execution-id abc123

    # Custom pipeline
    $0 start --pipeline my-pipeline --region us-west-2

EOF
}

# Parse arguments
COMMAND=""
EXECUTION_ID=""

while [[ $# -gt 0 ]]; do
    case $1 in
        start|status|stop|monitor)
            COMMAND="$1"
            shift
            ;;
        -p|--pipeline)
            PIPELINE_NAME="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -e|--execution-id)
            EXECUTION_ID="$2"
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

# Execute command
case "$COMMAND" in
    start)
        start_pipeline
        ;;
    status)
        get_pipeline_status
        ;;
    stop)
        stop_pipeline
        ;;
    monitor)
        if [[ -z "$EXECUTION_ID" ]]; then
            log_error "Execution ID required for monitoring. Use --execution-id"
            exit 1
        fi
        monitor_execution "$EXECUTION_ID"
        ;;
    "")
        log_error "No command specified"
        show_usage
        exit 1
        ;;
    *)
        log_error "Unknown command: $COMMAND"
        show_usage
        exit 1
        ;;
esac