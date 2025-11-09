# Fayvad Email Platform API - Overview

## Base Information

### Base URL
```
https://mail.fayvad.com/fayvad_api/
```

### API Version
- **Current Version**: v1
- **Status**: Production Ready
- **Last Updated**: July 28, 2025

### Content Type
All requests and responses use `application/json` content type.

### CORS Configuration
The API supports CORS for the following origins:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:3002`
- `http://localhost:8000`
- `http://localhost:8001`
- `http://localhost:8002`
- `http://mail.fayvad.com`
- `https://mail.fayvad.com`

---

## 🔐 Authentication & Authorization

### Token Authentication
All authenticated endpoints require a token in the Authorization header:
```
Authorization: Token <your_token>
```

### Token Format
- **Type**: Django REST Framework Token
- **Length**: 40 characters
- **Format**: Alphanumeric string
- **Expiration**: Tokens do not expire by default (can be configured)

### Authentication Endpoints
- **Login**: `POST /auth/login/`
- **Logout**: `POST /auth/logout/`
- **Refresh**: `POST /auth/refresh/`
- **Current User**: `GET /auth/me/`

### Role-Based Access Control

#### User Roles
1. **Superuser (Admin)**
   - Full system access
   - Can manage all organizations, users, and domains
   - Access to all admin endpoints

2. **Organization Admin**
   - Manage their organization's email accounts
   - View organization limits and usage
   - Access to org-specific endpoints

3. **Regular User**
   - Personal profile management
   - Email operations
   - Limited access to organization data

#### Permission Matrix

| Endpoint Category | Superuser | Org Admin | User |
|------------------|-----------|-----------|------|
| System Admin | ✅ Full | ❌ None | ❌ None |
| Organization Management | ✅ Full | ✅ Own Org | ❌ None |
| User Management | ✅ Full | ✅ Org Users | ✅ Self |
| Domain Management | ✅ Full | ❌ None | ❌ None |
| Email Operations | ✅ Full | ✅ Org Emails | ✅ Own |
| Analytics & Reports | ✅ Full | ✅ Org Data | ❌ None |
| Health & Monitoring | ✅ Full | ❌ None | ❌ None |

---

## 📊 API Structure

### Endpoint Categories

1. **Authentication** (`/auth/`)
   - User login/logout
   - Token management
   - Current user info

2. **System Administration** (`/admin/`)
   - Organization management
   - User management
   - Domain management
   - Analytics and reporting
   - System health monitoring

3. **Organization Management** (`/org/`)
   - Email account management
   - Organization limits and usage
   - Subscription management
   - User management within org

4. **Email Operations** (`/email/`)
   - Email authentication
   - Message management
   - Folder operations
   - Attachment handling

5. **Staff Operations** (`/me/`)
   - Personal profile
   - Password management
   - Personal usage stats

6. **ERP Integration** (`/erp/`)
   - Usage summaries
   - Provisioning
   - Billing webhooks

7. **Public Endpoints**
   - Health checks
   - API documentation

---

## 🔧 Error Handling

### Standard Error Response Format
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "field_errors": {
    "field_name": ["Error message"]
  }
}
```

### HTTP Status Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not supported |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `AUTHENTICATION_FAILED` | Invalid credentials |
| `PERMISSION_DENIED` | Insufficient permissions |
| `VALIDATION_ERROR` | Request data validation failed |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `QUOTA_EXCEEDED` | Organization limits exceeded |
| `DOMAIN_VERIFICATION_FAILED` | Domain DNS verification failed |

---

## 📝 Request/Response Headers

### Required Headers
```
Content-Type: application/json
Authorization: Token <your_token>  # For authenticated endpoints
```

### Optional Headers
```
Accept: application/json
User-Agent: Your-App-Name/1.0
```

### Response Headers
```
Content-Type: application/json
X-Total-Count: 100  # For paginated responses
X-Rate-Limit-Remaining: 999  # Rate limiting info
```

---

## 📄 Pagination

### Pagination Format
```json
{
  "count": 100,
  "next": "https://mail.fayvad.com/fayvad_api/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

### Query Parameters
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

---

## 🔍 Rate Limiting

### Limits
- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **Bulk operations**: 10 requests per hour

### Rate Limit Headers
```
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 999
X-Rate-Limit-Reset: 1640995200
```

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `GET /docs/`
- **OpenAPI Schema**: `GET /schema/`

### SDKs and Libraries
- **Python**: Django REST Framework client
- **JavaScript**: Axios/Fetch compatible
- **cURL**: All endpoints support cURL requests

---

## 🔒 Security

### Data Protection
- All data transmitted over HTTPS
- Passwords hashed using Django's password hashers
- API keys stored as SHA-256 hashes
- Session tokens with configurable expiration

### Best Practices
1. Store tokens securely
2. Use HTTPS for all requests
3. Implement proper error handling
4. Respect rate limits
5. Validate all input data
6. Use appropriate user roles

---

*This document provides an overview of the Fayvad Email Platform API. For detailed endpoint documentation, see the specific category documents.* 