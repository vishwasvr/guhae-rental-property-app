# AWS CodePipeline Setup Guide

## Overview

This guide sets up AWS CodePipeline for automated CI/CD from GitHub to production, providing a robust enterprise-grade deployment pipeline while leveraging your existing proven deployment scripts.

## Architecture

```
GitHub → CodePipeline → CodeBuild → CloudFormation → Production
    ↓         ↓            ↓            ↓
 Source   Test/Build   Testing     Deploy Dev → Manual Approval → Deploy Prod
```

## Pipeline Stages

### 1. Source Stage

- **Trigger**: GitHub push to main branch
- **Action**: Download source code from GitHub
- **Artifact**: Source code package

### 2. Test Stage

- **Action**: CodeBuild project runs tests and builds
- **Tests**: Python linting, CloudFormation validation, security checks
- **Build**: Creates Lambda deployment package
- **Artifact**: Tested code + deployment package

### 3. Deploy to Development

- **Actions**:
  - Deploy CloudFormation stack (dev environment)
  - Update Lambda function code
  - Upload frontend files to S3
  - Invalidate CloudFront cache
- **Result**: Fully deployed dev environment

### 4. Manual Approval

- **Trigger**: Email notification to stakeholders
- **Action**: Manual approval required for production
- **Link**: Direct link to dev environment for testing

### 5. Deploy to Production

- **Actions**: Same as dev but with production configuration
- **Domain**: Deploys to www.guhae.com with SSL
- **Result**: Live production application

## Setup Instructions

### Prerequisites

1. **AWS CLI configured** with deployment permissions
2. **GitHub repository** with your code
3. **AWS CodeStar Connection** for GitHub access (free)

### Step 1: Deploy CodePipeline

```bash
cd deployment
chmod +x setup-codepipeline.sh
./setup-codepipeline.sh
```

The script will:

- Guide you through creating a CodeStar Connection for GitHub (free alternative to tokens)
- Deploy the CodePipeline CloudFormation stack
- Configure all necessary IAM roles and permissions

### Step 2: Configure GitHub (Optional)

The pipeline uses GitHub OAuth, but you can also configure webhooks for faster triggering:

1. Go to AWS CodePipeline console
2. Select your pipeline
3. Edit the Source stage
4. Enable webhooks for faster triggering

### Step 3: Test the Pipeline

```bash
# Push a small change to trigger the pipeline
git add .
git commit -m "Test CodePipeline deployment"
git push origin main
```

Monitor the pipeline execution in the AWS CodePipeline console.

## Configuration Options

### Environment Variables

```bash
# Override defaults
export CODEPIPELINE_STACK_NAME="my-app-pipeline"
export GITHUB_OWNER="myorg"
export GITHUB_REPO="my-app"
export GITHUB_BRANCH="develop"
export NOTIFICATION_EMAIL="devops@mycompany.com"
```

### Command Line Options

```bash
./setup-codepipeline.sh \
  --github-owner myorg \
  --github-repo my-app \
  --github-branch develop \
  --email devops@mycompany.com
```

## Security Features

### 🔐 Secure GitHub Integration

- AWS CodeStar Connections for secure, tokenless GitHub access
- OAuth-based authorization with granular permissions
- No sensitive credentials stored in AWS

### 🛡️ Least Privilege IAM

- Separate roles for CodePipeline, CodeBuild, and CloudFormation
- Minimal required permissions for each service

### ✅ Manual Approvals

- Production deployments require manual approval
- Email notifications sent to stakeholders
- Direct links to review dev environment

## Monitoring & Troubleshooting

### Pipeline Monitoring

```bash
# Check pipeline status
aws codepipeline get-pipeline-state --name guhae-codepipeline

# View pipeline execution history
aws codepipeline list-pipeline-executions --pipeline-name guhae-codepipeline
```

### Common Issues

#### Pipeline Fails at Source Stage

```bash
# Check GitHub token
aws secretsmanager get-secret-value --secret-id guhae-github-token

# Verify token permissions in GitHub
```

#### CloudFormation Deployment Fails

```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name guhae-serverless

# View detailed error
aws cloudformation describe-stacks --stack-name guhae-serverless
```

#### Lambda Update Fails

```bash
# Check Lambda function
aws lambda get-function --function-name guhae-serverless-rental-property-api-handler

# View CloudWatch logs
aws logs tail /aws/lambda/guhae-serverless-rental-property-api-handler --follow
```

## Cost Analysis

### Monthly Cost Estimate

| Service              | Cost      | Purpose                   |
| -------------------- | --------- | ------------------------- |
| CodePipeline         | $1.00     | Pipeline execution        |
| CodeBuild            | $0.50     | Build environment         |
| S3 (artifacts)       | $0.10     | Pipeline artifacts        |
| CodeStar Connections | $0.00     | GitHub integration (free) |
| **Total**            | **$1.60** | CI/CD infrastructure      |

_Costs based on typical usage; actual costs may vary_

## Comparison: CodePipeline vs GitHub Actions

| Feature              | AWS CodePipeline          | GitHub Actions               |
| -------------------- | ------------------------- | ---------------------------- |
| **AWS Integration**  | Native, seamless          | Requires OIDC setup          |
| **Cost**             | Predictable AWS pricing   | Free tier available          |
| **Setup Complexity** | Moderate (CloudFormation) | Simple (YAML files)          |
| **Cross-Account**    | Excellent                 | Requires additional setup    |
| **Approval Gates**   | Built-in manual approval  | Requires third-party actions |
| **Monitoring**       | AWS-native dashboards     | GitHub + third-party         |
| **Vendor Lock-in**   | AWS-only                  | GitHub ecosystem             |
| **Local Testing**    | Limited                   | Excellent                    |

## Best Use Cases

### Choose CodePipeline if you:

- Want deep AWS integration
- Need cross-account deployments
- Prefer AWS-native monitoring
- Have complex approval workflows
- Want predictable AWS pricing

### Choose GitHub Actions if you:

- Prefer simpler YAML configuration
- Want free tier for small projects
- Need extensive third-party integrations
- Prefer GitHub's ecosystem
- Want easier local testing

## Migration from Manual Deployments

Your existing deployment scripts remain fully functional and are used by the CodePipeline. The pipeline simply orchestrates their execution with additional testing and approval gates.

### What Changes

- ✅ Automated testing on every commit
- ✅ Consistent deployment process
- ✅ Production approval gates
- ✅ Comprehensive audit trail
- ✅ Email notifications

### What Stays the Same

- ✅ Your proven deployment scripts
- ✅ Environment separation (dev/prod)
- ✅ CloudFormation templates
- ✅ Manual deployment capability

## Emergency Procedures

If CodePipeline fails, you can still deploy manually:

```bash
# Deploy to development
cd deployment
./deploy-serverless.sh all

# Deploy to production
./deploy-custom-domain.sh -s guhae-prod -d www.guhae.com -c YOUR_CERT_ARN all
```

## Next Steps

1. **Deploy the pipeline** using the setup script
2. **Test with a small change** to verify functionality
3. **Configure monitoring** alerts for pipeline failures
4. **Set up team notifications** for approval requests
5. **Document approval procedures** for your team

The CodePipeline provides enterprise-grade CI/CD while preserving your battle-tested deployment scripts and processes.
