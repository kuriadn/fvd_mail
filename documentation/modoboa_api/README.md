# Fayvad Email Platform API Documentation

## 📚 Documentation Index

Welcome to the comprehensive API documentation for the Fayvad Email Platform. This documentation is organized into logical sections to help you quickly find the information you need.

---

## 📖 Quick Start

### Getting Started
1. **Read the Overview** - Start with the [API Overview](01_API_OVERVIEW.md) to understand the basic concepts
2. **Authentication** - Learn about authentication in [Authentication Endpoints](02_AUTHENTICATION_ENDPOINTS.md)
3. **Choose Your Role** - Select the appropriate documentation based on your role and needs

### Base URL
```
https://mail.fayvad.com/fayvad_api/
```

### Authentication
All authenticated endpoints require a token in the Authorization header:
```
Authorization: Token <your_token>
```

---

## 📋 Documentation Structure

### 1. [API Overview](01_API_OVERVIEW.md)
- Base information and configuration
- Authentication & authorization
- API structure and organization
- Error handling standards
- Security considerations
- Rate limiting policies

### 2. [Authentication Endpoints](02_AUTHENTICATION_ENDPOINTS.md)
- User login and logout
- Token management
- Current user information
- API key management
- Security best practices

### 3. [System Administration Endpoints](03_SYSTEM_ADMIN_ENDPOINTS.md)
- Organization management
- User management
- Domain management
- Analytics and reporting
- System health monitoring
- Usage statistics

### 4. [Organization Management Endpoints](04_ORGANIZATION_MANAGEMENT_ENDPOINTS.md)
- Email account management
- Organization limits and usage
- Subscription management
- Organization profile
- User management within org

### 5. [Email Operations Endpoints](05_EMAIL_OPERATIONS_ENDPOINTS.md)
- Email authentication
- Message management
- Folder operations
- Attachment handling
- Draft management
- Email filters

### 6. [Staff Operations Endpoints](06_STAFF_OPERATIONS_ENDPOINTS.md)
- Personal profile management
- Password management
- Personal usage statistics

### 7. [ERP Integration Endpoints](07_ERP_INTEGRATION_ENDPOINTS.md)
- Usage summaries
- Organization provisioning
- Email account provisioning
- Billing webhooks
- Data synchronization

### 8. [Public Endpoints](08_PUBLIC_ENDPOINTS.md)
- Health checks
- API documentation
- System status
- Public analytics
- Security information

---

## 👥 Role-Based Access

### System Administrators
- **Primary Documentation**: [System Administration Endpoints](03_SYSTEM_ADMIN_ENDPOINTS.md)
- **Additional**: [API Overview](01_API_OVERVIEW.md), [Authentication Endpoints](02_AUTHENTICATION_ENDPOINTS.md)
- **Key Capabilities**: Full system management, user management, analytics, health monitoring

### Organization Administrators
- **Primary Documentation**: [Organization Management Endpoints](04_ORGANIZATION_MANAGEMENT_ENDPOINTS.md)
- **Additional**: [Authentication Endpoints](02_AUTHENTICATION_ENDPOINTS.md), [Staff Operations Endpoints](06_STAFF_OPERATIONS_ENDPOINTS.md)
- **Key Capabilities**: Email account management, organization limits, subscription management

### Email Users
- **Primary Documentation**: [Email Operations Endpoints](05_EMAIL_OPERATIONS_ENDPOINTS.md)
- **Additional**: [Authentication Endpoints](02_AUTHENTICATION_ENDPOINTS.md), [Staff Operations Endpoints](06_STAFF_OPERATIONS_ENDPOINTS.md)
- **Key Capabilities**: Email management, personal profile, usage statistics

### Developers/Integrators
- **Primary Documentation**: [ERP Integration Endpoints](07_ERP_INTEGRATION_ENDPOINTS.md)
- **Additional**: [API Overview](01_API_OVERVIEW.md), [Public Endpoints](08_PUBLIC_ENDPOINTS.md)
- **Key Capabilities**: System integration, provisioning, webhooks

### System Monitors
- **Primary Documentation**: [Public Endpoints](08_PUBLIC_ENDPOINTS.md)
- **Additional**: [API Overview](01_API_OVERVIEW.md)
- **Key Capabilities**: Health monitoring, system status, public analytics

---

## 🔧 Common Use Cases

### Getting Started
1. **Obtain Authentication Token**
   ```bash
   curl -X POST https://mail.fayvad.com/fayvad_api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_email", "password": "your_password"}'
   ```

2. **Check Current User**
   ```bash
   curl -X GET https://mail.fayvad.com/fayvad_api/auth/me/ \
     -H "Authorization: Token your_token_here"
   ```

### Organization Management
1. **List Email Accounts**
   ```bash
   curl -X GET https://mail.fayvad.com/fayvad_api/org/email-accounts/ \
     -H "Authorization: Token your_token_here"
   ```

2. **Create Email Account**
   ```bash
   curl -X POST https://mail.fayvad.com/fayvad_api/org/email-accounts/ \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"address": "newuser", "domain": 1, "quota": 1073741824}'
   ```

### Email Operations
1. **List Email Messages**
   ```bash
   curl -X GET "https://mail.fayvad.com/fayvad_api/email/messages/?folder=INBOX" \
     -H "Authorization: Token your_token_here"
   ```

2. **Send Email**
   ```bash
   curl -X POST https://mail.fayvad.com/fayvad_api/email/send/ \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"to": ["recipient@example.com"], "subject": "Test", "body": "Hello"}'
   ```

---

## 📝 Error Handling

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

### Common HTTP Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

---

## 🔒 Security Guidelines

### Authentication
- Always use HTTPS for all requests
- Store tokens securely (environment variables, secure storage)
- Never expose tokens in client-side code
- Rotate tokens regularly

### Data Protection
- Validate all input data
- Implement proper error handling
- Monitor API usage for suspicious activity
- Use appropriate user roles and permissions

### Best Practices
1. Use HTTPS for all requests
2. Implement proper error handling
3. Respect rate limits
4. Validate all input data
5. Use appropriate user roles
6. Monitor API usage

---

## 📊 Rate Limiting

### Limits by Endpoint Category
- **Authentication**: 100 requests per hour
- **System Admin**: 1000 requests per hour
- **Organization Management**: 500 requests per hour
- **Email Operations**: 1000 requests per hour
- **Staff Operations**: 500 requests per hour
- **ERP Integration**: 100 requests per hour
- **Public Endpoints**: 1000 requests per hour

### Rate Limit Headers
```
X-Rate-Limit-Limit: 1000
X-Rate-Limit-Remaining: 999
X-Rate-Limit-Reset: 1640995200
```

---

## 🛠️ SDKs and Tools

### Available SDKs
- **Python**: Django REST Framework client
- **JavaScript**: Axios/Fetch compatible
- **cURL**: All endpoints support cURL requests

### Interactive Documentation
- **Swagger UI**: `GET /docs/`
- **OpenAPI Schema**: `GET /schema/`

---

## 📞 Support

### Getting Help
- **Documentation**: This comprehensive guide
- **Interactive Docs**: [Swagger UI](https://mail.fayvad.com/fayvad_api/docs/)
- **API Schema**: [OpenAPI Schema](https://mail.fayvad.com/fayvad_api/schema/)
- **Support Email**: support@fayvad.com
- **Phone**: +1234567890

### Reporting Issues
When reporting issues, please include:
1. HTTP method and endpoint
2. Request headers and body
3. Response status and body
4. Expected vs actual behavior
5. Steps to reproduce

---

## 📅 Version Information

- **Current Version**: v1.0.0
- **Status**: Production Ready
- **Last Updated**: July 28, 2025
- **API Stability**: Stable (backward compatible)

---

## 🔄 Changelog

### v1.0.0 (July 28, 2025)
- Initial API release
- Complete endpoint coverage
- Comprehensive documentation
- Role-based access control
- ERP integration support

---

*This documentation is maintained by the Fayvad development team. For the latest updates, check the [API Overview](01_API_OVERVIEW.md) or visit our [interactive documentation](https://mail.fayvad.com/fayvad_api/docs/).* 