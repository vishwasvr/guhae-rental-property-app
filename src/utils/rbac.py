"""
Role-Based Access Control (RBAC) utilities for the backend Lambda function
"""
import json

# User roles with hierarchical levels
USER_ROLES = {
    'ADMIN': {'name': 'admin', 'level': 100},
    'OWNER': {'name': 'owner', 'level': 80},
    'PROPERTY_MANAGER': {'name': 'property_manager', 'level': 70},
    'TENANT': {'name': 'tenant', 'level': 50},
    'PROSPECT': {'name': 'prospect', 'level': 30},
    'GUEST': {'name': 'guest', 'level': 10}
}

# Permission definitions
ROLE_PERMISSIONS = {
    'admin': [
        'property.*', 'tenant.*', 'lease.*', 'finance.*', 
        'maintenance.*', 'communication.*', 'application.*', 'admin.*'
    ],
    'owner': [
        'property.create', 'property.read.own', 'property.update.own', 'property.delete.own',
        'tenant.create', 'tenant.read', 'tenant.update', 'tenant.delete',
        'lease.create', 'lease.read', 'lease.update', 'lease.terminate',
        'finance.rent.collect', 'finance.expenses.manage', 'finance.reports.view',
        'maintenance.manage', 'maintenance.assign', 'maintenance.complete',
        'communication.tenant', 'application.review', 'application.approve'
    ],
    'property_manager': [
        'property.read.managed', 'property.update.managed',
        'tenant.create', 'tenant.read', 'tenant.update',
        'lease.create', 'lease.read', 'lease.update',
        'finance.rent.collect', 'finance.reports.view',
        'maintenance.manage', 'maintenance.assign',
        'communication.tenant', 'communication.owner',
        'application.review'
    ],
    'tenant': [
        'property.read.public', 'tenant.read.own', 'tenant.update.own',
        'lease.read.own', 'lease.update.own',
        'finance.rent.pay', 'maintenance.request',
        'communication.owner', 'communication.manager'
    ],
    'prospect': [
        'property.read.public', 'tenant.read.own', 'tenant.update.own',
        'application.submit'
    ],
    'guest': [
        'property.read.public'
    ]
}

def get_user_role(user_data):
    """Extract user role from user data"""
    if not user_data:
        return USER_ROLES['GUEST']
    
    account_type = user_data.get('accountType', user_data.get('role', 'guest'))
    
    role_mapping = {
        'admin': USER_ROLES['ADMIN'],
        'administrator': USER_ROLES['ADMIN'],
        'owner': USER_ROLES['OWNER'],
        'landlord': USER_ROLES['OWNER'],
        'property_manager': USER_ROLES['PROPERTY_MANAGER'],
        'manager': USER_ROLES['PROPERTY_MANAGER'],
        'tenant': USER_ROLES['TENANT'],
        'prospect': USER_ROLES['PROSPECT'],
        'prospective_tenant': USER_ROLES['PROSPECT']
    }
    
    return role_mapping.get(account_type.lower(), USER_ROLES['GUEST'])

def has_permission(user_data, permission):
    """Check if user has specific permission"""
    user_role = get_user_role(user_data)
    role_name = user_role['name']
    
    permissions = ROLE_PERMISSIONS.get(role_name, [])
    
    # Check for exact permission match
    if permission in permissions:
        return True
    
    # Check for wildcard permission (e.g., 'property.*' matches 'property.create')
    for perm in permissions:
        if perm.endswith('.*'):
            prefix = perm[:-1]  # Remove the '*'
            if permission.startswith(prefix):
                return True
    
    return False

def can_access_resource(user_data, resource_type, resource_id, action='read'):
    """Check if user can access a specific resource"""
    permission = f"{resource_type}.{action}"
    
    # Check basic permission
    if has_permission(user_data, permission):
        return True
    
    # Check owner-specific permission
    owner_permission = f"{permission}.own"
    if has_permission(user_data, owner_permission):
        return is_resource_owner(user_data, resource_type, resource_id)
    
    # Check managed permission
    managed_permission = f"{permission}.managed"
    if has_permission(user_data, managed_permission):
        return is_resource_managed(user_data, resource_type, resource_id)
    
    return False

def is_resource_owner(user_data, resource_type, resource_id):
    """Check if user owns the resource"""
    if not user_data or not resource_id:
        return False
    
    user_id = user_data.get('id', user_data.get('user_id', user_data.get('sub')))
    
    # This would typically query the database to check ownership
    # For now, we'll use a simple check based on naming convention
    # In a real implementation, you'd query DynamoDB here
    
    return False  # Placeholder - implement actual ownership checking

def is_resource_managed(user_data, resource_type, resource_id):
    """Check if user manages the resource"""
    if not user_data or not resource_id:
        return False
    
    user_id = user_data.get('id', user_data.get('user_id', user_data.get('sub')))
    
    # This would typically query the database to check management rights
    # For now, we'll use a simple check
    # In a real implementation, you'd query DynamoDB here
    
    return False  # Placeholder - implement actual management checking

def filter_properties_by_role(properties, user_data):
    """Filter properties list based on user role and permissions"""
    user_role = get_user_role(user_data)
    role_name = user_role['name']
    
    if role_name in ['admin']:
        # Admins can see all properties
        return properties
    
    elif role_name in ['owner', 'property_manager']:
        # Owners and managers can see their own/managed properties
        # In a real implementation, you'd filter based on ownership/management
        return properties
    
    elif role_name in ['tenant']:
        # Tenants can see public properties and their own
        # Filter to public properties only for now
        return [p for p in properties if p.get('status') == 'active']
    
    else:
        # Prospects and guests can only see public, active properties
        return [p for p in properties if p.get('status') == 'active']

def get_user_from_token(event):
    """Extract user information from JWT token or API request"""
    # This is a placeholder - in a real implementation, you'd:
    # 1. Extract JWT token from Authorization header
    # 2. Validate and decode the token
    # 3. Return user information
    
    headers = event.get('headers', {})
    auth_header = headers.get('Authorization', headers.get('authorization', ''))
    
    if auth_header and auth_header.startswith('Bearer '):
        # TODO: Implement JWT token validation
        # For now, return a default user
        return {
            'id': 'default-user',
            'email': 'user@example.com',
            'accountType': 'owner',  # Default for testing
            'firstName': 'Test',
            'lastName': 'User'
        }
    
    return None

def require_permission(permission):
    """Decorator to require specific permission for an endpoint"""
    def decorator(func):
        def wrapper(event, *args, **kwargs):
            user_data = get_user_from_token(event)
            
            if not has_permission(user_data, permission):
                return {
                    'statusCode': 403,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                    },
                    'body': json.dumps({
                        'error': 'Insufficient permissions',
                        'required_permission': permission
                    })
                }
            
            return func(event, user_data, *args, **kwargs)
        return wrapper
    return decorator

def add_rbac_context(response_data, user_data, resource_type=None):
    """Add RBAC context to API responses"""
    if not isinstance(response_data, dict):
        return response_data
    
    user_role = get_user_role(user_data)
    
    rbac_context = {
        'user_role': user_role['name'],
        'permissions': ROLE_PERMISSIONS.get(user_role['name'], [])
    }
    
    if resource_type:
        available_actions = []
        for action in ['read', 'create', 'update', 'delete']:
            if has_permission(user_data, f"{resource_type}.{action}"):
                available_actions.append(action)
        
        rbac_context['available_actions'] = available_actions
    
    response_data['_rbac'] = rbac_context
    return response_data