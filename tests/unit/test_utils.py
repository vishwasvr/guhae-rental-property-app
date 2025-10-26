import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from decimal import Decimal

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils import validators, aws_helpers


class TestValidators:
    """Test validation utility functions"""

    def test_validate_property_data_valid_full(self):
        """Test validation of complete valid property data"""
        valid_data = {
            'address': '123 Main St, City, State 12345',
            'rent': 1500.00,
            'property_type': 'apartment',
            'bedrooms': 2,
            'bathrooms': 1.5,
            'square_feet': 800,
            'available': True
        }

        errors = validators.validate_property_data(valid_data)
        assert errors == []

    def test_validate_property_data_valid_partial(self):
        """Test validation of partial property data"""
        partial_data = {
            'rent': 1200,
            'bedrooms': 1
        }

        errors = validators.validate_property_data(partial_data, partial=True)
        assert errors == []

    def test_validate_property_data_missing_required(self):
        """Test validation fails for missing required fields"""
        invalid_data = {
            'bedrooms': 2,
            'bathrooms': 1
        }

        errors = validators.validate_property_data(invalid_data)
        assert len(errors) >= 2  # Should have errors for address and rent
        assert any('address is required' in error for error in errors)
        assert any('rent is required' in error for error in errors)

    def test_validate_property_data_invalid_address(self):
        """Test validation of invalid address"""
        invalid_data = {
            'address': '12',  # Too short
            'rent': 1000
        }

        errors = validators.validate_property_data(invalid_data)
        assert any('Address must be at least 5 characters' in error for error in errors)

    def test_validate_property_data_invalid_rent(self):
        """Test validation of invalid rent values"""
        test_cases = [
            {'rent': -100, 'expected': 'positive number'},
            {'rent': 0, 'expected': 'positive number'},
            {'rent': 'not-a-number', 'expected': 'valid number'}
        ]

        for case in test_cases:
            errors = validators.validate_property_data(case)
            assert any(case['expected'] in error for error in errors)

    def test_validate_property_data_invalid_property_type(self):
        """Test validation of invalid property type"""
        invalid_data = {
            'address': '123 Main St',
            'rent': 1000,
            'property_type': 'invalid-type'
        }

        errors = validators.validate_property_data(invalid_data)
        assert any('Property type must be one of' in error for error in errors)

    def test_validate_property_data_invalid_bedrooms(self):
        """Test validation of invalid bedroom values"""
        test_cases = [
            {'bedrooms': -1, 'expected': 'between 0 and 20'},
            {'bedrooms': 25, 'expected': 'between 0 and 20'},
            {'bedrooms': 'not-a-number', 'expected': 'valid integer'}
        ]

        for case in test_cases:
            errors = validators.validate_property_data(case)
            assert any(case['expected'] in error for error in errors)

    def test_validate_property_data_invalid_bathrooms(self):
        """Test validation of invalid bathroom values"""
        test_cases = [
            {'bathrooms': -0.5, 'expected': 'between 0 and 20'},
            {'bathrooms': 25.5, 'expected': 'between 0 and 20'},
            {'bathrooms': 'not-a-number', 'expected': 'valid number'}
        ]

        for case in test_cases:
            errors = validators.validate_property_data(case)
            assert any(case['expected'] in error for error in errors)

    def test_validate_property_data_invalid_square_feet(self):
        """Test validation of invalid square feet values"""
        test_cases = [
            {'square_feet': 0, 'expected': 'between 1 and 50,000'},
            {'square_feet': 60000, 'expected': 'between 1 and 50,000'},
            {'square_feet': 'not-a-number', 'expected': 'valid integer'}
        ]

        for case in test_cases:
            errors = validators.validate_property_data(case)
            assert any(case['expected'] in error for error in errors)

    def test_validate_property_data_invalid_available(self):
        """Test validation of invalid available flag"""
        invalid_data = {
            'address': '123 Main St',
            'rent': 1000,
            'available': 'yes'  # Should be boolean
        }

        errors = validators.validate_property_data(invalid_data)
        assert any('Available must be true or false' in error for error in errors)

    def test_validate_email_valid(self):
        """Test validation of valid email addresses"""
        valid_emails = [
            'test@example.com',
            'user.name+tag@domain.co.uk',
            'test123@gmail.com'
        ]

        for email in valid_emails:
            assert validators.validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validation of invalid email addresses"""
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'test@',
            'test.example.com',
            ''
        ]

        for email in invalid_emails:
            assert validators.validate_email(email) is False

    def test_validate_phone_valid(self):
        """Test validation of valid phone numbers"""
        valid_phones = [
            '+1234567890',
            '123-456-7890',
            '(123) 456-7890',
            '1234567890',
            '+1 234 567 8901'
        ]

        for phone in valid_phones:
            assert validators.validate_phone(phone) is True

    def test_validate_phone_invalid(self):
        """Test validation of invalid phone numbers"""
        invalid_phones = [
            '123',  # Too short
            'not-a-phone',
            '',
            'abc123def456'
        ]

        for phone in invalid_phones:
            assert validators.validate_phone(phone) is False


class TestAWSHelpers:
    """Test AWS helper functions"""

    @pytest.fixture
    def mock_s3_client(self):
        """Mock S3 client"""
        with patch('boto3.client') as mock_client:
            yield mock_client.return_value

    @pytest.fixture
    def mock_dynamodb_resource(self):
        """Mock DynamoDB resource"""
        with patch('boto3.resource') as mock_resource:
            yield mock_resource.return_value

    def test_upload_to_s3_success(self, mock_s3_client):
        """Test successful S3 upload"""
        mock_s3_client.upload_file.return_value = None

        result = aws_helpers.upload_to_s3('test.txt', 'test-bucket', 'test-key')

        assert result is True
        mock_s3_client.upload_file.assert_called_once_with('test.txt', 'test-bucket', 'test-key')

    def test_upload_to_s3_default_object_name(self, mock_s3_client):
        """Test S3 upload with default object name"""
        mock_s3_client.upload_file.return_value = None

        result = aws_helpers.upload_to_s3('test.txt', 'test-bucket')

        assert result is True
        mock_s3_client.upload_file.assert_called_once_with('test.txt', 'test-bucket', 'test.txt')

    def test_upload_to_s3_failure(self, mock_s3_client):
        """Test S3 upload failure"""
        from botocore.exceptions import ClientError
        mock_s3_client.upload_file.side_effect = ClientError(
            error_response={'Error': {'Code': 'NoSuchBucket'}},
            operation_name='UploadFile'
        )

        result = aws_helpers.upload_to_s3('test.txt', 'nonexistent-bucket')

        assert result is False

    def test_save_property_to_dynamodb_success(self, mock_dynamodb_resource):
        """Test successful DynamoDB property save"""
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table
        mock_table.put_item.return_value = None

        test_data = {'id': 'test-id', 'name': 'Test Property'}
        result = aws_helpers.save_property_to_dynamodb('test-table', test_data)

        assert result is True
        mock_table.put_item.assert_called_once_with(Item=test_data)

    def test_save_property_to_dynamodb_failure(self, mock_dynamodb_resource):
        """Test DynamoDB property save failure"""
        from botocore.exceptions import ClientError
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table
        mock_table.put_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ValidationException'}},
            operation_name='PutItem'
        )

        test_data = {'id': 'test-id', 'name': 'Test Property'}
        result = aws_helpers.save_property_to_dynamodb('test-table', test_data)

        assert result is False

    def test_get_property_from_dynamodb_success(self, mock_dynamodb_resource):
        """Test successful DynamoDB property retrieval"""
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table
        expected_item = {'id': 'test-id', 'name': 'Test Property'}
        mock_table.get_item.return_value = {'Item': expected_item}

        result = aws_helpers.get_property_from_dynamodb('test-table', 'test-id')

        assert result == expected_item
        mock_table.get_item.assert_called_once_with(Key={'id': 'test-id'})

    def test_get_property_from_dynamodb_not_found(self, mock_dynamodb_resource):
        """Test DynamoDB property retrieval when item doesn't exist"""
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table
        mock_table.get_item.return_value = {}  # No Item key

        result = aws_helpers.get_property_from_dynamodb('test-table', 'nonexistent-id')

        assert result is None

    def test_get_property_from_dynamodb_failure(self, mock_dynamodb_resource):
        """Test DynamoDB property retrieval failure"""
        from botocore.exceptions import ClientError
        mock_table = MagicMock()
        mock_dynamodb_resource.Table.return_value = mock_table
        mock_table.get_item.side_effect = ClientError(
            error_response={'Error': {'Code': 'ResourceNotFoundException'}},
            operation_name='GetItem'
        )

        result = aws_helpers.get_property_from_dynamodb('test-table', 'test-id')

        assert result is None