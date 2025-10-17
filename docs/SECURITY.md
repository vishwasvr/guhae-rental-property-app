# 🔐 Security Setup Guide

## Overview

This guide covers setting up a dedicated IAM user with managed policies for secure Guhae deployment.

## Creating a Dedicated IAM User

### 1. Create IAM User

```bash
aws iam create-user --user-name guhae-deployment-user
```

### 2. Create Managed Policy (Recommended - 6KB limit)

Create the managed policy from our comprehensive permissions file:

```bash
cd deployment
aws iam create-policy \
  --policy-name GuhaeDeploymentPolicy \
  --policy-document file://guhae-minimal-policy.json \
  --description "Managed policy for Guhae rental property app deployment with least-privilege permissions"
```

### 3. Attach Managed Policy

```bash
aws iam attach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy
```

### 4. Create Access Keys

```bash
aws iam create-access-key --user-name guhae-deployment-user
```

### 5. Configure AWS Profile

```bash
aws configure --profile guhae-deployment
# Enter the access key ID and secret from step 4
# Region: us-east-1 (or your preferred region)
# Output format: json
```

## Policy Details

Our comprehensive policy (`guhae-minimal-policy.json`) includes:

- **S3 Operations**: Bucket management, object operations for `guhae-*` resources
- **DynamoDB Operations**: Table management for rental properties data
- **Lambda Operations**: Function creation, updates, and configuration
- **API Gateway Operations**: REST API management and deployment
- **CloudFormation Operations**: Stack management for infrastructure
- **CloudFront Operations**: CDN distribution management
- **IAM Operations**: Role management for Lambda execution

**All permissions are scoped to resources matching `guhae-*` pattern for maximum security.**

## Security Benefits

- ✅ **Principle of Least Privilege** - Only required permissions
- ✅ **Resource Scoping** - Limited to `guhae-*` resources
- ✅ **Audit Trail** - Separate user for application operations
- ✅ **Easy Revocation** - Delete user to revoke all access

## Policy Updates

If you need to update permissions later:

```bash
# Update the managed policy
aws iam create-policy-version \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy \
  --policy-document file://guhae-minimal-policy.json \
  --set-as-default
```

## Alternative: Minimal Update-Only Policy

For environments where you only need to update existing resources:

```bash
# Use the smaller update-only policy
aws iam create-policy \
  --policy-name GuhaeUpdateOnlyPolicy \
  --policy-document file://guhae-update-only-policy.json
```

## Cleanup

To remove the IAM user and policies:

```bash
# Detach policy
aws iam detach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy

# Delete access keys (list them first)
aws iam list-access-keys --user-name guhae-deployment-user
aws iam delete-access-key --user-name guhae-deployment-user --access-key-id ACCESS_KEY_ID

# Delete user
aws iam delete-user --user-name guhae-deployment-user

# Delete policy
aws iam delete-policy --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy
```
