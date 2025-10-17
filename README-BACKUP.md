# Guhae - Serverless Rental Property Management

A modern, serverless rental property management application built on AWS Lambda with enterprise-grade security and semantic naming conventions.

## � Live Demo

- **API Gateway**: https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod
- **CloudFront CDN**: https://d3qr4jcsohv892.cloudfront.net
- **Test Dashboard**: `curl https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/dashboard`

## �🏗️ Architecture

**Serverless Stack with Semantic Naming:**

- **RentalPropertyApiHandler** - Lambda function for API backend (pay-per-request)
- **RentalPropertyApiGateway** - REST API endpoints with proper routing
- **RentalPropertiesTable** - DynamoDB table for rental data (pay-per-request)
- **RentalPropertyAssetsBucket** - S3 bucket for static files & property assets
- **RentalPropertyWebDistribution** - CloudFront CDN for global delivery
- **RentalPropertyLambdaExecutionRole** - IAM role with least-privilege permissions

## 💰 Cost Structure

- **Idle Cost**: ~$0.50/month (90%+ reduction from EC2-based solutions)
- **1,000 users/month**: ~$2/month
- **10,000 users/month**: ~$8/month
- **100,000 users/month**: ~$35/month

_Compared to traditional EC2 deployment: $9.11/month baseline_

## 🚀 Quick Deployment

### Prerequisites

- AWS CLI configured
- Dedicated IAM user with managed policy (recommended)

```bash
cd deployment

# Method 1: With dedicated IAM user (RECOMMENDED - secure)
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all

# Method 2: With default AWS credentials (less secure)
./deploy-serverless.sh all
```

**Your app will be live in 3-5 minutes with semantic resource names!**

## 🛡️ Security Features

- ✅ **Managed IAM Policy**: 4.7KB policy with least-privilege permissions
- ✅ **Resource Scoping**: All permissions limited to "guhae-\*" resources
- ✅ **CORS Protection**: Proper cross-origin resource sharing
- ✅ **Semantic Naming**: Clear, professional resource identification
- ✅ **No Admin Access**: Dedicated deployment user without over-privileges

## 📋 Features

- ✅ Property listing and management with semantic API endpoints
- ✅ Dashboard with real-time statistics
- ✅ File upload for property images to dedicated assets bucket
- ✅ RESTful API with proper error handling
- ✅ Responsive Bootstrap UI with professional styling
- ✅ Serverless architecture with auto-scaling
- ✅ CloudFront global distribution
- ✅ Enterprise-grade security practices

## 📁 Project Structure

```
guhae-rental-property-app/
├── README.md                              # Project documentation
├── requirements.txt                       # Python dependencies
├── .env                                   # Environment variables
├── .env.example                          # Environment variables template
├── .gitignore                            # Git ignore rules
├── deployment/
│   ├── cloudformation-serverless.yaml    # Infrastructure with semantic naming
│   ├── deploy-serverless.sh             # Automated deployment script
│   ├── guhae-minimal-policy.json        # Comprehensive IAM permissions (4.7KB)
│   └── guhae-update-only-policy.json    # Minimal update permissions (for reference)
├── src/
│   ├── __init__.py
│   ├── config.py                         # Serverless configuration
│   ├── lambda_function.py               # Separated Lambda function code
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py                   # DynamoDB operations
│   │   └── properties.py                 # Property business logic
│   ├── static/
│   │   ├── css/style.css                 # Professional Bootstrap styling
│   │   └── js/app.js                     # Frontend JavaScript with API integration
│   ├── templates/                        # Responsive HTML templates
│   │   ├── base.html                     # Bootstrap 5 base template
│   │   ├── dashboard.html                # Real-time statistics dashboard
│   │   ├── properties.html               # Property listing with search
│   │   ├── property_detail.html          # Individual property view
│   │   └── add_property.html             # Property creation form
│   └── utils/
│       ├── __init__.py
│       ├── aws_helpers.py                # AWS utility functions
│       └── validators.py                 # Input validation
```

## 🛠️ Prerequisites

- **AWS CLI** installed and configured
- **Python 3.9+** (Lambda runtime compatible)
- **Git** (for version control and deployment)
- **AWS Account** with appropriate permissions
- **Dedicated IAM User** (recommended for security)

## 🔐 AWS Security Setup (Recommended)

### Creating a Dedicated IAM User with Managed Policy

For security best practices, create a dedicated IAM user with a managed policy for precise permissions:

#### 1. Create IAM User

```bash
aws iam create-user --user-name guhae-deployment-user
```

#### 2. Create Managed Policy (Recommended - 6KB limit)

Create the managed policy from our comprehensive permissions file:

```bash
cd deployment
aws iam create-policy \
  --policy-name GuhaeDeploymentPolicy \
  --policy-document file://guhae-minimal-policy.json \
  --description "Managed policy for Guhae rental property app deployment with least-privilege permissions"
```

#### 3. Attach Managed Policy

```bash
aws iam attach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy
```

#### 4. Create Access Keys

```bash
aws iam create-access-key --user-name guhae-deployment-user
```

#### 5. Configure AWS Profile

```bash
aws configure --profile guhae-deployment
# Enter the access key ID and secret from step 4
# Region: us-east-1 (or your preferred region)
# Output format: json
```

### 🏗️ What the Managed Policy Includes

Our comprehensive policy (`guhae-minimal-policy.json`) includes:

- **S3 Operations**: Bucket management, object operations for `guhae-*` resources
- **DynamoDB Operations**: Table management for rental properties data
- **Lambda Operations**: Function creation, updates, and configuration
- **API Gateway Operations**: REST API management and deployment
- **CloudFormation Operations**: Stack management for infrastructure
- **CloudFront Operations**: CDN distribution management
- **IAM Operations**: Role management for Lambda execution

**All permissions are scoped to resources matching `guhae-*` pattern for maximum security.**

### 🔄 Policy Updates

If you need to update permissions later:

```bash
# Update the managed policy
aws iam create-policy-version \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy \
  --policy-document file://guhae-minimal-policy.json \
  --set-as-default
```

        "iam:GetRole",
        "iam:PassRole",
        "iam:*RolePolicy"
      ],
      "Resource": "arn:aws:iam::*:role/guhae-*"
    },
    {
      "Effect": "Allow",
      "Action": ["logs:*"],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/guhae-*"
    }

]
}

````

#### 3. Create and Attach Policy

```bash
# Create policy from file
aws iam create-policy \
    --policy-name guhae-deployment-policy \
    --policy-document file://guhae-policy.json

# Attach policy to user
aws iam attach-user-policy \
    --user-name guhae-deployment-user \
    --policy-arn arn:aws:iam::YOUR-ACCOUNT-ID:policy/guhae-deployment-policy
````

#### 4. Generate Access Keys

```bash
aws iam create-access-key --user-name guhae-deployment-user
```

**Save the AccessKeyId and SecretAccessKey securely!**

#### 5. Configure AWS Profile

```bash
# Set up dedicated profile
aws configure set aws_access_key_id YOUR-ACCESS-KEY --profile guhae-deployment
aws configure set aws_secret_access_key YOUR-SECRET-KEY --profile guhae-deployment
aws configure set region us-east-1 --profile guhae-deployment

# Test the profile
aws sts get-caller-identity --profile guhae-deployment
```

### Security Benefits

- ✅ **Principle of Least Privilege** - Only required permissions
- ✅ **Resource Scoping** - Limited to `guhae-*` resources
- ✅ **Audit Trail** - Separate user for application operations
- ✅ **Easy Revocation** - Delete user to revoke all access

## 🚀 Deployment Process

### Step-by-Step Deployment

1. **Clone the repository**

   ```bash
   git clone https://github.com/vishwasvr/guhae-rental-property-app.git
   cd guhae-rental-property-app
   ```

2. **Set up AWS IAM User** (Complete the security setup above first)

3. **Deploy Infrastructure & Code**

   ```bash
   cd deployment

   # Method 1: Secure deployment with dedicated user (RECOMMENDED)
   AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all

   # Method 2: Using default AWS credentials (less secure)
   ./deploy-serverless.sh all
   ```

4. **Deployment Output**

   The script will deploy:

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

5. **Verify Deployment**

   Test your API endpoints:

   ```bash
   # Test dashboard
   curl https://YOUR-API-URL/api/dashboard

   # Test properties
   curl https://YOUR-API-URL/api/properties
   ```

### 🔧 Deployment Options

| **Component**           | **Command**                             | **Description**               |
| ----------------------- | --------------------------------------- | ----------------------------- |
| **Everything**          | `./deploy-serverless.sh all`            | Full deployment (recommended) |
| **Infrastructure Only** | `./deploy-serverless.sh infrastructure` | CloudFormation stack only     |
| **Code Update**         | `./deploy-serverless.sh code`           | Update Lambda function only   |
| **Website Only**        | `./deploy-serverless.sh website`        | Upload static files only      |

### 🛠️ What Gets Deployed

| **Resource Type** | **Resource Name**                              | **Purpose**                        |
| ----------------- | ---------------------------------------------- | ---------------------------------- |
| **Lambda**        | `guhae-serverless-rental-property-api-handler` | API backend with semantic naming   |
| **API Gateway**   | `guhae-serverless-rental-property-api`         | REST API endpoints                 |
| **DynamoDB**      | `guhae-serverless-rental-properties`           | Properties data storage            |
| **S3 Bucket**     | `guhae-serverless-assets-{AccountId}`          | Static files and property assets   |
| **CloudFront**    | Distribution with semantic domain              | Global CDN for fast delivery       |
| **IAM Role**      | `guhae-serverless-lambda-execution-role`       | Least-privilege Lambda permissions |

## 🧪 API Endpoints

**Live API Base URL**: `https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod`

| **Method** | **Endpoint**           | **Description**      | **Example**                                       |
| ---------- | ---------------------- | -------------------- | ------------------------------------------------- |
| `GET`      | `/api/dashboard`       | Dashboard statistics | `{"total_properties": 0, "active_properties": 0}` |
| `GET`      | `/api/properties`      | List all properties  | `{"properties": []}`                              |
| `POST`     | `/api/properties`      | Create new property  | Create rental property                            |
| `GET`      | `/api/properties/{id}` | Get property details | Individual property data                          |
| `PUT`      | `/api/properties/{id}` | Update property      | Modify property information                       |
| `DELETE`   | `/api/properties/{id}` | Delete property      | Remove property from system                       |

## 🔧 Local Development

1. **Set up virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials and settings
   ```

## 🏷️ Environment Variables

Create a `.env` file with:

```env
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=guhae-properties
S3_BUCKET_NAME=guhae-storage
NOTIFICATION_EMAIL=your-email@example.com
```

## 📊 Monitoring

- **CloudWatch Logs** - Lambda function logs
- **CloudWatch Metrics** - API Gateway and Lambda metrics
- **X-Ray Tracing** - Distributed tracing (optional)

## 🔒 Security

- IAM roles with least-privilege access
- API Gateway with CORS configuration
- CloudFront with HTTPS enforcement
- DynamoDB with encryption at rest

## 🎯 Recent Improvements & Architecture Decisions

### Semantic Resource Naming Convention

We've implemented enterprise-grade semantic naming for all AWS resources:

| **Before**            | **After**                           | **Benefit**                  |
| --------------------- | ----------------------------------- | ---------------------------- |
| `GuhaeApiFunction`    | `RentalPropertyApiHandler`          | Clear purpose identification |
| `GuhaeStorageBucket`  | `RentalPropertyAssetsBucket`        | Semantic bucket purpose      |
| `GuhaeDataTable`      | `RentalPropertiesTable`             | Explicit data structure      |
| `GuhaeServerlessRole` | `RentalPropertyLambdaExecutionRole` | Role responsibility clarity  |

### Security & Permission Management

- **Managed IAM Policy**: Upgraded from 2KB inline policy limitation to 6KB managed policy
- **Least-Privilege Access**: All permissions scoped to `guhae-*` resources only
- **Separated Concerns**: Lambda function code separated from CloudFormation template
- **Comprehensive Permissions**: 4.7KB policy covering all deployment scenarios

### Performance & Deployment Optimizations

- **Lambda Code Separation**: Moved from inline CloudFormation code to dedicated file
- **Deployment Options**: Full package (13MB, stable) vs lightweight (6KB, fast updates)
- **Error Handling**: Improved CORS configuration and API error responses
- **Path Corrections**: Fixed deployment script file path references

### Cost & Scalability Benefits

- **90%+ Cost Reduction**: From $9.11/month (EC2) to ~$0.50/month (serverless)
- **Pay-per-Request**: DynamoDB and Lambda pricing models
- **Global Distribution**: CloudFront CDN for worldwide performance
- **Auto-scaling**: Handle traffic spikes without manual intervention

### Development Experience Improvements

- **Comprehensive Documentation**: Detailed troubleshooting and deployment guides
- **Multiple Deployment Options**: Infrastructure-only, code-only, or full deployment
- **Local Development**: Clear setup instructions with environment management
- **Professional Structure**: Enterprise-ready codebase organization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Architecture Benefits

- **Serverless**: No server management required
- **Auto-scaling**: Handles traffic spikes automatically
- **Cost-effective**: Pay only for what you use
- **High availability**: Built on AWS managed services
- **Global**: CloudFront provides worldwide content delivery

## 🚨 Troubleshooting & Common Issues

### IAM Permission Issues

**Issue**: `AccessDeniedException` when running deployment

```
User is not authorized to perform: lambda:GetFunctionConfiguration
```

**Solution**: Use managed policy instead of inline policy

```bash
# Create managed policy (overcomes 2KB inline policy limit)
aws iam create-policy \
  --policy-name GuhaeDeploymentPolicy \
  --policy-document file://guhae-minimal-policy.json

# Attach to user
aws iam attach-user-policy \
  --user-name guhae-deployment-user \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GuhaeDeploymentPolicy
```

### Lambda Function Issues

**Issue**: API returns `{"error": "Not found"}` after deployment

**Solution**: Lambda function code not updated properly

```bash
# Check function status
aws lambda get-function-configuration \
  --function-name guhae-serverless-rental-property-api-handler \
  --region us-east-1

# Manual code update
cd deployment
aws lambda update-function-code \
  --function-name guhae-serverless-rental-property-api-handler \
  --zip-file fileb://lambda-deployment.zip
```

### Deployment Speed Issues

**Issue**: Lambda function updates taking 30+ minutes

**Causes & Solutions**:

- **Large Package (13MB)**: Full boto3 dependencies
  - _Solution_: Accept longer upload time for version stability
- **Network Speed**: Slow internet connection
  - _Solution_: Use lightweight package (see below)
- **AWS Processing**: Lambda extraction and validation
  - _Solution_: Normal AWS behavior for large packages

**Create Lightweight Package** (for development):

```bash
cd deployment
mkdir lambda-lightweight && cd lambda-lightweight
cp ../../src/lambda_function.py .
zip lambda-lightweight.zip lambda_function.py
# Upload this 6KB package instead of 13MB
```

### Policy Size Limitations

**Issue**: `Maximum policy size of 2048 bytes exceeded`

**Solution**: Use managed policies (6KB limit) instead of inline policies (2KB limit)

```bash
# Check policy size
wc -c deployment/guhae-minimal-policy.json

# If over 2KB, use managed policy approach (recommended)
```

### Resource Naming Issues

**Issue**: CloudFormation references fail after semantic naming changes

**Solution**: Ensure all resource references are updated

- Check `!Ref` statements in CloudFormation
- Verify deployment script variable names
- Update output keys in CloudFormation template

### Stack Update Issues

**Issue**: CloudFormation stack update fails

**Solution**: Check for resource dependencies

```bash
# Describe stack events to see specific error
aws cloudformation describe-stack-events \
  --stack-name guhae-serverless \
  --region us-east-1
```

## 📊 Monitoring

- **CloudWatch Logs** - Lambda function logs at `/aws/lambda/guhae-serverless-rental-property-api-handler`
- **CloudWatch Metrics** - API Gateway and Lambda metrics with semantic names
- **X-Ray Tracing** - Distributed tracing (optional)
- **Cost Explorer** - Monitor actual costs vs. projections

## 🔒 Security Best Practices

- ✅ **Managed IAM Policies**: Use managed policies for better permissions management
- ✅ **Resource Scoping**: All permissions limited to `guhae-*` resources
- ✅ **Least Privilege**: Only necessary permissions granted
- ✅ **API Gateway CORS**: Proper cross-origin configuration
- ✅ **CloudFront HTTPS**: SSL/TLS enforcement for all traffic
- ✅ **DynamoDB Encryption**: Encryption at rest enabled
- ✅ **Semantic Naming**: Clear resource identification for auditing

## 🚨 Legacy Troubleshooting

### Common Issues

1. **AWS CLI not configured**

   ```bash
   aws configure
   ```

2. **Permission denied on deployment script**

   ```bash
   chmod +x deployment/deploy-serverless.sh
   ```

3. **Stack already exists**

   ```bash
   aws cloudformation delete-stack --stack-name guhae-serverless --profile guhae-deployment
   # Wait for deletion, then redeploy
   ```

4. **IAM permission errors**

   ```bash
   # Check which user you're using
   aws sts get-caller-identity --profile guhae-deployment

   # Verify policy is attached
   aws iam list-attached-user-policies --user-name guhae-deployment-user
   ```

5. **Update IAM user access keys**

   ```bash
   # List existing keys
   aws iam list-access-keys --user-name guhae-deployment-user

   # Create new key
   aws iam create-access-key --user-name guhae-deployment-user

   # Delete old key (after updating profile)
   aws iam delete-access-key --user-name guhae-deployment-user --access-key-id OLD-KEY-ID
   ```

## 🗑️ Cleanup Commands

### Remove IAM User and Resources

```bash
# Detach policy
aws iam detach-user-policy \
    --user-name guhae-deployment-user \
    --policy-arn arn:aws:iam::YOUR-ACCOUNT:policy/guhae-deployment-policy

# Delete access keys
aws iam delete-access-key \
    --user-name guhae-deployment-user \
    --access-key-id YOUR-ACCESS-KEY

# Delete user
aws iam delete-user --user-name guhae-deployment-user

# Delete policy
aws iam delete-policy \
    --policy-arn arn:aws:iam::YOUR-ACCOUNT:policy/guhae-deployment-policy

# Remove AWS profile (careful - this affects the specific profile only)
# Method 1: Remove specific profile
aws configure --profile guhae-deployment set aws_access_key_id ""
aws configure --profile guhae-deployment set aws_secret_access_key ""

# Method 2: Manually edit ~/.aws/credentials to remove [guhae-deployment] section
```

## 🔐 Git Authentication & Token Management

### Initial Setup

This repository uses GitHub Personal Access Tokens for secure authentication:

1. **Create a Personal Access Token**

   - Go to: https://github.com/settings/tokens
   - Click "Generate new token" → "Generate new token (classic)"
   - Name: `Guhae Development` (or any descriptive name)
   - Scopes: Select `repo` (Full control of private repositories)
   - Click "Generate token" and **copy it immediately** (you won't see it again!)

2. **Configure Secure Credential Storage**

   ```bash
   # macOS (recommended)
   git config --global credential.helper osxkeychain

   # Windows
   git config --global credential.helper manager

   # Linux
   git config --global credential.helper store
   ```

3. **First Push/Pull**
   - Git will prompt for credentials:
     - **Username**: `vishwasvr`
     - **Password**: `your-personal-access-token`
   - Credentials will be stored securely for future use

### Updating Your Token

When your token expires or you need to update it:

1. **Generate a new token** (same process as above)

2. **Update stored credentials:**

   **macOS:**

   ```bash
   # Remove old credential from Keychain
   git config --global --unset credential.helper
   git config --global credential.helper osxkeychain

   # Or manually via Keychain Access app:
   # Applications > Utilities > Keychain Access
   # Search for "github.com" and delete the entry
   ```

   **Windows:**

   ```bash
   # Use Windows Credential Manager
   # Control Panel > Credential Manager > Windows Credentials
   # Find and remove GitHub entry
   ```

   **Linux:**

   ```bash
   # Remove stored credential file
   rm ~/.git-credentials
   ```

3. **Next git operation will prompt for new token**

### Security Best Practices

- ✅ **Never commit tokens** to your repository
- ✅ **Use credential helpers** instead of embedding tokens in URLs
- ✅ **Set token expiration** (30-90 days recommended)
- ✅ **Use minimal scopes** (only `repo` for this project)
- ✅ **Revoke unused tokens** regularly in GitHub settings
- ⚠️ **Avoid sharing tokens** via chat, email, or screenshots

### Troubleshooting Authentication

1. **"Authentication failed" error**

   ```bash
   # Check if credential helper is configured
   git config --global credential.helper

   # If not set, configure it:
   git config --global credential.helper osxkeychain  # macOS
   ```

2. **Token not working**

   - Verify token has `repo` scope
   - Check if token has expired in GitHub settings
   - Ensure you're using the token as password, not your GitHub password

3. **Still having issues?**

   ```bash
   # Test with explicit credentials (temporary)
   git clone https://username:token@github.com/vishwasvr/guhae-rental-property-app.git

   # Then fix credential helper setup
   ```

## �📞 Support

For support, please open an issue in the GitHub repository or contact the development team.

---

**Built with ❤️ using AWS Serverless Technologies**
