import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.database import DatabaseService

class TestDatabaseService:
    """Test DatabaseService class"""

    @pytest.fixture
    def db_service(self, mock_env):
        """Create DatabaseService instance with mocked table"""
        with patch('boto3.resource') as mock_resource:
            mock_table = MagicMock()
            mock_resource.return_value.Table.return_value = mock_table
            service = DatabaseService('test-table')
            service.table = mock_table
            yield service, mock_table

    def test_create_property(self, db_service, sample_property):
        """Test creating a property"""
        service, mock_table = db_service
        
        mock_table.put_item.return_value = {}
        
        result = service.create_property(sample_property)
        
        assert 'id' in result
        assert result['owner_id'] == sample_property['user_id']
        assert 'pk' in result
        assert 'sk' in result
        assert 'gsi1pk' in result
        mock_table.put_item.assert_called_once()

    def test_get_property_found(self, db_service):
        """Test getting an existing property"""
        service, mock_table = db_service
        
        mock_item = {'id': 'prop-123', 'address': '123 Test St'}
        mock_table.get_item.return_value = {'Item': mock_item}
        
        result = service.get_property('prop-123')
        
        assert result == mock_item
        mock_table.get_item.assert_called_once()

    def test_get_property_not_found(self, db_service):
        """Test getting a non-existent property"""
        service, mock_table = db_service
        
        mock_table.get_item.return_value = {}
        
        result = service.get_property('non-existent')
        
        assert result is None

    def test_update_property(self, db_service):
        """Test updating a property"""
        service, mock_table = db_service
        
        updates = {'address': '456 New St', 'rent_amount': 2000}
        existing_item = {'id': 'prop-123', 'address': '123 Old St'}
        
        mock_table.get_item.return_value = {'Item': existing_item}
        mock_table.put_item.return_value = {}
        
        result = service.update_property('prop-123', updates)
        
        assert result['address'] == '456 New St'
        assert result['rent_amount'] == 2000
        mock_table.put_item.assert_called_once()

    def test_delete_property(self, db_service):
        """Test deleting a property"""
        service, mock_table = db_service
        
        mock_table.delete_item.return_value = {}
        
        result = service.delete_property('prop-123')
        
        assert result is True
        mock_table.delete_item.assert_called_once()

    def test_list_properties(self, db_service):
        """Test listing properties for an owner"""
        service, mock_table = db_service
        
        mock_items = [
            {'id': 'prop-1', 'address': '123 St'},
            {'id': 'prop-2', 'address': '456 St'}
        ]
        mock_table.query.return_value = {'Items': mock_items}
        
        result = service.list_properties('owner-123')
        
        assert len(result) == 2
        assert result[0]['id'] == 'prop-1'
        mock_table.query.assert_called_once()

    def test_create_user(self, db_service, sample_user):
        """Test creating a user"""
        service, mock_table = db_service
        
        mock_table.put_item.return_value = {}
        
        result = service.create_user(sample_user)
        
        assert 'id' in result
        assert result['email'] == sample_user['email']
        assert 'pk' in result
        assert 'sk' in result
        mock_table.put_item.assert_called_once()

    def test_get_user(self, db_service):
        """Test getting a user"""
        service, mock_table = db_service
        
        mock_user = {'id': 'user-123', 'email': 'test@example.com'}
        mock_table.get_item.return_value = {'Item': mock_user}
        
        result = service.get_user('user-123')
        
        assert result == mock_user

    def test_get_user_by_email(self, db_service):
        """Test getting user by email"""
        service, mock_table = db_service
        
        mock_user = {'id': 'user-123', 'email': 'test@example.com'}
        mock_table.query.return_value = {'Items': [mock_user]}
        
        result = service.get_user_by_email('test@example.com')
        
        assert result == mock_user

    def test_get_dashboard_stats(self, db_service):
        """Test getting dashboard statistics"""
        service, mock_table = db_service
        
        mock_table.query.return_value = {'Items': [{'id': 'prop-1'}, {'id': 'prop-2'}]}
        
        result = service.get_dashboard_stats('owner-123')
        
        assert 'total_properties' in result
        assert result['total_properties'] == 2