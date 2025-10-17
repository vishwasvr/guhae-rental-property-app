# Guhae - Serverless Rental Property Management

A modern, serverless rental property management application built on AWS Lambda with ultra-low costs.

## 🏗️ Architecture

**Serverless Stack:**

- **Lambda** - API backend (pay-per-request)
- **API Gateway** - REST API endpoints
- **DynamoDB** - NoSQL database (pay-per-request)
- **S3** - Static website hosting & file storage
- **CloudFront** - Global CDN

## 💰 Cost Structure

- **Idle Cost**: ~$0.50/month
- **1,000 users/month**: ~$2/month
- **10,000 users/month**: ~$8/month
- **100,000 users/month**: ~$35/month

## 🚀 Quick Deployment

```bash
cd deployment
# With dedicated IAM user (recommended)
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all

# Or with default AWS credentials
./deploy-serverless.sh all
```

Your app will be live at a CloudFront URL in minutes!

## 📋 Features

- ✅ Property listing and management
- ✅ Dashboard with statistics
- ✅ File upload for property images
- ✅ RESTful API endpoints
- ✅ Responsive Bootstrap UI
- ✅ Serverless architecture
- ✅ Auto-scaling and high availability

## 📁 Project Structure

```
guhae-rental-property-app/
├── README.md                              # Project documentation
├── requirements.txt                       # Python dependencies
├── .env                                   # Environment variables
├── .gitignore                            # Git ignore rules
├── deployment/
│   ├── cloudformation-serverless.yaml    # Complete infrastructure
│   └── deploy-serverless.sh             # Automated deployment
├── src/
│   ├── __init__.py
│   ├── config.py                         # Serverless configuration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py                   # DynamoDB operations
│   │   └── properties.py                 # Property business logic
│   ├── static/
│   │   ├── css/style.css                 # Bootstrap styling
│   │   └── js/app.js                     # Frontend JavaScript
│   ├── templates/                        # HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── properties.html
│   │   ├── property_detail.html
│   │   └── add_property.html
│   └── utils/
│       ├── __init__.py
│       ├── aws_helpers.py                # AWS utility functions
│       └── validators.py                 # Input validation
```

## 🛠️ Prerequisites

- AWS CLI installed and configured
- Python 3.8+ (for local development)
- Git (for version control)

## 🔐 AWS Security Setup (Recommended)

### Creating a Dedicated IAM User

For security best practices, create a dedicated IAM user for this application:

#### 1. Create IAM User

```bash
aws iam create-user --user-name guhae-deployment-user
```

#### 2. Create Custom Policy

Create a policy file with minimal required permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["cloudformation:*"],
      "Resource": "arn:aws:cloudformation:*:*:stack/guhae-serverless/*"
    },
    {
      "Effect": "Allow",
      "Action": ["lambda:*"],
      "Resource": "arn:aws:lambda:*:*:function:guhae-*"
    },
    {
      "Effect": "Allow",
      "Action": ["apigateway:*", "cloudfront:*"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": ["dynamodb:*"],
      "Resource": "arn:aws:dynamodb:*:*:table/guhae-*"
    },
    {
      "Effect": "Allow",
      "Action": ["s3:*"],
      "Resource": ["arn:aws:s3:::guhae-*", "arn:aws:s3:::guhae-*/*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:CreateRole",
        "iam:DeleteRole",
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
```

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
```

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

## Deployment Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/vishwasvr/guhae-rental-property-app.git
   cd guhae-rental-property-app
   ```

2. **Configure Git authentication** (for contributors)

   ```bash
   # Set up secure credential storage
   git config --global credential.helper osxkeychain  # macOS
   # git config --global credential.helper manager     # Windows
   # git config --global credential.helper store       # Linux
   ```

3. **Set up AWS IAM User** (recommended - see AWS Security Setup above)

4. **Deploy to AWS**

   ```bash
   cd deployment

   # Option 1: Using dedicated user profile (recommended)
   AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all

   # Option 2: Using default AWS credentials
   ./deploy-serverless.sh all
   ```

5. **Access your application**
   - API will be available at the provided API Gateway URL
   - Website will be available at the CloudFront URL

## 🧪 API Endpoints

- `GET /api/health` - Health check
- `GET /api/properties` - List all properties
- `POST /api/properties` - Create new property
- `GET /api/properties/{id}` - Get property details
- `PUT /api/properties/{id}` - Update property
- `DELETE /api/properties/{id}` - Delete property
- `GET /api/dashboard` - Dashboard statistics

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

## 🚨 Troubleshooting

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
