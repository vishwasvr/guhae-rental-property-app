# 🚀 Automated CI/CD Setup Guide

## Overview

This guide walks you through setting up automated production deployments with manual approval gates.

## Prerequisites

- ✅ Repository with quality check pipeline
- ✅ DNS and SSL certificates configured
- ✅ AWS account with deployment permissions
- ✅ GitHub repository access

## Step 1: Configure GitHub Environment Protection

### 1.1 Create Development Environment

1. Go to your GitHub repository
2. Click **Settings** tab
3. Scroll down and click **Environments** in the left sidebar
4. Click **New environment**
5. Enter environment name: `development`
6. Click **Configure environment**

**For Development Environment:**

- **Required Reviewers**: Leave unchecked (automatic deployment)
- **Deployment Branches**: Add branch `develop`
- **Environment URL**: Add your dev domain (e.g., `https://guhae-dev.example.com`)

### 1.2 Create Production Environment

7. Click **New environment**
8. Enter environment name: `production`
9. Click **Configure environment**

**For Production Environment (Single User):**

**Option A: No Required Reviewers (Recommended for solo development)**
- **Required Reviewers**: Leave unchecked (you can self-approve)
- **Deployment Branches**: Add branch `main`
- **Environment URL**: `https://www.guhae.com`

**Option B: Required Reviewers (For team collaboration)**
- **Required Reviewers**: Check and add team members
- **Deployment Branches**: Add branch `main`
- **Environment URL**: `https://www.guhae.com`

**Option C: Use Manual Trigger Only**
- Skip environment protection entirely
- Use `workflow_dispatch` to manually trigger deployments
- No approval required, full control

### 1.3 Save Configuration

Click **Save protection rules** to apply the settings.

## Step 2: Configure AWS Deployment Secrets

### 2.1 Create IAM User for Deployment

```bash
# Create IAM policy for deployment
aws iam create-policy \
  --policy-name GuhaeDeploymentPolicy \
  --policy-document file://deployment/guhae-deployment-policy.json

# Create IAM user
aws iam create-user --user-name guhae-deployment-user

# Attach policies
aws iam attach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess

aws iam attach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::YOUR-ACCOUNT-ID:policy/GuhaeDeploymentPolicy

# Create access keys
aws iam create-access-key --user-name guhae-deployment-user
```

### 2.2 Add Secrets to GitHub

1. Go to repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

```
Name: AWS_ACCESS_KEY_ID
Value: [Access key from step 2.1]

Name: AWS_SECRET_ACCESS_KEY
Value: [Secret key from step 2.1]
```

## Step 3: Test the Setup

### 3.1 Manual Workflow Trigger

1. Go to **Actions** tab
2. Select **Production Deployment** workflow
3. Click **Run workflow**
4. Select `production` environment
5. Click **Run workflow**

### 3.2 Verify Deployment

Check the workflow logs for:

- ✅ AWS credential validation
- ✅ SSL certificate detection
- ✅ CloudFormation deployment
- ✅ Lambda code update
- ✅ Website deployment
- ✅ Health checks

## Step 4: Approval Workflow

### For Future Deployments:

#### Development Environment (Automatic):

1. **Push code** to `develop` branch
2. **Quality checks** run automatically
3. **Dev deployment** runs automatically after checks pass
4. **Ready for testing** at dev URL

#### Production Environment (Manual Approval):

1. **Create PR** from `develop` to `main`
2. **Quality checks** run on PR
3. **Merge to main** after approval
4. **Manual approval** required for production deployment
5. **Production deployment** runs automatically after approval

### Approval Process:

1. Go to **Actions** tab
2. Find the **Production Deployment** workflow run
3. Click **Review deployments**
4. Select the production environment
5. Click **Approve and deploy**

## Single-User Deployment Options

### Scenario: You're the Only Developer

As a solo developer, you have three options for production deployments:

#### **Option 1: Self-Approval (Recommended)**
- Configure production environment **without required reviewers**
- Deployments to `main` will auto-deploy after quality checks pass
- You maintain control but skip the approval step

#### **Option 2: Manual Trigger Only (Most Control)**
- Use the **"Manual Production Deployment"** workflow
- Click **"Run workflow"** in GitHub Actions
- Type `"deploy"` to confirm deployment
- No environment protection or approvals needed
- Full manual control over production deployments

### Manual Production Deployment Workflow

For complete control as a solo developer:

1. **Push code** to `main` branch (quality checks run automatically)
2. **Go to Actions** tab in GitHub
3. **Select "Manual Production Deployment"** workflow
4. **Click "Run workflow"**
5. **Type "deploy"** in the confirmation field
6. **Click "Run workflow"** to start deployment

This approach gives you:
- ✅ No approval loops
- ✅ Complete deployment control
- ✅ Can deploy anytime after quality checks
- ✅ Works perfectly for solo development

### Recommended Setup for Solo Development

1. **Development**: Automatic deployment on `develop` branch
2. **Production**: Self-approval on `main` branch (no required reviewers)
3. **Manual Override**: Use workflow dispatch for emergency deployments

### Workflow for Solo Developer

```
develop branch ── Quality Checks ── ✅ Auto Deploy to Dev
     │
     └── Create PR ── Quality Checks ── Self Review ── Merge to Main
           │
main branch ── Quality Checks ── ✅ Auto Deploy to Prod (Self-Approved)
```

This gives you fast feedback in development while maintaining production safety.

## Troubleshooting

### Environment Not Protected

- Check that environment name matches exactly: `production`
- Verify protection rules are enabled

### AWS Credential Errors

- Confirm secrets are added to repository (not environment)
- Validate IAM user has required permissions
- Check AWS region configuration

### SSL Certificate Not Found

- Ensure certificate is in `us-east-1` region
- Verify domain name matches exactly: `www.guhae.com`
- Check certificate validation status

### Deployment Fails

- Review CloudFormation stack events
- Check Lambda function logs
- Validate API Gateway configuration

## Security Best Practices

- **Rotate AWS credentials** regularly
- **Use least-privilege IAM policies**
- **Enable MFA** for GitHub accounts
- **Monitor deployment logs** regularly
- **Set up billing alerts** for AWS costs

## Cost Considerations

- **GitHub Actions**: Free for public repos, $0.008/minute for private
- **AWS Lambda**: ~$0.50/month for basic usage
- **CloudFront**: Pay-per-GB transferred
- **DynamoDB**: Pay-per-request pricing

## Next Steps

1. ✅ Configure environment protection
2. ✅ Set up AWS credentials
3. ✅ Test automated deployment
4. 🔄 Add monitoring and alerts
5. 🔄 Set up rollback procedures

Your automated CI/CD pipeline is now ready! Deployments to production will require manual approval while maintaining full automation of the deployment process.
