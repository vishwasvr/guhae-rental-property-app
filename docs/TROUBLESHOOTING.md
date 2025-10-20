# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 🚀 Deployment Issues

#### "Stack already exists" Error

**Problem**: CloudFormation stack name conflict

```bash
An error occurred (AlreadyExistsException) when calling the CreateStack operation:
Stack [guhae-serverless] already exists
```

**Solution**: Update existing stack or use different name

```bash
# Option 1: Update existing stack
aws cloudformation update-stack --stack-name guhae-serverless \
  --template-body file://cloudformation-serverless.yaml

# Option 2: Delete and recreate
aws cloudformation delete-stack --stack-name guhae-serverless
```

#### IAM Permissions Denied

**Problem**: Insufficient AWS permissions

```bash
User: arn:aws:iam::123456789012:user/test-user is not authorized to perform:
cloudformation:CreateStack
```

**Solution**: Follow [Security Setup Guide](SECURITY.md) to create properly configured IAM user

#### Lambda Package Too Large

**Problem**: Deployment package exceeds size limit

```bash
An error occurred (InvalidParameterValueException): Unzipped size must be smaller than 262144000 bytes
```

**Solution**: Use optimized deployment process

```bash
# The deployment script now uses optimized 2KB packages
./deploy-serverless.sh code   # Fast code-only updates

# Avoid bundling AWS runtime libraries (boto3, etc.)
# Use AWS Lambda runtime dependencies instead
```

#### Deployment Hanging on Lambda Updates

**Problem**: Script appears to hang during Lambda function updates

```bash
📤 Uploading Lambda function code...
⏳ Waiting for function update to complete...
# (hangs here indefinitely)
```

**Solution**: The deployment script now includes proper wait logic and timeouts

```bash
# Use the updated deployment script with status checking
./deploy-serverless.sh code

# If still hanging, check function status manually:
aws lambda get-function --function-name FUNCTION_NAME --query 'Configuration.State'
```

### 🌐 API Issues

#### "Missing Authentication Token" Error

**Problem**: API returns authentication error on root path

```bash
curl https://YOUR-API-URL/
{"message":"Missing Authentication Token"}
```

**Solution**: Deploy infrastructure updates to activate root path routing

```bash
./deploy-serverless.sh infrastructure
# Root path (/) should now return welcome message
```

#### "Not Found" Response

**Problem**: API returns 404 for valid endpoints

```json
{ "message": "Not found" }
```

**Solutions**:

1. **Check URL structure**:

   ```bash
   # Correct format
   https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/api/properties

   # Incorrect (missing /api prefix)
   https://YOUR-API-ID.execute-api.us-east-1.amazonaws.com/prod/properties
   ```

2. **Verify Lambda function code**:
   ```bash
   # Update Lambda function
   cd deployment
   ./deploy-serverless.sh code
   ```

#### CORS Errors in Browser

**Problem**: Cross-origin requests blocked

```javascript
Access to fetch at 'API_URL' from origin 'https://example.com' has been blocked by CORS policy
```

**Solution**: Verify CORS headers in Lambda response

```python
# In lambda_function.py
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
}
```

#### Slow API Response Times

**Problem**: Lambda cold starts causing delays

**Solutions**:

1. **Use Lambda warming** (for production):

   ```bash
   # Schedule CloudWatch event to keep function warm
      aws events put-rule --name warm-lambda --schedule-expression "rate(5 minutes)"
   ```

### 🔧 Lambda Runtime Issues

#### Missing Environment Variables

**Problem**: Lambda function fails to start with validation error

```bash
ERROR: Missing required environment variables: DYNAMODB_TABLE_NAME, S3_BUCKET_NAME
ValueError: Missing required environment variables: DYNAMODB_TABLE_NAME, S3_BUCKET_NAME
```

**Solution**: Configure all required environment variables

**Required Variables:**

- `DYNAMODB_TABLE_NAME` - Your DynamoDB table name
- `S3_BUCKET_NAME` - Your S3 bucket name
- `COGNITO_USER_POOL_ID` - Your Cognito User Pool ID
- `COGNITO_CLIENT_ID` - Your Cognito Client ID

**Recommended Variables:**

- `AWS_REGION` - AWS region (default: us-east-1)
- `JWT_SECRET_KEY` - Secret key for JWT validation

**Configuration Steps:**

```bash
# Option 1: Update via AWS Console
# Lambda Console → Functions → Your Function → Configuration → Environment variables

# Option 2: Update via CloudFormation
aws cloudformation update-stack --stack-name your-stack \
  --template-body file://cloudformation-serverless.yaml \
  --parameters ParameterKey=TableName,ParameterValue=your-table-name

# Option 3: Update via AWS CLI
aws lambda update-function-configuration --function-name your-function \
  --environment Variables="{DYNAMODB_TABLE_NAME=your-table-name,S3_BUCKET_NAME=your-bucket}"
```

#### Environment Variable Validation Warnings

**Problem**: Lambda starts but shows warnings

```bash
WARNING: Missing recommended environment variables: AWS_REGION, JWT_SECRET_KEY
```

**Solution**: Add recommended variables for optimal operation (not required but suggested)

### 💾 Database Issues

````

2. **Optimize Lambda code**:
- Minimize package size
- Use connection pooling for DynamoDB
- Initialize resources outside handler function

### 💾 Database Issues

#### DynamoDB Access Denied

**Problem**: Lambda cannot access DynamoDB table

```json
{
"errorMessage": "User: arn:aws:sts::123:assumed-role/lambda-role is not authorized to perform: dynamodb:PutItem"
}
````

**Solution**: Verify IAM permissions in managed policy

```bash
# Check current policy
aws iam get-policy-version --policy-arn arn:aws:iam::ACCOUNT:policy/GuhaeMinimalPolicy --version-id v1

# Update managed policy if needed
aws iam create-policy-version --policy-arn arn:aws:iam::ACCOUNT:policy/GuhaeMinimalPolicy \
  --policy-document file://guhae-deployment-policy.json --set-as-default
```

#### Table Not Found

**Problem**: DynamoDB table doesn't exist

```json
{ "errorMessage": "Requested resource not found" }
```

**Solution**: Verify table creation and naming

```bash
# List tables
aws dynamodb list-tables --region us-east-1

# Check if table exists with correct name
aws dynamodb describe-table --table-name guhae-serverless-rental-properties
```

### 🌍 Static Website Issues

#### CloudFront Distribution Not Working

**Problem**: Website not accessible via CloudFront URL

**Solutions**:

1. **Wait for propagation** (can take 15-20 minutes)
2. **Check S3 bucket policy**:
   ```bash
   aws s3api get-bucket-policy --bucket guhae-serverless-assets-YOUR-ACCOUNT-ID
   ```
3. **Verify static files uploaded**:
   ```bash
   aws s3 ls s3://guhae-serverless-assets-YOUR-ACCOUNT-ID/
   ```

#### CSS/JavaScript Not Loading

**Problem**: Static assets return 403 Forbidden

**Solution**: Update S3 bucket policy for public read access

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::guhae-serverless-assets-YOUR-ACCOUNT-ID/*"
    }
  ]
}
```

### ⚡ Performance Issues

#### High Lambda Costs

**Problem**: Unexpected AWS charges

**Solutions**:

1. **Monitor invocations**:

   ```bash
   aws logs describe-log-groups --log-group-name-prefix /aws/lambda/guhae-serverless
   ```

2. **Set up billing alerts**:
   ```bash
   aws cloudwatch put-metric-alarm --alarm-name lambda-cost-alert \
     --alarm-description "Alert when Lambda costs exceed $10" \
     --metric-name EstimatedCharges --namespace AWS/Billing \
     --statistic Maximum --period 86400 --threshold 10 \
     --comparison-operator GreaterThanThreshold
   ```

#### DynamoDB Throttling

**Problem**: ReadCapacityUnits exceeded

```json
{ "errorMessage": "ProvisionedThroughputExceededException" }
```

**Solution**: Increase read/write capacity or use on-demand billing

```bash
aws dynamodb update-table --table-name guhae-serverless-rental-properties \
  --billing-mode PAY_PER_REQUEST
```

### 🔍 Debugging Tools

#### Check CloudFormation Stack Status

```bash
aws cloudformation describe-stacks --stack-name guhae-serverless \
  --query 'Stacks[0].StackStatus'
```

#### View Lambda Function Logs

```bash
# Get latest log stream
aws logs describe-log-streams \
  --log-group-name /aws/lambda/guhae-serverless-rental-property-api-handler \
  --order-by LastEventTime --descending --max-items 1

# View logs
aws logs get-log-events \
  --log-group-name /aws/lambda/guhae-serverless-rental-property-api-handler \
  --log-stream-name STREAM_NAME
```

#### Test API Endpoints Manually

```bash
# Test dashboard endpoint
curl -v https://YOUR-API-URL/api/dashboard

# Test with detailed output
curl -X GET https://YOUR-API-URL/api/properties \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\nTotal time: %{time_total}s\n"
```

#### Validate CloudFormation Template

```bash
aws cloudformation validate-template --template-body file://cloudformation-serverless.yaml
```

### 🆘 Emergency Recovery

#### Complete Stack Deletion

If deployment is completely broken:

```bash
# 1. Delete CloudFormation stack
aws cloudformation delete-stack --stack-name guhae-serverless

# 2. Wait for deletion to complete
aws cloudformation wait stack-delete-complete --stack-name guhae-serverless

# 3. Manually clean up any remaining resources
aws s3 rm s3://guhae-serverless-assets-YOUR-ACCOUNT-ID --recursive
aws s3 rb s3://guhae-serverless-assets-YOUR-ACCOUNT-ID

# 4. Redeploy from scratch
cd deployment
./deploy-serverless.sh all
```

#### Lambda Function Recovery

If only Lambda function is broken:

```bash
# Quick code update
cd deployment
./deploy-serverless.sh code

# Force update with new package
aws lambda update-function-code \
  --function-name guhae-serverless-rental-property-api-handler \
  --zip-file fileb://lambda-deployment.zip
```

### 📞 Getting Help

1. **Check AWS CloudWatch Logs** for detailed error messages
2. **Review CloudFormation Events** for deployment issues
3. **Validate API requests** using curl or Postman
4. **Monitor AWS Costs** in the billing dashboard
5. **Test locally** using the development server (see [Development Guide](DEVELOPMENT.md))

### 🔗 Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Step-by-step deployment instructions
- [Security Setup](SECURITY.md) - IAM user and policy configuration
- [API Reference](API.md) - Complete API documentation
- [Development Guide](DEVELOPMENT.md) - Local development setup
