"""
Minimal DynamoDB service for single-table design
Optimized for lowest cost with pay-per-request pricing
"""
import boto3
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class DatabaseService:
    def __init__(self, table_name: str, region: str = 'us-east-1'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)
    
    def _get_timestamp(self) -> str:
        return datetime.utcnow().isoformat()
    
    # Property operations
    def create_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        property_id = str(uuid.uuid4())
        owner_id = property_data.get('owner_id', 'default-owner')
        
        item = {
            'pk': f'PROPERTY#{property_id}',
            'sk': f'METADATA',
            'gsi1pk': f'OWNER#{owner_id}',
            'id': property_id,
            'owner_id': owner_id,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp(),
            **property_data
        }
        
        self.table.put_item(Item=item)
        return item
    
    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(
                Key={
                    'pk': f'PROPERTY#{property_id}',
                    'sk': 'METADATA'
                }
            )
            return response.get('Item')
        except Exception:
            return None
    
    def update_property(self, property_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        updates['updated_at'] = self._get_timestamp()
        
        # Build update expression
        update_expression = "SET "
        expression_values = {}
        
        for key, value in updates.items():
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value
        
        update_expression = update_expression.rstrip(', ')
        
        response = self.table.update_item(
            Key={
                'pk': f'PROPERTY#{property_id}',
                'sk': 'METADATA'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ReturnValues='ALL_NEW'
        )
        return response['Attributes']
    
    def delete_property(self, property_id: str) -> bool:
        try:
            self.table.delete_item(
                Key={
                    'pk': f'PROPERTY#{property_id}',
                    'sk': 'METADATA'
                }
            )
            return True
        except Exception:
            return False
    
    def list_properties(self, owner_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        if owner_id:
            # Query by owner using GSI
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='gsi1pk = :gsi1pk',
                ExpressionAttributeValues={
                    ':gsi1pk': f'OWNER#{owner_id}'
                },
                Limit=limit
            )
        else:
            # Scan for all properties (expensive but okay for small datasets)
            response = self.table.scan(
                FilterExpression='begins_with(pk, :pk_prefix)',
                ExpressionAttributeValues={
                    ':pk_prefix': 'PROPERTY#'
                },
                Limit=limit
            )
        
        return response.get('Items', [])
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        email = user_data.get('email', '')
        
        item = {
            'pk': f'USER#{user_id}',
            'sk': 'METADATA',
            'gsi1pk': f'EMAIL#{email}',
            'id': user_id,
            'email': email,
            'created_at': self._get_timestamp(),
            'updated_at': self._get_timestamp(),
            **user_data
        }
        
        self.table.put_item(Item=item)
        return item
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.get_item(
                Key={
                    'pk': f'USER#{user_id}',
                    'sk': 'METADATA'
                }
            )
            return response.get('Item')
        except Exception:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.table.query(
                IndexName='GSI1',
                KeyConditionExpression='gsi1pk = :gsi1pk',
                ExpressionAttributeValues={
                    ':gsi1pk': f'EMAIL#{email}'
                },
                Limit=1
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except Exception:
            return None
    
    # Simple metrics for dashboard
    def get_dashboard_stats(self, owner_id: str = None) -> Dict[str, int]:
        try:
            # Get property count
            properties = self.list_properties(owner_id=owner_id, limit=1000)
            property_count = len(properties)
            
            # Simple stats
            stats = {
                'total_properties': property_count,
                'active_properties': len([p for p in properties if p.get('status') == 'active']),
                'total_users': 0,  # Simplified for minimal version
                'total_leases': 0   # Simplified for minimal version
            }
            
            return stats
        except Exception:
            return {
                'total_properties': 0,
                'active_properties': 0,
                'total_users': 0,
                'total_leases': 0
            }