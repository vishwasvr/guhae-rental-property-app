import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.aws_helpers import upload_to_s3, save_property_to_dynamodb, get_property_from_dynamodb

class TestAWSHelpers:
    """Test AWS helper utilities"""

    def test_upload_to_s3_success(self, mock_boto3):
        """Test successful S3 upload"""
        mock_resource, mock_client, _, mock_s3, _ = mock_boto3
        
        mock_s3.upload_file.return_value = None  # upload_file doesn't return anything on success
        
        result = upload_to_s3('test-file.txt', 'test-bucket')
        
        assert result is True
        mock_s3.upload_file.assert_called_once_with('test-file.txt', 'test-bucket', 'test-file.txt')

    def test_upload_to_s3_custom_object_name(self, mock_boto3):
        """Test S3 upload with custom object name"""
        mock_resource, mock_client, _, mock_s3, _ = mock_boto3
        
        mock_s3.upload_file.return_value = None
        
        result = upload_to_s3('test-file.txt', 'test-bucket', 'custom-name.txt')
        
        assert result is True
        mock_s3.upload_file.assert_called_once_with('test-file.txt', 'test-bucket', 'custom-name.txt')

    def test_upload_to_s3_failure(self, mock_boto3):
        """Test S3 upload failure"""
        mock_resource, mock_client, _, mock_s3, _ = mock_boto3
        
        mock_s3.upload_file.side_effect = ClientError(
            error_response={'Error': {'Code': 'NoSuchBucket'}},
            operation_name='UploadFile'
        )
        
        result = upload_to_s3('test-file.txt', 'non-existent-bucket')
        
        assert result is False

    def test_save_property_to_dynamodb_success(self, mock_boto3):
        """Test successful DynamoDB save"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.put_item.return_value = {}
        
        property_data = {'id': 'prop-123', 'address': '123 Main St'}
        result = save_property_to_dynamodb('test-table', property_data)
        
        assert result is True
        mock_table.put_item.assert_called_once_with(Item=property_data)

    def test_save_property_to_dynamodb_failure(self, mock_boto3):
        """Test DynamoDB save failure"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.put_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException'}},
            operation_name='PutItem'
        )
        
        property_data = {'id': 'prop-123', 'address': '123 Main St'}
        result = save_property_to_dynamodb('test-table', property_data)
        
        assert result is False

    def test_get_property_from_dynamodb_found(self, mock_boto3):
        """Test getting existing property from DynamoDB"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_item = {'id': 'prop-123', 'address': '123 Main St'}
        mock_table.get_item.return_value = {'Item': mock_item}
        
        result = get_property_from_dynamodb('test-table', 'prop-123')
        
        assert result == mock_item
        mock_table.get_item.assert_called_once_with(Key={'id': 'prop-123'})

    def test_get_property_from_dynamodb_not_found(self, mock_boto3):
        """Test getting non-existent property from DynamoDB"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.get_item.return_value = {}  # No Item key
        
        result = get_property_from_dynamodb('test-table', 'non-existent')
        
        assert result is None

    def test_get_property_from_dynamodb_error(self, mock_boto3):
        """Test DynamoDB get error"""
        mock_resource, mock_client, mock_table, _, _ = mock_boto3
        
        mock_table.get_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ResourceNotFoundException'}},
            operation_name='GetItem'
        )
        
        result = get_property_from_dynamodb('test-table', 'prop-123')
        
        assert result is None