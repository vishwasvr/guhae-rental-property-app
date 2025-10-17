# Guhae - Serverless Rental Property Management

A modern, serverless rental property management application built on AWS Lambda with enterprise-grade security and semantic naming conventions.

## 🌐 Live Demo

- **API Gateway**: https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod
- **CloudFront CDN**: https://d3qr4jcsohv892.cloudfront.net
- **Test Dashboard**: `curl https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/dashboard`

## 🏗️ Architecture

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

| **Topic**               | **Link**                                           | **Description**                      |
| ----------------------- | -------------------------------------------------- | ------------------------------------ |
| **🔐 Security Setup**   | [docs/SECURITY.md](docs/SECURITY.md)               | IAM user creation & managed policies |
| **🚀 Deployment Guide** | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)           | Step-by-step deployment process      |
| **🧪 API Reference**    | [docs/API.md](docs/API.md)                         | Complete API endpoint documentation  |
| **🚨 Troubleshooting**  | [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues & solutions            |
| **🔧 Development**      | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)         | Local development setup              |
| **🏗️ Architecture**     | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)       | Detailed system design               |

## ✨ Key Features

- ✅ **90%+ Cost Reduction**: From EC2 to serverless architecture
- ✅ **Enterprise Security**: Managed IAM policies with least-privilege access
- ✅ **Semantic Naming**: Professional resource identification
- ✅ **Auto-scaling**: Handle traffic spikes automatically
- ✅ **Global CDN**: CloudFront for worldwide performance
- ✅ **Real-time Dashboard**: Property statistics and management

## 🧪 Quick API Test

```bash
# Test the live API
curl https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/dashboard
curl https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/properties
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
