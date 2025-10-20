"""
Validation configuration for pre-deployment checks.
This file centralizes all validation rules and can be easily extended
for future resources, environment variables, and validation requirements.
"""

VALIDATION_CONFIG = {
    "environment_variables": {
        "required": [
            "DYNAMODB_TABLE_NAME",
            "S3_BUCKET_NAME",
            "COGNITO_USER_POOL_ID",
            "COGNITO_CLIENT_ID"
        ],
        "recommended": [
            "AWS_REGION",
            "JWT_SECRET_KEY"
        ],
        "optional": [
            "ENVIRONMENT",
            "DEBUG",
            "LOG_LEVEL"
        ]
    },

    "cloudformation_parameters": {
        "required": [
            "TableName",
            "BucketName"
        ],
        "optional": [
            "Environment",
            "NotificationEmail"
        ]
    },

    "aws_resources": {
        "dynamodb": {
            "service": "dynamodb",
            "regions": ["us-east-1", "us-west-2", "eu-west-1"],
            "permissions_required": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ]
        },
        "s3": {
            "service": "s3",
            "permissions_required": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ]
        },
        "cognito": {
            "service": "cognito-idp",
            "permissions_required": [
                "cognito-idp:AdminGetUser",
                "cognito-idp:AdminCreateUser",
                "cognito-idp:AdminSetUserPassword"
            ]
        },
        "lambda": {
            "service": "lambda",
            "permissions_required": [
                "lambda:CreateFunction",
                "lambda:UpdateFunctionCode",
                "lambda:InvokeFunction"
            ]
        }
    },

    "security_checks": {
        "dependency_scanning": {
            "python": {
                "tool": "safety",
                "fail_level": "high",
                "ignore_vulns": []  # Add vulnerability IDs to ignore if needed
            },
            "nodejs": {
                "tool": "npm audit",
                "audit_level": "high"
            }
        },
        "code_scanning": {
            "bandit": {
                "severity": "medium",
                "confidence": "medium"
            }
        }
    },

    "performance_limits": {
        "lambda_package_size_mb": 50,
        "test_coverage_minimum": 80,
        "max_cold_start_time_ms": 5000
    },

    "future_extensions": {
        "additional_services": [
            "rds", "elasticsearch", "kinesis", "sns", "sqs"
        ],
        "monitoring_services": [
            "cloudwatch", "xray", "config"
        ],
        "compliance_checks": [
            "gdpr", "hipaa", "pci_dss", "sox"
        ]
    }
}

def get_required_env_vars():
    """Get list of required environment variables."""
    return VALIDATION_CONFIG["environment_variables"]["required"]

def get_recommended_env_vars():
    """Get list of recommended environment variables."""
    return VALIDATION_CONFIG["environment_variables"]["recommended"]

def get_required_cf_params():
    """Get list of required CloudFormation parameters."""
    return VALIDATION_CONFIG["cloudformation_parameters"]["required"]

def get_aws_services():
    """Get list of AWS services to validate."""
    return list(VALIDATION_CONFIG["aws_resources"].keys())

def get_future_services():
    """Get list of services planned for future implementation."""
    return VALIDATION_CONFIG["future_extensions"]["additional_services"]

def validate_config():
    """Validate the configuration itself for consistency."""
    # Ensure no duplicates between required and recommended env vars
    required = set(get_required_env_vars())
    recommended = set(get_recommended_env_vars())

    if required & recommended:
        overlap = required & recommended
        raise ValueError(f"Environment variables cannot be both required and recommended: {overlap}")

    return True