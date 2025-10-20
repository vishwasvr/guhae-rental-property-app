# Guhae - Serverless Rental Property Management

A modern, serverless rental property management application built on AWS with enterprise-grade Cognito authentication and global CDN delivery.

<!-- CI/CD Pipeline Test - This comment triggers automated testing and deployment (after stack deletion) -->

## 🌐 Live Demo

**Frontend Application**: https://d3qr4jcsohv892.cloudfront.net

**Authentication System**: AWS Cognito User Pools

- **Register**: Create new account with email and password
- **Login**: Email-based authentication with JWT tokens
- **Security**: Password policies enforced (8+ characters, complexity requirements)

> **Demo User (for testing)**:
>
> - Email: `demo@example.com`
> - Password: `Demo123!`
>
> Or register a new account using the Register tab on the login page.

**API Endpoints:**

- **API Gateway**: https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod
- **Authentication**: `POST /api/auth/login` and `POST /api/auth/register`
- **Health Check**: `GET /api/health`
- **Dashboard API**: `GET /api/dashboard`

**Architecture:**

- **Frontend**: S3 + CloudFront CDN (global edge caching)
- **Backend**: Lambda + API Gateway (serverless)
- **Authentication**: AWS Cognito User Pools
- **Database**: DynamoDB (NoSQL, pay-per-request)

## 🏗️ Architecture

**S3-Hosted Frontend + Serverless Backend + Cognito Auth:**

- **RentalPropertyAssetsBucket** - S3 bucket for frontend hosting & property assets
- **RentalPropertyWebDistribution** - CloudFront CDN for global frontend delivery
- **RentalPropertyApiHandler** - Lambda function for API backend (2KB package)
- **RentalPropertyApiGateway** - REST API endpoints with /api/\* routing
- **RentalPropertiesTable** - DynamoDB table for rental data (pay-per-request)
- **CognitoUserPool** - User authentication and management
- **CognitoUserPoolClient** - Application client for authentication flows
- **RentalPropertyLambdaExecutionRole** - IAM role with least-privilege permissions

**Request Flow:**

1. `yourdomain.com/` → CloudFront → S3 (frontend files)
2. `yourdomain.com/api/*` → CloudFront → API Gateway → Lambda (backend)
3. Authentication → Cognito User Pools → JWT tokens

## 🔐 Authentication System

**AWS Cognito Integration:**

- **User Pool**: Centralized user management
- **Email-based Login**: Users authenticate with email addresses
- **JWT Tokens**: Access, ID, and refresh tokens for secure sessions
- **Password Policies**: Enforced complexity requirements
- **Email Verification**: Built-in verification workflow

**Frontend Integration:**

- **Registration Form**: New user signup with email/password
- **Login Form**: Existing user authentication
- **Token Storage**: Secure localStorage management
- **Session Management**: Automatic token refresh and logout

## 💰 Cost Structure

**Monthly Costs (Pay-per-use):**

- **Idle Cost**: ~$0.50-$2.00/month (90%+ reduction vs EC2)
- **1,000 page views**: ~$0.50/month
- **10,000 page views**: ~$2.00/month
- **100,000 page views**: ~$15.00/month
- **Cognito**: First 50,000 MAUs free, then $0.0055/MAU

**Breakdown:**

- **Lambda**: $0.0000166667/request + $0.0000000021/MB-ms
- **API Gateway**: $3.50/million requests
- **CloudFront**: $0.085/GB + $0.0075/10k requests
- **DynamoDB**: $0.25/million reads, $1.25/million writes
- **S3**: $0.023/GB storage + $0.0004/1k requests

_Compared to traditional EC2 deployment: $9.11/month baseline + compute costs_

## � API Authentication

**Register New User:**

```bash
curl -X POST https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePass123!",
    "email": "user@example.com"
  }'
```

**User Login:**

```bash
curl -X POST https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "SecurePass123!"
  }'
```

**Response includes JWT tokens:**

```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "username": "user@example.com",
    "email": "user@example.com",
    "role": "user"
  },
  "tokens": {
    "access_token": "eyJraWQiOiJua3RneWtaT0NOMmtmTkJYWEZH...",
    "id_token": "eyJraWQiOiJXOXd1a1wvczlsR1RVdnRcL0MwREw1N1pK...",
    "refresh_token": "eyJjdHkiOiJKV1QiLCJlbmMiOiJBMjU2R0NNIiwiYWxnIjoi..."
  }
}
```

## �🚀 Quick Start

### Prerequisites

- AWS CLI configured
- Dedicated IAM user with managed policy (recommended)

### Deploy in 3 Steps

```bash
# 1. Clone the repository
git clone https://github.com/vishwasvr/guhae-rental-property-app.git
cd guhae-rental-property-app

# 2. Set up IAM user (see Security Setup guide)
# 3. Deploy
cd deployment
AWS_PROFILE=guhae-deployment ./deploy-serverless.sh all
```

**Your app will be live in 3-5 minutes!**

## 📚 Documentation

| **Topic**                   | **Link**                                                                 | **Description**                         |
| --------------------------- | ------------------------------------------------------------------------ | --------------------------------------- |
| **🔐 Security Setup**       | [docs/SECURITY.md](docs/SECURITY.md)                                     | IAM user creation & managed policies    |
| **🚀 Deployment Guide**     | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)                                 | Step-by-step deployment process         |
| **🌐 S3 Frontend**          | [docs/S3_FRONTEND_IMPLEMENTATION.md](docs/S3_FRONTEND_IMPLEMENTATION.md) | S3-hosted frontend architecture details |
| **✅ Deployment Readiness** | [DEPLOYMENT_READINESS_CHECK.md](DEPLOYMENT_READINESS_CHECK.md)           | Complete system validation checklist    |
| **🧪 API Reference**        | [docs/API.md](docs/API.md)                                               | Complete API endpoint documentation     |
| **🚨 Troubleshooting**      | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)                       | Common issues & solutions               |
| **🔧 Development**          | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)                               | Local development setup                 |
| **🏗️ Architecture**         | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)                             | Detailed system design                  |

## ✨ Key Features

- ✅ **S3-Hosted Frontend**: Modern web interface with global CDN delivery
- ✅ **90%+ Cost Reduction**: From EC2 to true serverless architecture
- ✅ **Ultra-Fast Deployments**: 2KB packages deploy in seconds (vs 13MB)
- ✅ **Production-Ready Interface**: Clean, professional login and dashboard
- ✅ **AWS Cognito Authentication**: Enterprise-grade user management with JWT tokens
- ✅ **Email-based Login**: Professional authentication flow with registration
- ✅ **Enterprise Security**: Managed IAM policies with least-privilege access
- ✅ **Semantic Naming**: Professional resource identification
- ✅ **Auto-scaling**: Handle traffic spikes automatically
- ✅ **Global CDN**: CloudFront for worldwide performance with full HTTP method support
- ✅ **Token-based Sessions**: Secure JWT authentication with refresh tokens
- ✅ **Real-time Dashboard**: Property statistics and management
- ✅ **Health Monitoring**: Built-in API health checks and service status
- ✅ **Frontend/Backend Separation**: Production-ready architecture

## 🧪 Quick Test

**Frontend Access:**

1. Visit: https://d3qr4jcsohv892.cloudfront.net
2. **Register** a new account or **Login** with: `demo@example.com` / `Demo123!`
3. Explore the property management dashboard with secure JWT authentication

**API Testing:**

```bash
# Test Authentication
curl -X POST https://d3qr4jcsohv892.cloudfront.net/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "demo@example.com", "password": "Demo123!"}'

# Test Health Checks
curl https://d3qr4jcsohv892.cloudfront.net/api/health
curl https://d3qr4jcsohv892.cloudfront.net/api/dashboard
curl https://d3qr4jcsohv892.cloudfront.net/api/properties

# Direct API Gateway (development)
curl https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/health
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**🏠 Built with ❤️ for modern rental property management**
