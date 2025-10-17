# Role-Based Access Control (RBAC) System

## Overview

The Guhae Rental Property Application implements a comprehensive role-based access control system to ensure secure and appropriate access to features and data based on user roles.

## User Roles

### 1. **System Administrator** (`admin`)

- **Level**: 100 (Highest)
- **Description**: Full system access and management
- **Permissions**: Complete system administration and oversight

**Key Features**:

- ✅ Manage all users and properties
- ✅ Access system configuration
- ✅ View all reports and audit logs
- ✅ Manage system settings
- ✅ Override any restrictions

---

### 2. **Property Owner** (`owner`)

- **Level**: 80
- **Description**: Property owner with full management rights
- **Permissions**: Full property management, tenant management, financial control

**Key Features**:

- ✅ Create, edit, and delete own properties
- ✅ Manage tenants and lease agreements
- ✅ Collect rent and manage finances
- ✅ Handle maintenance requests
- ✅ Review and approve rental applications
- ✅ Generate financial reports

---

### 3. **Property Manager** (`property_manager`)

- **Level**: 70
- **Description**: Manages properties on behalf of owners
- **Permissions**: Property management, tenant relations, maintenance coordination

**Key Features**:

- ✅ Manage assigned properties
- ✅ Handle tenant applications and relations
- ✅ Coordinate maintenance requests
- ✅ Collect rent payments
- ✅ Generate property reports
- ❌ Cannot create/delete properties (owner permission required)

---

### 4. **Tenant** (`tenant`)

- **Level**: 50
- **Description**: Current tenant renting a property
- **Permissions**: View lease, pay rent, submit maintenance requests

**Key Features**:

- ✅ View and update own profile
- ✅ View lease information
- ✅ Make rent payments
- ✅ Submit maintenance requests
- ✅ Communicate with property manager/owner
- ❌ Cannot access other tenants' information
- ❌ Cannot manage properties

---

### 5. **Prospective Tenant** (`prospect`)

- **Level**: 30
- **Description**: Looking for rental properties
- **Permissions**: Browse properties, submit applications

**Key Features**:

- ✅ Browse available properties
- ✅ Submit rental applications
- ✅ Save favorite properties
- ✅ Schedule property viewings
- ❌ Cannot access tenant-specific features
- ❌ Limited profile information

---

### 6. **Guest** (`guest`)

- **Level**: 10 (Lowest)
- **Description**: Unauthenticated or limited access user
- **Permissions**: Limited browsing access

**Key Features**:

- ✅ View publicly available properties
- ✅ Basic property search
- ❌ Cannot submit applications
- ❌ Cannot access any personal information
- ❌ Cannot communicate with other users

## Permission System

### Permission Categories

1. **Property Management**

   - `property.create` - Create new properties
   - `property.read` - View all properties
   - `property.read.public` - View publicly listed properties
   - `property.read.own` - View own properties
   - `property.read.managed` - View managed properties
   - `property.update` - Edit any property
   - `property.update.own` - Edit own properties
   - `property.update.managed` - Edit managed properties
   - `property.delete` - Delete any property
   - `property.delete.own` - Delete own properties
   - `property.publish` - Publish/unpublish properties

2. **Tenant Management**

   - `tenant.create` - Add new tenants
   - `tenant.read` - View tenant information
   - `tenant.read.own` - View own tenant profile
   - `tenant.update` - Edit tenant information
   - `tenant.update.own` - Edit own tenant profile
   - `tenant.delete` - Remove tenants
   - `tenant.applications.manage` - Manage rental applications

3. **Financial Management**

   - `finance.rent.collect` - Collect rent payments
   - `finance.rent.pay` - Make rent payments
   - `finance.expenses.manage` - Manage property expenses
   - `finance.reports.view` - View financial reports
   - `finance.reports.generate` - Generate financial reports

4. **Maintenance Management**

   - `maintenance.request` - Submit maintenance requests
   - `maintenance.manage` - Manage maintenance requests
   - `maintenance.assign` - Assign maintenance tasks
   - `maintenance.complete` - Mark maintenance as complete

5. **Communication**
   - `communication.tenant` - Communicate with tenants
   - `communication.owner` - Communicate with property owners
   - `communication.manager` - Communicate with property managers
   - `communication.broadcast` - Send broadcast messages

## Implementation

### Frontend (JavaScript)

```javascript
// Initialize RBAC for current user
const user = AuthUtils.getCurrentUser();
rbacManager.initialize(user);

// Check permissions
if (rbacManager.hasPermission("property.create")) {
  // Show "Add Property" button
}

// Check resource access
if (rbacManager.canAccessResource("property", propertyId, "update")) {
  // Show edit button
}
```

### Backend (Python)

```python
from utils.rbac import has_permission, can_access_resource, get_user_from_token

# Check permissions in Lambda function
user_data = get_user_from_token(event)
if not has_permission(user_data, 'property.create'):
    return {
        'statusCode': 403,
        'body': json.dumps({'error': 'Insufficient permissions'})
    }
```

## Dashboard Customization

Each role gets a customized dashboard with role-appropriate widgets and actions:

### Owner Dashboard

- My Properties
- Rental Income
- Maintenance Requests
- Tenant Overview
- Quick Actions: Add Property, Collect Rent, View Reports

### Property Manager Dashboard

- Managed Properties
- Tenant Applications
- Maintenance Queue
- Rent Collection
- Quick Actions: Schedule Showing, Process Application, Assign Maintenance

### Tenant Dashboard

- My Lease
- Rent Status
- Maintenance Requests
- Announcements
- Quick Actions: Pay Rent, Request Maintenance, Contact Manager

## Security Features

1. **Hierarchical Permissions**: Higher-level roles can perform actions of lower-level roles
2. **Resource Ownership**: Users can only modify resources they own (unless admin)
3. **Contextual Access**: Permissions are checked for each specific action and resource
4. **Frontend Hiding**: UI elements are hidden based on permissions (security by obscurity + backend validation)
5. **Backend Validation**: All permissions are validated on the server side
6. **Audit Trail**: All actions are logged with user role context

## Migration Guide

If you have existing users, update their account types:

- `landlord` → `owner`
- `company` → `property_manager`
- `agent` → `property_manager`
- Existing `tenant` → `tenant`
- New users without properties → `prospect`

## API Response Format

All API responses include RBAC context:

```json
{
  "properties": [...],
  "_rbac": {
    "user_role": "owner",
    "permissions": ["property.create", "property.read.own", ...],
    "available_actions": ["read", "create", "update", "delete"]
  }
}
```

This comprehensive RBAC system ensures that each user has appropriate access to features and data based on their role in the rental property ecosystem.
