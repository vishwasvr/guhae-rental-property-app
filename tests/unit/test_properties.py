import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.properties import PropertyService

class TestPropertyService:
    """Test PropertyService class"""

    @pytest.fixture
    def property_service(self, mock_env):
        """Create PropertyService with mocked dependencies"""
        with patch('services.properties.config') as mock_config, \
             patch('services.database.boto3') as mock_boto3:
            
            # Mock config
            mock_config.get_aws_config.return_value = {
                'dynamodb_table': 'test-table',
                'region': 'us-east-1',
                's3_bucket': 'test-bucket'
            }
            mock_config.is_feature_enabled.return_value = False
            
            # Mock database service
            mock_db = MagicMock()
            with patch('services.properties.DatabaseService', return_value=mock_db):
                service = PropertyService()
                service.db = mock_db
                yield service, mock_db

    def test_create_property(self, property_service, sample_property):
        """Test creating a property"""
        service, mock_db = property_service
        
        mock_db.create_property.return_value = {**sample_property, 'id': 'new-prop-id'}
        
        result = service.create_property(sample_property)
        
        assert result['id'] == 'new-prop-id'
        assert 'status' in result
        assert 'property_type' in result
        mock_db.create_property.assert_called_once()

    def test_get_property_found(self, property_service):
        """Test getting an existing property"""
        service, mock_db = property_service
        
        mock_property = {'id': 'prop-123', 'address': '123 Test St'}
        mock_db.get_property.return_value = mock_property
        
        result = service.get_property('prop-123')
        
        assert result == mock_property
        mock_db.get_property.assert_called_once_with('prop-123')

    def test_get_property_not_found(self, property_service):
        """Test getting a non-existent property"""
        service, mock_db = property_service
        
        mock_db.get_property.return_value = None
        
        result = service.get_property('non-existent')
        
        assert result is None

    def test_update_property(self, property_service):
        """Test updating a property"""
        service, mock_db = property_service
        
        updates = {'address': '456 New St'}
        mock_db.update_property.return_value = {'id': 'prop-123', 'address': '456 New St'}
        
        result = service.update_property('prop-123', updates)
        
        assert result['address'] == '456 New St'
        mock_db.update_property.assert_called_once_with('prop-123', updates)

    def test_delete_property(self, property_service):
        """Test deleting a property"""
        service, mock_db = property_service
        
        mock_db.delete_property.return_value = True
        
        result = service.delete_property('prop-123')
        
        assert result is True
        mock_db.delete_property.assert_called_once_with('prop-123')

    def test_list_properties(self, property_service):
        """Test listing properties"""
        service, mock_db = property_service
        
        mock_properties = [{'id': 'prop-1'}, {'id': 'prop-2'}]
        mock_db.list_properties.return_value = mock_properties
        
        result = service.list_properties('owner-123')
        
        assert len(result) == 2
        mock_db.list_properties.assert_called_once_with('owner-123', 50)

    def test_get_dashboard_stats(self, property_service):
        """Test getting dashboard statistics"""
        service, mock_db = property_service
        
        mock_stats = {'total_properties': 5, 'active_properties': 3}
        mock_db.get_dashboard_stats.return_value = mock_stats
        
        result = service.get_dashboard_stats('owner-123')
        
        assert result == mock_stats
        mock_db.get_dashboard_stats.assert_called_once_with('owner-123')

    def test_upload_property_image_disabled(self, property_service):
        """Test uploading image when feature is disabled"""
        service, mock_db = property_service
        
        result = service.upload_property_image('prop-123', b'fake-data', 'test.jpg')
        
        assert result is None  # Should return None when S3 is disabled

    def test_upload_property_image_enabled(self, mock_env):
        """Test uploading image when feature is enabled"""
        with patch('services.properties.config') as mock_config, \
             patch('services.database.boto3') as mock_boto3, \
             patch('boto3.client') as mock_boto_client:
            
            # Mock config to enable S3
            mock_config.get_aws_config.return_value = {
                'dynamodb_table': 'test-table',
                'region': 'us-east-1',
                's3_bucket': 'test-bucket'
            }
            mock_config.is_feature_enabled.return_value = True
            
            mock_s3 = MagicMock()
            mock_boto_client.return_value = mock_s3
            
            with patch('services.properties.DatabaseService'):
                service = PropertyService()
                service.s3_client = mock_s3
                service.bucket_name = 'test-bucket'
                
                mock_s3.put_object.return_value = {}
                
                result = service.upload_property_image('prop-123', b'fake-data', 'test.jpg')
                
                assert result is not None
                assert 'prop-123' in result
                mock_s3.put_object.assert_called_once()