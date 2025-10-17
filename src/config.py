"""
Guhae Serverless Configuration
Uses serverless AWS services and single-table DynamoDB design
"""
import os
from typing import Dict, Any

class Config:
    # AWS Settings
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # DynamoDB - Single table for everything
    DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'guhae-serverless-data')
    
    # S3 - Single bucket for all storage
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'guhae-serverless-storage')
    
    # App Settings (for future use)
    ENV = os.getenv('ENV', 'production')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # Feature flags for serverless deployment
    FEATURES = {
        'email_notifications': False,  # Disable SES to save costs
        'advanced_monitoring': False,  # Disable CloudWatch custom metrics
        'file_uploads': True,          # Keep S3 uploads
        'user_authentication': False, # Simplified for MVP
        'multi_tenant': False         # Single tenant for now
    }
    
    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """Get AWS service configuration"""
        return {
            'region': cls.AWS_REGION,
            'dynamodb_table': cls.DYNAMODB_TABLE_NAME,
            's3_bucket': cls.S3_BUCKET_NAME
        }
    
    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if a feature is enabled"""
        return cls.FEATURES.get(feature, False)

# Export for easy import
config = Config()