import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from utils.validators import validate_property_data, validate_email, validate_phone

class TestValidators:
    """Test validation utilities"""

    def test_validate_property_data_valid_full(self):
        """Test validating complete valid property data"""
        data = {
            'address': '123 Main Street',
            'rent': 1500.00,
            'property_type': 'apartment',
            'bedrooms': 2,
            'bathrooms': 1.5
        }
        
        errors = validate_property_data(data)
        
        assert errors == []

    def test_validate_property_data_valid_partial(self):
        """Test validating partial property data"""
        data = {
            'address': '123 Main Street',
            'rent': 1500.00
        }
        
        errors = validate_property_data(data, partial=True)
        
        assert errors == []

    def test_validate_property_data_missing_required(self):
        """Test validation with missing required fields"""
        data = {'property_type': 'house'}
        
        errors = validate_property_data(data)
        
        assert len(errors) >= 2  # address and rent required
        assert any('address is required' in error for error in errors)
        assert any('rent is required' in error for error in errors)

    def test_validate_property_data_invalid_address(self):
        """Test validation with invalid address"""
        data = {
            'address': '123',  # Too short
            'rent': 1500
        }
        
        errors = validate_property_data(data)
        
        assert any('Address must be at least 5 characters' in error for error in errors)

    def test_validate_property_data_invalid_rent(self):
        """Test validation with invalid rent"""
        test_cases = [
            {'rent': -100, 'expected': 'positive number'},
            {'rent': 'not-a-number', 'expected': 'valid number'},
            {'rent': 0, 'expected': 'positive number'}
        ]
        
        for case in test_cases:
            data = {'address': '123 Main St', 'rent': case['rent']}
            errors = validate_property_data(data)
            assert any(case['expected'] in error for error in errors)

    def test_validate_property_data_invalid_property_type(self):
        """Test validation with invalid property type"""
        data = {
            'address': '123 Main St',
            'rent': 1500,
            'property_type': 'invalid-type'
        }
        
        errors = validate_property_data(data)
        
        assert any('Property type must be one of' in error for error in errors)

    def test_validate_property_data_invalid_bedrooms(self):
        """Test validation with invalid bedrooms"""
        test_cases = [
            {'bedrooms': -1, 'expected': 'between 0 and 20'},
            {'bedrooms': 25, 'expected': 'between 0 and 20'},
            {'bedrooms': 'not-a-number', 'expected': 'valid integer'}
        ]
        
        for case in test_cases:
            data = {'address': '123 Main St', 'rent': 1500, 'bedrooms': case['bedrooms']}
            errors = validate_property_data(data)
            assert any(case['expected'] in error for error in errors)

    def test_validate_email_valid(self):
        """Test validating valid email"""
        valid_emails = [
            'test@example.com',
            'user.name+tag@domain.co.uk',
            'test123@gmail.com'
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True

    def test_validate_email_invalid(self):
        """Test validating invalid email"""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'test@',
            'test.example.com',
            ''
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False

    def test_validate_phone_valid(self):
        """Test validating valid phone numbers"""
        valid_phones = [
            '+1234567890',
            '123-456-7890',
            '(123) 456-7890',
            '1234567890'
        ]
        
        for phone in valid_phones:
            assert validate_phone(phone) is True

    def test_validate_phone_invalid(self):
        """Test validating invalid phone numbers"""
        invalid_phones = [
            '123',
            'abc1234567',
            '123-456-789',
            ''
        ]
        
        for phone in invalid_phones:
            assert validate_phone(phone) is False