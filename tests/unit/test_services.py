import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.database import DatabaseService
from services.properties import PropertyService


class TestDatabaseService:
    """Test DatabaseService class"""

    @pytest.fixture
    def mock_table(self):
        """Mock DynamoDB table"""
        return MagicMock()

    @pytest.fixture
    def db_service(self, mock_table):
        """Create DatabaseService instance with mocked table"""
        with patch('boto3.resource') as mock_resource:
            mock_resource.return_value.Table.return_value = mock_table
            service = DatabaseService('test-table')
            service.table = mock_table
            yield service

    def test_create_property_success(self, db_service, mock_table):
        """Test successful property creation"""
        property_data = {
            'title': 'Test Property',
            'price': 250000,
            'owner_id': 'test@example.com'
        }

        mock_table.put_item.return_value = None

        result = db_service.create_property(property_data)

        assert 'pk' in result
        assert 'sk' in result
        assert result['owner_id'] == 'test@example.com'
        assert result['title'] == 'Test Property'
        assert 'created_at' in result
        assert 'updated_at' in result
        assert 'id' in result

        mock_table.put_item.assert_called_once()

    def test_get_property_success(self, db_service, mock_table):
        """Test successful property retrieval"""
        expected_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'id': 'test-id',
            'title': 'Test Property'
        }
        mock_table.get_item.return_value = {'Item': expected_item}

        result = db_service.get_property('test-id')

        assert result == expected_item
        mock_table.get_item.assert_called_once_with(
            Key={'pk': 'PROPERTY#test-id', 'sk': 'METADATA'}
        )

    def test_get_property_not_found(self, db_service, mock_table):
        """Test property retrieval when item doesn't exist"""
        mock_table.get_item.return_value = {}

        result = db_service.get_property('nonexistent-id')

        assert result is None

    def test_get_property_exception(self, db_service, mock_table):
        """Test property retrieval with exception"""
        mock_table.get_item.side_effect = Exception("DynamoDB error")

        result = db_service.get_property('test-id')

        assert result is None

    def test_update_property_success(self, db_service, mock_table):
        """Test successful property update"""
        updates = {
            'title': 'Updated Title',
            'price': 300000
        }

        expected_response = {
            'Attributes': {
                'pk': 'PROPERTY#test-id',
                'sk': 'METADATA',
                'title': 'Updated Title',
                'price': 300000,
                'updated_at': '2024-01-01T00:00:00.000000'
            }
        }
        mock_table.update_item.return_value = expected_response

        result = db_service.update_property('test-id', updates)

        assert result == expected_response['Attributes']
        assert 'updated_at' in result

        # Verify update expression was built correctly
        call_args = mock_table.update_item.call_args
        assert 'UpdateExpression' in call_args[1]
        assert 'ExpressionAttributeValues' in call_args[1]

    def test_delete_property_success(self, db_service, mock_table):
        """Test successful property deletion"""
        mock_table.delete_item.return_value = None

        result = db_service.delete_property('test-id')

        assert result is True
        mock_table.delete_item.assert_called_once_with(
            Key={'pk': 'PROPERTY#test-id', 'sk': 'METADATA'}
        )

    def test_delete_property_exception(self, db_service, mock_table):
        """Test property deletion with exception"""
        mock_table.delete_item.side_effect = Exception("Delete failed")

        result = db_service.delete_property('test-id')

        assert result is False

    def test_list_properties_all(self, db_service, mock_table):
        """Test listing all properties"""
        expected_items = [
            {'pk': 'PROPERTY#1', 'sk': 'METADATA', 'title': 'Property 1'},
            {'pk': 'PROPERTY#2', 'sk': 'METADATA', 'title': 'Property 2'}
        ]
        mock_table.scan.return_value = {'Items': expected_items}

        result = db_service.list_properties()

        assert result == expected_items
        mock_table.scan.assert_called_once()

    def test_list_properties_by_owner(self, db_service, mock_table):
        """Test listing properties by owner"""
        expected_items = [
            {'pk': 'PROPERTY#1', 'sk': 'METADATA', 'title': 'Property 1'}
        ]
        mock_table.query.return_value = {'Items': expected_items}

        result = db_service.list_properties(owner_id='test@example.com')

        assert result == expected_items
        mock_table.query.assert_called_once()

    def test_create_user_success(self, db_service, mock_table):
        """Test successful user creation"""
        user_data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }

        mock_table.put_item.return_value = None

        result = db_service.create_user(user_data)

        assert 'pk' in result
        assert 'sk' in result
        assert result['email'] == 'test@example.com'
        assert result['name'] == 'Test User'
        assert 'created_at' in result
        assert 'updated_at' in result

    def test_get_user_success(self, db_service, mock_table):
        """Test successful user retrieval"""
        expected_item = {
            'pk': 'USER#test-id',
            'sk': 'METADATA',
            'id': 'test-id',
            'email': 'test@example.com'
        }
        mock_table.get_item.return_value = {'Item': expected_item}

        result = db_service.get_user('test-id')

        assert result == expected_item

    def test_get_user_by_email_success(self, db_service, mock_table):
        """Test successful user retrieval by email"""
        expected_item = {
            'gsi1pk': 'EMAIL#test@example.com',
            'email': 'test@example.com',
            'name': 'Test User'
        }
        mock_table.query.return_value = {'Items': [expected_item]}

        result = db_service.get_user_by_email('test@example.com')

        assert result == expected_item

    def test_get_user_by_email_not_found(self, db_service, mock_table):
        """Test user retrieval by email when not found"""
        mock_table.query.return_value = {'Items': []}

        result = db_service.get_user_by_email('nonexistent@example.com')

        assert result is None

    def test_get_dashboard_stats_success(self, db_service, mock_table):
        """Test successful dashboard stats retrieval"""
        properties = [
            {'status': 'active', 'title': 'Property 1'},
            {'status': 'inactive', 'title': 'Property 2'},
            {'status': 'active', 'title': 'Property 3'}
        ]
        mock_table.scan.return_value = {'Items': properties}

        result = db_service.get_dashboard_stats()

        assert result['total_properties'] == 3
        assert result['active_properties'] == 2
        assert result['total_users'] == 0
        assert result['total_leases'] == 0

    def test_get_dashboard_stats_exception(self, db_service, mock_table):
        """Test dashboard stats with exception"""
        mock_table.scan.side_effect = Exception("Scan failed")

        result = db_service.get_dashboard_stats()

        assert result['total_properties'] == 0
        assert result['active_properties'] == 0
        assert result['total_users'] == 0
        assert result['total_leases'] == 0


class TestPropertyService:
    """Test PropertyService class"""

    @pytest.fixture
    def mock_db_service(self):
        """Mock DatabaseService"""
        return MagicMock()

    @pytest.fixture
    def property_service(self, mock_db_service):
        """Create PropertyService instance with mocked dependencies"""
        with patch('services.properties.DatabaseService', return_value=mock_db_service), \
             patch('services.properties.config') as mock_config:

            # Mock config
            mock_config.get_aws_config.return_value = {
                'dynamodb_table': 'test-table',
                'region': 'us-east-1',
                's3_bucket': 'test-bucket'
            }
            mock_config.is_feature_enabled.return_value = True
            mock_config.AWS_REGION = 'us-east-1'

            service = PropertyService()
            service.db = mock_db_service
            yield service

    def test_create_property_success(self, property_service, mock_db_service):
        """Test successful property creation"""
        property_data = {
            'title': 'Test Property',
            'price': 250000
        }

        expected_db_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'id': 'test-id',
            'title': 'Test Property',
            'price': 250000,
            'status': 'active',
            'property_type': 'residential',
            'owner_id': 'default-owner'
        }

        mock_db_service.create_property.return_value = expected_db_item

        result = property_service.create_property(property_data)

        assert result['id'] == 'test-id'
        assert result['title'] == 'Test Property'
        assert result['status'] == 'active'
        assert 'pk' not in result  # Should be filtered out
        assert 'sk' not in result  # Should be filtered out

    def test_get_property_success(self, property_service, mock_db_service):
        """Test successful property retrieval"""
        db_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'id': 'test-id',
            'title': 'Test Property'
        }

        mock_db_service.get_property.return_value = db_item

        result = property_service.get_property('test-id')

        assert result is not None
        assert result['id'] == 'test-id'
        assert 'pk' not in result

    def test_get_property_not_found(self, property_service, mock_db_service):
        """Test property retrieval when not found"""
        mock_db_service.get_property.return_value = None

        result = property_service.get_property('nonexistent-id')

        assert result is None

    def test_update_property_success(self, property_service, mock_db_service):
        """Test successful property update"""
        updates = {'title': 'Updated Title'}
        db_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'id': 'test-id',
            'title': 'Updated Title'
        }

        mock_db_service.update_property.return_value = db_item

        result = property_service.update_property('test-id', updates)

        assert result is not None
        assert result['title'] == 'Updated Title'
        assert 'pk' not in result

    def test_update_property_exception(self, property_service, mock_db_service):
        """Test property update with exception"""
        mock_db_service.update_property.side_effect = Exception("Update failed")

        result = property_service.update_property('test-id', {'title': 'New Title'})

        assert result is None

    def test_delete_property_success(self, property_service, mock_db_service):
        """Test successful property deletion"""
        mock_db_service.delete_property.return_value = True

        result = property_service.delete_property('test-id')

        assert result is True

    def test_list_properties_success(self, property_service, mock_db_service):
        """Test successful property listing"""
        db_items = [
            {
                'pk': 'PROPERTY#1',
                'sk': 'METADATA',
                'id': '1',
                'title': 'Property 1'
            },
            {
                'pk': 'PROPERTY#2',
                'sk': 'METADATA',
                'id': '2',
                'title': 'Property 2'
            }
        ]

        mock_db_service.list_properties.return_value = db_items

        result = property_service.list_properties()

        assert len(result) == 2
        assert result[0]['title'] == 'Property 1'
        assert 'pk' not in result[0]

    def test_get_dashboard_stats_success(self, property_service, mock_db_service):
        """Test successful dashboard stats retrieval"""
        expected_stats = {
            'total_properties': 5,
            'active_properties': 3,
            'total_users': 10,
            'total_leases': 2
        }

        mock_db_service.get_dashboard_stats.return_value = expected_stats

        result = property_service.get_dashboard_stats()

        assert result == expected_stats

    def test_upload_property_image_success(self, property_service):
        """Test successful property image upload"""
        with patch.object(property_service, 's3_client') as mock_s3:
            property_service.bucket_name = 'test-bucket'

            mock_s3.put_object.return_value = None

            result = property_service.upload_property_image(
                'test-property-id',
                b'fake-image-data',
                'test.jpg'
            )

            assert result is not None
            assert 'test-bucket' in result
            assert 'properties/test-property-id/' in result
            assert result.endswith('.jpg')

            mock_s3.put_object.assert_called_once()

    def test_upload_property_image_disabled(self, property_service):
        """Test property image upload when feature is disabled"""
        with patch('services.properties.config') as mock_config:
            mock_config.is_feature_enabled.return_value = False

            # Recreate service with disabled uploads
            service = PropertyService()

            result = service.upload_property_image(
                'test-property-id',
                b'fake-image-data',
                'test.jpg'
            )

            assert result is None

    def test_upload_property_image_exception(self, property_service):
        """Test property image upload with exception"""
        with patch.object(property_service, 's3_client') as mock_s3:
            property_service.bucket_name = 'test-bucket'
            mock_s3.put_object.side_effect = Exception("S3 upload failed")

            result = property_service.upload_property_image(
                'test-property-id',
                b'fake-image-data',
                'test.jpg'
            )

            assert result is None

    def test_format_property_response_complete(self, property_service):
        """Test property response formatting with complete data"""
        property_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'gsi1pk': 'OWNER#test@example.com',
            'id': 'test-id',
            'title': 'Test Property',
            'description': 'A test property',
            'address': '123 Test St',
            'price': 250000,
            'property_type': 'house',
            'status': 'active',
            'owner_id': 'test@example.com',
            'images': ['image1.jpg'],
            'created_at': '2024-01-01T00:00:00.000000',
            'updated_at': '2024-01-01T00:00:00.000000'
        }

        result = property_service._format_property_response(property_item)

        # Should not contain DynamoDB keys
        assert 'pk' not in result
        assert 'sk' not in result
        assert 'gsi1pk' not in result

        # Should contain all expected fields
        assert result['id'] == 'test-id'
        assert result['title'] == 'Test Property'
        assert result['description'] == 'A test property'
        assert result['status'] == 'active'

    def test_format_property_response_minimal(self, property_service):
        """Test property response formatting with minimal data"""
        property_item = {
            'pk': 'PROPERTY#test-id',
            'sk': 'METADATA',
            'id': 'test-id'
        }

        result = property_service._format_property_response(property_item)

        # Should have default values for missing fields
        assert result['id'] == 'test-id'
        assert result['title'] == 'Untitled Property'
        assert result['description'] == ''
        assert result['address'] == ''
        assert result['price'] == 0
        assert result['property_type'] == 'residential'
        assert result['status'] == 'active'
        assert result['images'] == []
        assert 'created_at' in result
        assert 'updated_at' in result