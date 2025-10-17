"""
Minimal property service for cost-optimized deployment
Uses single-table DynamoDB design and simplified S3 storage
"""
import boto3
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from .database import DatabaseService
from ..config import config

class PropertyService:
    def __init__(self):
        aws_config = config.get_aws_config()
        self.db = DatabaseService(
            table_name=aws_config['dynamodb_table'],
            region=aws_config['region']
        )
        
        # S3 client for file uploads (if feature enabled)
        if config.is_feature_enabled('file_uploads'):
            self.s3_client = boto3.client('s3', region_name=aws_config['region'])
            self.bucket_name = aws_config['s3_bucket']
        else:
            self.s3_client = None
            self.bucket_name = None
    
    def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new property"""
        # Set default values for minimal version
        property_data.setdefault('status', 'active')
        property_data.setdefault('property_type', 'residential')
        property_data.setdefault('owner_id', 'default-owner')
        
        # Create in database
        property_item = self.db.create_property(property_data)
        
        return self._format_property_response(property_item)
    
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a property by ID"""
        property_item = self.db.get_property(property_id)
        if not property_item:
            return None
        
        return self._format_property_response(property_item)
    
    def update_property(self, property_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a property"""
        try:
            updated_item = self.db.update_property(property_id, updates)
            return self._format_property_response(updated_item)
        except Exception:
            return None
    
    def delete_property(self, property_id: str) -> bool:
        """Delete a property"""
        return self.db.delete_property(property_id)
    
    def list_properties(self, owner_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List properties"""
        properties = self.db.list_properties(owner_id=owner_id, limit=limit)
        return [self._format_property_response(prop) for prop in properties]
    
    def get_dashboard_stats(self, owner_id: str = None) -> Dict[str, int]:
        """Get dashboard statistics"""
        return self.db.get_dashboard_stats(owner_id=owner_id)
    
    def upload_property_image(self, property_id: str, file_data: bytes, filename: str) -> Optional[str]:
        """Upload property image to S3"""
        if not config.is_feature_enabled('file_uploads') or not self.s3_client:
            return None
        
        try:
            # Generate unique filename
            file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
            s3_key = f"properties/{property_id}/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_data,
                ContentType=f'image/{file_extension}',
                ACL='public-read'
            )
            
            # Return the URL
            return f"https://{self.bucket_name}.s3.{config.AWS_REGION}.amazonaws.com/{s3_key}"
        
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None
    
    def _format_property_response(self, property_item: Dict[str, Any]) -> Dict[str, Any]:
        """Format property item for API response"""
        # Remove DynamoDB-specific keys
        response = {k: v for k, v in property_item.items() 
                   if not k.startswith('pk') and not k.startswith('sk') and not k.startswith('gsi')}
        
        # Ensure required fields exist
        response.setdefault('id', property_item.get('id', ''))
        response.setdefault('title', 'Untitled Property')
        response.setdefault('description', '')
        response.setdefault('address', '')
        response.setdefault('price', 0)
        response.setdefault('property_type', 'residential')
        response.setdefault('status', 'active')
        response.setdefault('owner_id', 'default-owner')
        response.setdefault('images', [])
        response.setdefault('created_at', datetime.utcnow().isoformat())
        response.setdefault('updated_at', datetime.utcnow().isoformat())
        
        return response