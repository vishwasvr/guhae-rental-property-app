# Guhae - Serverless Rental Property Management

A modern, serverless rental property management application built on AWS Lambda with enterprise-grade security and semantic naming conventions.

## 🌐 Live Demo

**Frontend Application**: https://d3qr4jcsohv892.cloudfront.net

**Demo Login Credentials (for testing):**

- **Username**: `demo`
- **Password**: `demo123`

> **Note**: The system includes a production-ready authentication system. The above credentials are provided for demonstration and testing purposes.

**API Endpoints:**

- **API Gateway**: https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod
- **Health Check**: `curl https://d3qr4jcsohv892.cloudfront.net/api/health`
- **Dashboard API**: `curl https://d3qr4jcsohv892.cloudfront.net/api/dashboard`

**Architecture:**

- **Frontend**: S3 + CloudFront CDN (global edge caching)
- **Backend**: Lambda + API Gateway (serverless)

## 🏗️ Architecture

**S3-Hosted Frontend + Serverless Backend:**

- **RentalPropertyAssetsBucket** - S3 bucket for frontend hosting & property assets
- **RentalPropertyWebDistribution** - CloudFront CDN for global frontend delivery
- **RentalPropertyApiHandler** - Lambda function for API backend (2KB package)
- **RentalPropertyApiGateway** - REST API endpoints with /api/\* routing
- **RentalPropertiesTable** - DynamoDB table for rental data (pay-per-request)
- **RentalPropertyLambdaExecutionRole** - IAM role with least-privilege permissions

**Request Flow:**

1. `yourdomain.com/` → CloudFront → S3 (frontend files)
2. `yourdomain.com/api/*` → CloudFront → API Gateway → Lambda (backend)

## 💰 Cost Structure

**Monthly Costs (Pay-per-use):**

- **Idle Cost**: ~$0.50-$2.00/month (90%+ reduction vs EC2)
- **1,000 page views**: ~$0.50/month
- **10,000 page views**: ~$2.00/month
- **100,000 page views**: ~$15.00/month

**Breakdown:**

- **Lambda**: $0.0000166667/request + $0.0000000021/MB-ms
- **API Gateway**: $3.50/million requests
- **CloudFront**: $0.085/GB + $0.0075/10k requests
- **DynamoDB**: $0.25/million reads, $1.25/million writes
- **S3**: $0.023/GB storage + $0.0004/1k requests

_Compared to traditional EC2 deployment: $9.11/month baseline + compute costs_

## 🚀 Quick Start

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
- ✅ **Authentication System**: Secure login with role-based access control
- ✅ **Enterprise Security**: Managed IAM policies with least-privilege access
- ✅ **Semantic Naming**: Professional resource identification
- ✅ **Auto-scaling**: Handle traffic spikes automatically
- ✅ **Global CDN**: CloudFront for worldwide performance with full HTTP method support
- ✅ **Working Authentication**: Complete login system with token-based sessions
- ✅ **Real-time Dashboard**: Property statistics and management
- ✅ **Health Monitoring**: Built-in API health checks and service status
- ✅ **Frontend/Backend Separation**: Production-ready architecture

## 🧪 Quick Test

**Frontend Access:**

1. Visit: https://d3qr4jcsohv892.cloudfront.net
2. Login with test credentials: `demo` / `demo123`
3. Explore the property management dashboard

**API Testing:**

```bash
# Test via CloudFront (production routing)
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
