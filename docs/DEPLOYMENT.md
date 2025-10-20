# 🚀 Deployment Guide

## Overview

Complete guide for deploying the Guhae rental property management application with multi-environment support (development and production) and custom domain integration.

## Prerequisites

- **AWS CLI** installed and configured
- **Python 3.9+** (Lambda runtime compatible)
- **Git** (for version control and deployment)
- **AWS Account** with appropriate permissions
- **Dedicated IAM User** (see [Security Setup](SECURITY.md))
- **Domain ownership** (for production deployment with custom domain)

### Environment Variables Required

The application validates the following environment variables at startup:

**Required Variables:**

- `DYNAMODB_TABLE_NAME` - DynamoDB table identifier
- `S3_BUCKET_NAME` - S3 bucket for file storage
- `COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
- `COGNITO_CLIENT_ID` - AWS Cognito Client ID

**Recommended Variables:**

- `AWS_REGION` - AWS region (default: us-east-1)
- `JWT_SECRET_KEY` - Secret key for JWT token validation

> **⚠️ Deployment Note**: The Lambda function will fail to start if required environment variables are missing. Ensure these are properly configured in your CloudFormation template or Lambda environment settings.

## Environment Strategy

### 🧪 Development Environment (`guhae-serverless`)

- **Purpose**: Testing and development
- **URL**: AWS-generated CloudFront domain
- **Database**: Separate DynamoDB table for dev data
- **Deployment**: Quick iterations and testing

### 🚀 Production Environment (`guhae-prod`)

- **Purpose**: Live application for end users
- **URL**: Custom domain (www.guhae.com)
- **SSL**: AWS Certificate Manager with DNS validation
- **Database**: Separate production DynamoDB table

## Deployment Process

### Step 1: Clone Repository

```bash
git clone https://github.com/vishwasvr/guhae-rental-property-app.git
cd guhae-rental-property-app
```

### Step 2: Set up AWS IAM User

Complete the [Security Setup Guide](SECURITY.md) first.

### Step 3: Choose Deployment Environment

#### 🧪 Development Deployment

For testing and development:

```bash
cd deployment

# Deploy development environment
STACK_NAME="guhae-serverless" ./deploy-serverless.sh all
```

#### 🚀 Production Deployment with Custom Domain

For production with your custom domain:

##### 3a. Request SSL Certificate

```bash
# Request certificate for your domain
aws acm request-certificate \
  --domain-name "guhae.com" \
  --subject-alternative-names "www.guhae.com" \
  --validation-method DNS \
  --region us-east-1
```

##### 3b. Add DNS Validation Records

Add the CNAME records provided by AWS to your domain registrar's DNS settings.

##### 3c. Deploy Production Environment

```bash
# Deploy production with custom domain (after certificate is validated)
./deploy-custom-domain.sh \
  -s guhae-prod \
  -d www.guhae.com \
  -c arn:aws:acm:us-east-1:account:certificate/cert-id \
  all
```

##### 3d. Configure DNS for Your Domain

Add these DNS records to point your domain to the CloudFront distribution:

```
Type: CNAME
Name: www
Value: your-cloudfront-domain.cloudfront.net
```

### Step 4: Verify Deployment

The script will output:

- ✅ **Infrastructure**: CloudFormation stack with semantic resource names
- ✅ **Lambda Function**: Rental property API handler with proper code
- ✅ **Static Files**: Upload website assets to S3 bucket
- ✅ **Testing**: Automatic API endpoint validation

**Example Output:**

```bash
✅ Serverless infrastructure deployed!
📦 Lambda package created: lambda-deployment.zip
⬆️  Uploading Lambda function code...
🌐 API URL: https://abc123.execute-api.us-east-1.amazonaws.com/prod
🌍 Website URL: https://d1234567890.cloudfront.net
```

## Deployment Options

| **Component**           | **Command**                             | **Description**               |
| ----------------------- | --------------------------------------- | ----------------------------- |
| **Everything**          | `./deploy-serverless.sh all`            | Full deployment (recommended) |
| **Infrastructure Only** | `./deploy-serverless.sh infrastructure` | CloudFormation stack only     |
| **Code Update**         | `./deploy-serverless.sh code`           | Update Lambda function only   |
| **Website Only**        | `./deploy-serverless.sh website`        | Upload static files only      |

## What Gets Deployed

| **Resource Type** | **Resource Name**                              | **Purpose**                        |
| ----------------- | ---------------------------------------------- | ---------------------------------- |
| **Lambda**        | `guhae-serverless-rental-property-api-handler` | API backend with semantic naming   |
| **API Gateway**   | `guhae-serverless-rental-property-api`         | REST API endpoints                 |
| **DynamoDB**      | `guhae-serverless-rental-properties`           | Properties data storage            |
| **S3 Bucket**     | `guhae-serverless-assets-{AccountId}`          | Static files and property assets   |
| **CloudFront**    | Distribution with semantic domain              | Global CDN for fast delivery       |
| **IAM Role**      | `guhae-serverless-lambda-execution-role`       | Least-privilege Lambda permissions |

## Verification Steps

Test your API endpoints:

```bash
# Test root endpoint
curl https://YOUR-API-URL/

# Test health check
curl https://YOUR-API-URL/api/health

# Test dashboard
curl https://YOUR-API-URL/api/dashboard

# Test properties
curl https://YOUR-API-URL/api/properties

# Expected responses
{"message": "Welcome to Guhae Rental Property Management API", ...}
{"status": "healthy", "timestamp": "...", "services": {...}}
{"total_properties": 0, "active_properties": 0, "total_users": 1, "total_leases": 0}
{"properties": []}
```

## 🚀 Deployment Performance

### Package Optimization

- **Lambda Package Size**: ~2KB (vs 13MB before optimization)
- **Deployment Speed**: Seconds (vs minutes with large packages)
- **Architecture**: Leverages AWS Lambda runtime libraries (boto3 included)

### Quick Code Updates

```bash
# For rapid code-only deployments
./deploy-serverless.sh code
```

This skips infrastructure deployment and only updates Lambda function code, completing in ~10 seconds.

## Cost Monitoring

After deployment, monitor costs in AWS Cost Explorer:

- **Expected idle cost**: ~$0.50/month
- **DynamoDB**: Pay-per-request (very low for testing)
- **Lambda**: Pay-per-invocation (very low for testing)
- **CloudFront**: Pay-per-GB transferred

## Updating Existing Deployment

### Update Lambda Code Only

```bash
cd deployment
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh code
```

### Update Infrastructure Only

```bash
cd deployment
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh infrastructure
```

### Full Update

```bash
cd deployment
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all
```

## Cleanup

To completely remove the application:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name guhae-serverless --region us-east-1

# Empty and delete S3 bucket (if needed)
aws s3 rm s3://guhae-serverless-assets-YOUR-ACCOUNT-ID --recursive
aws s3 rb s3://guhae-serverless-assets-YOUR-ACCOUNT-ID
```

## Next Steps

After successful deployment:

1. Test all API endpoints (see [API Reference](API.md))
2. Upload static website files
3. Configure custom domain (optional)
4. Set up monitoring and alerts
5. Review [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues

## 🚀 Production Deployment Automation

### Overview

The application now includes automated CI/CD with manual approval for production deployments. This ensures code quality while maintaining control over production releases.

### CI/CD Pipeline Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Code Push     │ -> │ Quality Checks   │ -> │ Environment      │
│   (develop)     │    │ (Automated)      │    │ Deployment       │
└─────────────────┘    └──────────────────┘    └──────────────────┘
       │                                                │
       │                                                v
       │                                     ┌──────────────────┐
       │                                     │   Dev Deploy     │
       │                                     │   (Automatic)    │
       │                                     └──────────────────┘
       │                                                │
       └── Create PR ── Quality Checks ── Code Review ──┼── Merge to Main
                              │                          │
                              v                          v
                   ┌──────────────────┐    ┌──────────────────┐
                   │ Manual Approval  │ -> │ Prod Deploy      │
                   │ (Required)       │    │ (Approved)       │
                   └──────────────────┘    └──────────────────┘
```

### Pipeline Components

#### 1. Code Quality & Security (`quality-check.yml`)

- **Triggers**: Push to `main`/`develop`, Pull Requests to `main`
- **Checks**: Linting, security scanning, unit tests, integration tests
- **Coverage**: 80% minimum code coverage required
- **Validations**: Environment variables, CloudFormation templates, dependencies

#### 2. Development Deployment (`dev-deployment.yml`)

- **Triggers**: After quality checks pass on `develop` branch
- **Environment**: Development environment (automatic)
- **Steps**: Full infrastructure and code deployment
- **Validation**: Health checks and post-deployment testing

#### 3. Production Deployment (`production-deployment.yml`)

- **Triggers**: After quality checks pass on `main` + manual approval
- **Environment**: Protected production environment
- **Steps**: Infrastructure, Lambda code, website deployment
- **Validation**: Health checks and post-deployment testing

### Setting Up Automated Production Deployment

#### Step 1: Configure GitHub Environment Protection

1. Go to your repository settings
2. Navigate to **Environments** in the left sidebar
3. Click **New environment**
4. Name it `production`
5. Configure protection rules:

**Required Reviewers:**

- Add team members who must approve production deployments
- Set minimum number of approvals required

**Deployment Branches:**

- Allow deployments from: `main` branch only

**Environment URL:**

- Set to: `https://www.guhae.com`

#### Step 2: Configure AWS Secrets

Add the following secrets to your GitHub repository:

```
AWS_ACCESS_KEY_ID          # IAM user access key for deployment
AWS_SECRET_ACCESS_KEY      # IAM user secret key for deployment
```

**Important**: Use an IAM user with minimal required permissions (see [Security Setup](SECURITY.md)).

#### Step 3: SSL Certificate Setup

Ensure your SSL certificate is issued and validated in AWS Certificate Manager (us-east-1 region) for `www.guhae.com`.

### Deployment Process

#### Automatic Flow:

1. **Code Push**: Developer pushes code to `main` branch
2. **Quality Checks**: Pipeline runs all validations automatically
3. **Approval Required**: Deployment waits for manual approval
4. **Production Deploy**: Approved deployments run automatically

#### Manual Trigger:

You can also trigger production deployment manually:

1. Go to **Actions** tab in GitHub
2. Select **Production Deployment** workflow
3. Click **Run workflow**
4. Select environment and confirm

### Deployment Stages

#### Stage 1: Infrastructure Deployment

- Creates/updates CloudFormation stack
- Sets up DynamoDB, Cognito, S3, API Gateway, CloudFront
- Configures IAM roles and permissions

#### Stage 2: Lambda Code Deployment

- Packages Python Lambda function
- Updates function code in AWS
- Validates environment variables

#### Stage 3: Website Deployment

- Uploads static files to S3
- Invalidates CloudFront cache
- Updates website content

#### Stage 4: Validation & Health Checks

- Tests API endpoints (`/api/health`)
- Validates website accessibility
- Confirms all services are operational

### Rollback Strategy

If deployment fails:

1. **Automatic**: Pipeline stops and reports failure
2. **Manual Rollback**: Use CloudFormation to rollback or redeploy previous version
3. **Emergency**: Update DNS to point to backup environment

### Monitoring & Notifications

#### Health Monitoring:

- API health endpoint: `GET /api/health`
- Website availability checks
- CloudWatch metrics and logs

#### Notifications (Optional):

Add notification integrations:

- Slack notifications for deployment status
- Email alerts for failures
- Teams/Slack channels for approvals

### Security Considerations

#### Access Control:

- **Environment Protection**: Requires approval for production access
- **AWS Credentials**: Stored securely in GitHub secrets
- **IAM Permissions**: Least-privilege deployment user

#### Audit Trail:

- All deployments logged in GitHub Actions
- AWS CloudTrail tracks infrastructure changes
- Approval history maintained in GitHub

### Troubleshooting

#### Common Issues:

**Deployment Stuck on Approval:**

- Check environment protection rules
- Verify required reviewers are set
- Ensure approvers have repository access

**AWS Permission Errors:**

- Validate IAM user permissions
- Check AWS credentials in GitHub secrets
- Verify SSL certificate access

**Health Check Failures:**

- Wait for CloudFront propagation (5-30 minutes)
- Check API Gateway and Lambda logs
- Validate DNS configuration

### Cost Optimization

- **Lambda**: Pay-per-invocation (~$0.50/month idle)
- **CloudFront**: Pay-per-GB transferred
- **DynamoDB**: Pay-per-request pricing
- **API Gateway**: Pay-per-request

### Next Steps

1. Configure environment protection in GitHub
2. Set up AWS deployment credentials
3. Test the automated deployment
4. Add monitoring and notifications
5. Document emergency procedures
