# 📡 API Reference

## Overview

Complete API documentation for the Guhae rental property management system with multi-tenant architecture, JWT-based authentication, and comprehensive finance management.

## Base URL

**Development**: AWS-generated CloudFront domain (guhae-serverless stack)
**Production**: `https://www.guhae.com` (guhae-prod stack)

## Authentication

### 🔐 JWT Token Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

### Authentication Flow

1. **Login/Register** → Receive JWT token
2. **Store token** in localStorage/sessionStorage  
3. **Include token** in subsequent API requests
4. **Token validation** ensures multi-tenant data isolation

## API Endpoints

### 🔍 System Status

#### Health Check

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-19T18:00:00.000Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "storage": "healthy"
  }
}
```

### 🔑 Authentication Endpoints

#### User Registration

```http
POST /auth/register
```

**Request Body:**

```json
{
  "firstName": "John",
  "lastName": "Doe", 
  "email": "john@example.com",
  "password": "securepassword",
  "phone": "+1234567890",
  "dateOfBirth": "1990-01-01",
  "streetAddress": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "zipCode": "12345",
  "company": "Acme Corp"
}
```

**Response:**

```json
{
  "message": "User registered successfully",
  "tokens": {
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token"
  },
  "user": {
    "user_id": "uuid",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### User Login

```http
POST /auth/login
```

**Request Body:**

```json
{
  "username": "john@example.com",
  "password": "securepassword"
}
```

**Response:**

```json
{
  "message": "Login successful",
  "tokens": {
    "access_token": "jwt_access_token", 
    "refresh_token": "jwt_refresh_token"
  },
  "user": {
    "user_id": "uuid",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### 🏠 Properties Management

#### Get All Properties (Protected)

```http
GET /api/properties
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "properties": [
    {
      "property_id": "uuid",
      "owner_id": "user_uuid",
      "title": "2BR Apartment Downtown",
      "address": "123 Main St",
      "rent": 1200,
      "status": "available",
      "bedrooms": 2,
      "bathrooms": 1,
      "description": "Beautiful apartment",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Single Property (Protected)

```http
GET /api/properties/{property_id}
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "property_id": "uuid",
  "owner_id": "user_uuid",
  "title": "2BR Apartment Downtown",
  "address": "123 Main St",
  "rent": 1200,
  "status": "available",
  "bedrooms": 2,
  "bathrooms": 1,
  "description": "Beautiful apartment",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Add New Property (Protected)

```http
POST /api/properties
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "3BR House Suburbia",
  "address": "456 Oak Street",
  "rent": 1800,
  "bedrooms": 3,
  "bathrooms": 2,
  "description": "Spacious family home",
  "status": "available"
}
```

**Response:**

```json
{
  "message": "Property added successfully",
  "property_id": "new_uuid",
  "property": {
    "property_id": "new_uuid",
    "owner_id": "user_uuid",
    "title": "3BR House Suburbia",
    "address": "456 Oak Street",
    "rent": 1800,
    "bedrooms": 3,
    "bathrooms": 2,
    "description": "Spacious family home",
    "status": "available",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Update Property (Protected)

```http
PUT /api/properties/{property_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Updated Property Title",
  "rent": 1900,
  "status": "rented"
}
```

**Response:**

```json
{
  "message": "Property updated successfully",
  "property": {
    "property_id": "uuid",
    "owner_id": "user_uuid",
    "title": "Updated Property Title",
    "rent": 1900,
    "status": "rented",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Delete Property (Protected)

```http
DELETE /api/properties/{property_id}
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "message": "Property deleted successfully"
}
```

### 💰 Finance Management

#### Get Property Finance Data (Protected)

```http
GET /api/properties/{property_id}/finance
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "property_id": "uuid",
  "finance": {
    "ownership_type": "Individual",
    "ownership_status": "Financed",
    "purchase_info": {
      "purchase_price": 250000,
      "purchase_date": "2023-01-15",
      "builder": "ABC Construction",
      "seller": "John Doe",
      "buyer_agent": "Jane Smith",
      "title_company": "Secure Title Co"
    },
    "loans": [
      {
        "loan_id": "loan_uuid",
        "financial_institution": "First National Bank",
        "loan_type": "Conventional",
        "loan_amount": 200000,
        "interest_rate": 3.5,
        "loan_term": 30,
        "monthly_payment": 1200,
        "start_date": "2023-01-15",
        "status": "Active"
      }
    ]
  }
}
```

#### Update Property Finance Data (Protected)

```http
PUT /api/properties/{property_id}/finance
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "ownership_type": "LLC",
  "ownership_status": "Owned",
  "purchase_info": {
    "purchase_price": 300000,
    "purchase_date": "2023-06-01",
    "builder": "XYZ Builders",
    "seller": "Previous Owner",
    "buyer_agent": "Real Estate Pro",
    "title_company": "Reliable Title"
  }
}
```

**Response:**

```json
{
  "message": "Finance data updated successfully",
  "finance": {
    "ownership_type": "LLC",
    "ownership_status": "Owned",
    "purchase_info": {
      "purchase_price": 300000,
      "purchase_date": "2023-06-01",
      "builder": "XYZ Builders",
      "seller": "Previous Owner",
      "buyer_agent": "Real Estate Pro",
      "title_company": "Reliable Title"
    }
  }
}
```

#### Add Loan to Property (Protected)

```http
POST /api/properties/{property_id}/finance/loans
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "financial_institution": "Second Bank",
  "loan_type": "HELOC",
  "loan_amount": 50000,
  "interest_rate": 4.2,
  "loan_term": 15,
  "monthly_payment": 400,
  "start_date": "2024-01-01",
  "status": "Active"
}
```

**Response:**

```json
{
  "message": "Loan added successfully",
  "loan": {
    "loan_id": "new_loan_uuid",
    "financial_institution": "Second Bank",
    "loan_type": "HELOC",
    "loan_amount": 50000,
    "interest_rate": 4.2,
    "loan_term": 15,
    "monthly_payment": 400,
    "start_date": "2024-01-01",
    "status": "Active"
  }
}
```

#### Update Loan (Protected)

```http
PUT /api/properties/{property_id}/finance/loans/{loan_id}
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "status": "Ended",
  "monthly_payment": 0
}
```

**Response:**

```json
{
  "message": "Loan updated successfully",
  "loan": {
    "loan_id": "loan_uuid",
    "status": "Ended",
    "monthly_payment": 0
  }
}
```

#### Delete Loan (Protected)

```http
DELETE /api/properties/{property_id}/finance/loans/{loan_id}
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "message": "Loan deleted successfully"
}
```

### 👤 User Management

#### Get User Profile (Protected)

```http
GET /api/users/profile
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "user_id": "uuid",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User Profile (Protected)

```http
PUT /api/users/profile
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "first_name": "Jonathan",
  "phone": "+1987654321"
}
```

**Response:**

```json
{
  "message": "Profile updated successfully",
  "user": {
    "user_id": "uuid",
    "email": "john@example.com",
    "first_name": "Jonathan",
    "last_name": "Doe",
    "phone": "+1987654321",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## Error Responses

### Standard Error Format

```json
{
  "error": "Error message",
  "details": "Additional error details",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes

- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Access denied (ownership/permissions)
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource already exists
- **500 Internal Server Error**: Server error

### Authentication Errors

#### Invalid/Missing Token

```json
{
  "error": "Invalid or missing authentication token",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Expired Token

```json
{
  "error": "Token has expired",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Validation Errors

#### Missing Required Fields

```json
{
  "error": "Validation failed",
  "details": "Missing required fields: title, address",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Invalid Data Format

```json
{
  "error": "Invalid data format",
  "details": "Email must be a valid email address",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Authorization Errors

#### Resource Not Owned

```json
{
  "error": "Access denied",
  "details": "You don't have permission to access this resource",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Rate Limiting

- **Rate Limit**: 1000 requests per minute per user
- **Headers**: Rate limit information included in response headers
- **429 Too Many Requests**: Returned when rate limit exceeded

## Data Validation

### Property Validation

- **title**: Required, max 200 characters
- **address**: Required, max 500 characters
- **rent**: Required, positive number
- **bedrooms**: Required, integer ≥ 0
- **bathrooms**: Required, number ≥ 0
- **status**: Must be one of: "available", "rented", "maintenance"

### Finance Validation

- **ownership_type**: Must be one of: "Individual", "Joint", "LLC", "Corporation"
- **ownership_status**: Must be one of: "Owned", "Financed", "Rented"
- **purchase_price**: Positive number
- **loan_amount**: Positive number
- **interest_rate**: Number between 0 and 100
- **loan_term**: Positive integer (years)

### User Validation

- **email**: Valid email format, unique
- **password**: Minimum 8 characters (registration only)
- **phone**: Valid phone number format
- **firstName/lastName**: Required, max 100 characters each

## Multi-Tenant Security

### Data Isolation

- All property and finance data is isolated by `owner_id`
- JWT tokens contain user identity for authorization
- Database queries automatically filter by authenticated user
- No cross-tenant data access possible

### Ownership Verification

Every protected endpoint verifies:
1. **Valid JWT token** with user identity
2. **Resource ownership** (property belongs to authenticated user)
3. **Request authorization** before data access

## SDK Integration

### JavaScript/Frontend

```javascript
// Authentication
const authService = new AuthService();
await authService.login('user@example.com', 'password');

// Property management
const propertyService = new PropertyService();
const properties = await propertyService.getProperties();

// Finance management  
const financeService = new FinanceService();
const financeData = await financeService.getPropertyFinance(propertyId);
```

### cURL Examples

#### Login

```bash
curl -X POST https://www.guhae.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user@example.com","password":"password"}'
```

#### Get Properties

```bash
curl -X GET https://www.guhae.com/api/properties \
  -H "Authorization: Bearer your_jwt_token"
```

#### Add Property

```bash
curl -X POST https://www.guhae.com/api/properties \
  -H "Authorization: Bearer your_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Property","address":"123 Street","rent":1500,"bedrooms":2,"bathrooms":1}'
```

## Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture overview
- [Deployment Guide](DEPLOYMENT.md) - Infrastructure deployment
- [Security Guide](SECURITY.md) - Security implementation details
- [Development Guide](DEVELOPMENT.md) - Local development setup