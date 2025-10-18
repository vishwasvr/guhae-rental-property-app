"""Validation utilities for Guhae."""
import re


def validate_property_data(data, partial=False):
    """Validate property data."""
    errors = []
    
    # Required fields for creation
    if not partial:
        required_fields = ['address', 'rent']
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"{field} is required")
    
    # Validate address
    if 'address' in data:
        if not isinstance(data['address'], str) or len(data['address'].strip()) < 5:
            errors.append("Address must be at least 5 characters long")
    
    # Validate rent
    if 'rent' in data:
        try:
            rent = float(data['rent'])
            if rent <= 0:
                errors.append("Rent must be a positive number")
        except (ValueError, TypeError):
            errors.append("Rent must be a valid number")
    
    # Validate property_type
    if 'property_type' in data:
        valid_types = ['apartment', 'house', 'condo', 'townhouse', 'studio', 'other']
        if data['property_type'] not in valid_types:
            errors.append(f"Property type must be one of: {', '.join(valid_types)}")
    
    # Validate bedrooms
    if 'bedrooms' in data:
        try:
            bedrooms = int(data['bedrooms'])
            if bedrooms < 0 or bedrooms > 20:
                errors.append("Bedrooms must be between 0 and 20")
        except (ValueError, TypeError):
            errors.append("Bedrooms must be a valid integer")
    
    # Validate bathrooms
    if 'bathrooms' in data:
        try:
            bathrooms = float(data['bathrooms'])
            if bathrooms < 0 or bathrooms > 20:
                errors.append("Bathrooms must be between 0 and 20")
        except (ValueError, TypeError):
            errors.append("Bathrooms must be a valid number")
    
    # Validate square_feet
    if 'square_feet' in data and data['square_feet'] is not None:
        try:
            sqft = int(data['square_feet'])
            if sqft <= 0 or sqft > 50000:
                errors.append("Square feet must be between 1 and 50,000")
        except (ValueError, TypeError):
            errors.append("Square feet must be a valid integer")
    
    # Validate available
    if 'available' in data:
        if not isinstance(data['available'], bool):
            errors.append("Available must be true or false")
    
    return errors


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number format."""
    # Simple phone validation - adjust as needed
    pattern = r'^\+?[\d\s\-\(\)]+$'
    return re.match(pattern, phone) is not None and len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 10