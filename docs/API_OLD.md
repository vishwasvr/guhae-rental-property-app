# 📡 API Reference

## Overview

Complete API documentation for the Guhae rental property management system with multi-tenant architecture and JWT-based authentication.

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
  "timestamp": "2025-10-17T06:09:26.312203Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "storage": "healthy"
  }
}
```

#### Welcome/Info

```http
GET /
```

**Response:**

```json
{
  "message": "Welcome to Guhae Rental Property Management API",
  "version": "1.0.0",
  "endpoints": {
    "dashboard": "/api/dashboard",
    "properties": "/api/properties",
    "health": "/api/health"
  },
  "documentation": "https://github.com/vishwasvr/guhae-rental-property-app"
}
```

### 🏠 Properties Management

#### Get All Properties

```http
GET /api/properties
```

**Response:**

```json
{
  "properties": [
    {
      "property_id": "uuid",
      "title": "2BR Apartment Downtown",
      "address": "123 Main St",
      "rent": 1200,
      "status": "available"
    }
  ]
}
```

#### Add New Property

```http
POST /api/properties
Content-Type: application/json

{
  "title": "Property Title",
  "address": "Full Address",
  "rent": 1200,
  "description": "Property description",
  "bedrooms": 2,
  "bathrooms": 1
}
```

**Response:**

```json
{
  "message": "Property added successfully",
  "property_id": "uuid"
}
```

#### Get Property Details

```http
GET /api/properties/{property_id}
```

**Response:**

```json
{
  "property_id": "uuid",
  "title": "Property Title",
  "address": "Full Address",
  "rent": 1200,
  "description": "Property description",
  "bedrooms": 2,
  "bathrooms": 1,
  "status": "available",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Update Property

```http
PUT /api/properties/{property_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "rent": 1300
}
```

**Response:**

```json
{
  "message": "Property updated successfully"
}
```

#### Delete Property

```http
DELETE /api/properties/{property_id}
```

**Response:**

```json
{
  "message": "Property deleted successfully"
}
```

### 📊 Dashboard & Analytics

#### Get Dashboard Data

```http
GET /api/dashboard
```

**Response:**

```json
{
  "total_properties": 10,
  "active_properties": 8,
  "total_users": 5,
  "total_leases": 6,
  "monthly_revenue": 9600,
  "occupancy_rate": 80.0
}
```

### 🏠 Web Interface

#### Home/Dashboard Page

```http
GET /
```

Returns the main dashboard HTML interface.

#### Add Property Form

```http
GET /add-property
```

Returns the property addition form.

#### Properties List

```http
GET /properties
```

Returns the properties management interface.

#### Property Detail View

```http
GET /property/{property_id}
```

Returns detailed view for a specific property.

## Response Codes

| **Code** | **Status**            | **Description**               |
| -------- | --------------------- | ----------------------------- |
| `200`    | OK                    | Request successful            |
| `201`    | Created               | Resource created successfully |
| `400`    | Bad Request           | Invalid request data          |
| `404`    | Not Found             | Resource not found            |
| `500`    | Internal Server Error | Server error occurred         |

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message",
  "message": "Detailed error description",
  "statusCode": 400
}
```

### Common Error Examples

#### Property Not Found

```json
{
  "error": "Property not found",
  "message": "Property with ID 'abc123' does not exist",
  "statusCode": 404
}
```

#### Validation Error

```json
{
  "error": "Validation failed",
  "message": "Required field 'title' is missing",
  "statusCode": 400
}
```

#### Server Error

```json
{
  "error": "Internal server error",
  "message": "Database connection failed",
  "statusCode": 500
}
```

## Request/Response Examples

### cURL Examples

#### List all properties

```bash
curl -X GET "https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/properties"
```

#### Add a new property

```bash
curl -X POST "https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/properties" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Modern 2BR Apartment",
    "address": "456 Oak Street, Downtown",
    "rent": 1500,
    "description": "Beautiful modern apartment with city views",
    "bedrooms": 2,
    "bathrooms": 2
  }'
```

#### Get dashboard data

```bash
curl -X GET "https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/dashboard"
```

### JavaScript/Fetch Examples

#### Get properties

```javascript
fetch(
  "https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/properties"
)
  .then((response) => response.json())
  .then((data) => console.log(data));
```

#### Add property

```javascript
fetch(
  "https://3ocjvh7hwj.execute-api.us-east-1.amazonaws.com/prod/api/properties",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: "Modern 2BR Apartment",
      address: "456 Oak Street, Downtown",
      rent: 1500,
      description: "Beautiful modern apartment with city views",
      bedrooms: 2,
      bathrooms: 2,
    }),
  }
)
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Rate Limits

- **Per IP**: 1000 requests per hour
- **Per API Key**: 10,000 requests per hour (when authentication is implemented)
- **Burst**: Up to 50 requests per second

## Data Models

### Property Model

```javascript
{
  property_id: "string (UUID)",
  title: "string (required)",
  address: "string (required)",
  rent: "number (required)",
  description: "string (optional)",
  bedrooms: "number (optional)",
  bathrooms: "number (optional)",
  status: "string (available|rented|maintenance)",
  created_at: "ISO 8601 timestamp",
  updated_at: "ISO 8601 timestamp"
}
```

### Dashboard Model

```javascript
{
  total_properties: "number",
  active_properties: "number",
  total_users: "number",
  total_leases: "number",
  monthly_revenue: "number (optional)",
  occupancy_rate: "number (optional, percentage)"
}
```

## Testing the API

### Automated Testing

```bash
# Test all endpoints
cd deployment
./test-api.sh

# Test specific endpoint
curl -X GET "https://YOUR-API-URL/api/dashboard"
```

### Manual Testing Tools

- **Postman**: Import the API collection
- **curl**: Command line testing
- **Browser**: GET endpoints and web interface
- **Thunder Client**: VS Code extension

## Support & Troubleshooting

- Check [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues
- API responds with detailed error messages
- Monitor CloudWatch logs for Lambda function errors
- Test locally using the development server (see [Development Guide](DEVELOPMENT.md))
