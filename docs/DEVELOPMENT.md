# 🛠️ Development Guide

## Local Development Setup

### Prerequisites

- **Python 3.9+** (matches Lambda runtime)
- **pip** (Python package manager)
- **AWS CLI** configured with your credentials
- **Git** for version control

### Environment Setup

#### 1. Clone and Setup

```bash
git clone https://github.com/vishwasvr/guhae-rental-property-app.git
cd guhae-rental-property-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Environment Configuration

```bash
# Create .env file for local development
cat > .env << EOF
AWS_REGION=us-east-1
DYNAMODB_TABLE=guhae-serverless-rental-properties
S3_BUCKET=guhae-serverless-assets-YOUR-ACCOUNT-ID
LOCAL_DEVELOPMENT=true
EOF
```

#### 3. Local DynamoDB (Optional)

```bash
# Download and run DynamoDB Local
wget https://s3.us-west-2.amazonaws.com/dynamodb-local/dynamodb_local_latest.tar.gz
tar -xzf dynamodb_local_latest.tar.gz
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

# Create local table
aws dynamodb create-table \
  --table-name guhae-serverless-rental-properties \
  --attribute-definitions AttributeName=property_id,AttributeType=S \
  --key-schema AttributeName=property_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --endpoint-url http://localhost:8000
```

## Running Locally

### Development Server

```bash
# Navigate to source directory
cd src

# Run Flask development server
python -m flask --app lambda_function run --debug --port 5000

# Access local application
open http://localhost:5000
```

### Test Lambda Function Locally

```bash
# Test specific endpoints
python -c "
from lambda_function import lambda_handler
import json

# Test dashboard
event = {
    'httpMethod': 'GET',
    'path': '/api/dashboard',
    'headers': {},
    'body': None
}
context = {}
response = lambda_handler(event, context)
print(json.dumps(response, indent=2))
"
```

## Development Workflow

### 1. Code Changes

```bash
# Edit source files in src/
vim src/lambda_function.py
vim src/services/properties.py
vim src/templates/dashboard.html
```

### 2. Local Testing

```bash
# Test changes locally
cd src
python -m flask --app lambda_function run --debug

# Run unit tests (if available)
python -m pytest tests/
```

### 3. Deploy Changes

```bash
# Deploy only code changes
cd deployment
./deploy-serverless.sh code

# Deploy everything (infrastructure + code)
./deploy-serverless.sh all
```

## Project Structure

```
guhae-rental-property-app/
├── src/                          # Main application code
│   ├── lambda_function.py        # Main Lambda handler
│   ├── config.py                 # Configuration settings
│   ├── services/                 # Business logic
│   │   ├── database.py           # DynamoDB operations
│   │   └── properties.py         # Property management
│   ├── utils/                    # Utility functions
│   │   ├── aws_helpers.py        # AWS service helpers
│   │   └── validators.py         # Input validation
│   ├── templates/                # HTML templates
│   │   ├── base.html             # Base template
│   │   ├── dashboard.html        # Dashboard page
│   │   ├── properties.html       # Properties list
│   │   ├── property_detail.html  # Property details
│   │   └── add_property.html     # Add property form
│   └── static/                   # Static assets
│       ├── css/style.css         # Stylesheets
│       └── js/app.js             # JavaScript
├── deployment/                   # Deployment scripts
│   ├── cloudformation-serverless.yaml  # Infrastructure template
│   ├── deploy-serverless.sh      # Deployment script
│   └── guhae-deployment-policy.json # IAM permissions
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview
```

## Key Development Files

### Lambda Handler (`src/lambda_function.py`)

Main entry point for AWS Lambda:

```python
def lambda_handler(event, context):
    """Main Lambda handler for API Gateway events"""
    try:
        # Route handling logic
        if event['path'].startswith('/api/'):
            return handle_api_request(event)
        else:
            return handle_web_request(event)
    except Exception as e:
        return error_response(str(e), 500)
```

### Database Service (`src/services/database.py`)

DynamoDB operations:

```python
def get_properties():
    """Retrieve all properties from DynamoDB"""
    response = dynamodb.scan(TableName=TABLE_NAME)
    return response.get('Items', [])

def add_property(property_data):
    """Add new property to DynamoDB"""
    # Implementation here
```

### Property Management (`src/services/properties.py`)

Business logic for property operations:

```python
def create_property(title, address, rent, **kwargs):
    """Create new rental property"""
    # Validation and creation logic
```

## Testing

### Unit Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_properties.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Integration Tests

```bash
# Test against deployed API
cd deployment
./test-api.sh

# Manual API testing
curl -X GET "https://YOUR-API-URL/api/properties"
curl -X POST "https://YOUR-API-URL/api/properties" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Property","address":"123 Test St","rent":1000}'
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install httpie  # macOS

# Basic load test
ab -n 100 -c 10 https://YOUR-API-URL/api/dashboard

# More comprehensive testing with wrk
wrk -t12 -c400 -d30s https://YOUR-API-URL/api/properties
```

## Debugging

### Local Debugging

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run with debugger
python -m flask --app lambda_function run --debug

# Use Python debugger
import pdb; pdb.set_trace()
```

### Lambda Function Debugging

```bash
# View CloudWatch logs
aws logs tail /aws/lambda/guhae-serverless-rental-property-api-handler --follow

# Get specific log stream
aws logs describe-log-streams \
  --log-group-name /aws/lambda/guhae-serverless-rental-property-api-handler

# Download logs for analysis
aws logs filter-log-events \
  --log-group-name /aws/lambda/guhae-serverless-rental-property-api-handler \
  --start-time 1640995200000 > lambda-logs.json
```

### DynamoDB Debugging

```bash
# List all items in table
aws dynamodb scan --table-name guhae-serverless-rental-properties

# Get specific item
aws dynamodb get-item \
  --table-name guhae-serverless-rental-properties \
  --key '{"property_id":{"S":"your-property-id"}}'

# Query table with conditions
aws dynamodb query \
  --table-name guhae-serverless-rental-properties \
  --key-condition-expression "property_id = :id" \
  --expression-attribute-values '{":id":{"S":"your-property-id"}}'
```

## Performance Optimization

### Lambda Optimization

```python
# Initialize outside handler for reuse
import boto3
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    # Handler logic here
    pass
```

### DynamoDB Optimization

```python
# Use batch operations for multiple items
def batch_get_properties(property_ids):
    response = dynamodb.batch_get_item(
        RequestItems={
            TABLE_NAME: {
                'Keys': [{'property_id': {'S': pid}} for pid in property_ids]
            }
        }
    )
    return response['Responses'][TABLE_NAME]
```

### Caching

```python
# Simple in-memory caching
import time
cache = {}

def get_cached_data(key, fetch_function, ttl=300):
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < ttl:
            return data

    data = fetch_function()
    cache[key] = (data, time.time())
    return data
```

## Continuous Integration

### GitHub Actions (Example)

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/
      - name: Deploy to AWS
        run: |
          cd deployment
          ./deploy-serverless.sh all
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Best Practices

### Code Quality

- Use type hints for better code documentation
- Follow PEP 8 style guidelines
- Write comprehensive unit tests
- Use meaningful variable and function names
- Add docstrings to all functions and classes

### Security

- Never commit AWS credentials to version control
- Use environment variables for configuration
- Validate all user inputs
- Implement proper error handling
- Follow least-privilege principle for IAM policies

### Performance

- Minimize Lambda cold starts
- Use connection pooling for database connections
- Implement caching where appropriate
- Optimize DynamoDB queries
- Monitor and optimize costs regularly

## Useful Commands

```bash
# Package Lambda function for deployment
cd src && zip -r ../deployment/lambda-deployment.zip . -x "*.pyc" "__pycache__/*"

# Update only Lambda function code
aws lambda update-function-code \
  --function-name guhae-serverless-rental-property-api-handler \
  --zip-file fileb://lambda-deployment.zip

# Sync static files to S3
aws s3 sync src/static/ s3://guhae-serverless-assets-YOUR-ACCOUNT-ID/

# Watch CloudWatch logs in real-time
aws logs tail /aws/lambda/guhae-serverless-rental-property-api-handler --follow

# Create CloudFormation change set
aws cloudformation create-change-set \
  --stack-name guhae-serverless \
  --template-body file://cloudformation-serverless.yaml \
  --change-set-name update-$(date +%Y%m%d-%H%M%S)
```

## Related Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [API Reference](API.md) - Complete API documentation
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Security Setup](SECURITY.md) - IAM configuration
