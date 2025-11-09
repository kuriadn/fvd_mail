# Public Endpoints

## Overview
Public endpoints provide access to system health checks, API documentation, and other publicly accessible information. These endpoints do not require authentication and are designed for monitoring and documentation purposes.

---

## 🏥 Health Checks

### Public Health Check

#### `GET /health/`

Provides a basic health check for the system.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/health/
```

#### Response (200 OK)
```json
{
  "status": "ok",
  "timestamp": "2025-07-28T10:00:00Z",
  "version": "1.0.0",
  "public_health": "ok",
  "uptime_seconds": 2592000
}
```

#### Response (503 Service Unavailable)
```json
{
  "status": "error",
  "timestamp": "2025-07-28T10:00:00Z",
  "version": "1.0.0",
  "public_health": "error",
  "error": "Database connection failed"
}
```

---

## 📚 API Documentation

### Get API Schema

#### `GET /schema/`

Retrieves the OpenAPI schema for the API.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/schema/
```

#### Response (200 OK)
```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "Fayvad Email Platform API",
    "version": "1.0.0",
    "description": "API for managing email services and organizations"
  },
  "servers": [
    {
      "url": "https://mail.fayvad.com/fayvad_api/",
      "description": "Production server"
    }
  ],
  "paths": {
    "/auth/login/": {
      "post": {
        "summary": "Login",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "username": {
                    "type": "string"
                  },
                  "password": {
                    "type": "string"
                  }
                }
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Login successful"
          }
        }
      }
    }
  },
  "components": {
    "securitySchemes": {
      "TokenAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
      }
    }
  }
}
```

### API Documentation UI

#### `GET /docs/`

Provides access to the interactive Swagger UI documentation.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/docs/
```

#### Response (200 OK)
HTML page with Swagger UI interface for interactive API documentation.

---

## 📊 System Status

### System Status

#### `GET /status/`

Provides detailed system status information.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/status/
```

#### Response (200 OK)
```json
{
  "status": "operational",
  "timestamp": "2025-07-28T10:00:00Z",
  "version": "1.0.0",
  "environment": "production",
  "components": {
    "api": {
      "status": "operational",
      "response_time_ms": 15
    },
    "database": {
      "status": "operational",
      "response_time_ms": 25
    },
    "email_delivery": {
      "status": "operational",
      "queue_size": 0
    },
    "storage": {
      "status": "operational",
      "available_gb": 850.5
    }
  },
  "maintenance": {
    "scheduled": false,
    "next_maintenance": null
  },
  "incidents": []
}
```

---

## 🔧 System Information

### System Information

#### `GET /info/`

Provides general system information.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/info/
```

#### Response (200 OK)
```json
{
  "name": "Fayvad Email Platform",
  "version": "1.0.0",
  "description": "Enterprise email hosting and management platform",
  "contact": {
    "email": "support@fayvad.com",
    "phone": "+1234567890",
    "website": "https://fayvad.com"
  },
  "features": [
    "Email hosting",
    "Organization management",
    "Domain management",
    "Analytics and reporting",
    "API access"
  ],
  "supported_protocols": [
    "SMTP",
    "IMAP",
    "POP3",
    "REST API"
  ],
  "data_centers": [
    {
      "location": "US East",
      "status": "operational"
    },
    {
      "location": "US West",
      "status": "operational"
    }
  ]
}
```

---

## 📈 Public Analytics

### Public Analytics

#### `GET /analytics/public/`

Provides public analytics data.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | ❌ | Period: "daily", "weekly", "monthly" (default: "monthly") |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/analytics/public/?period=monthly"
```

#### Response (200 OK)
```json
{
  "period": "monthly",
  "timestamp": "2025-07-28T10:00:00Z",
  "metrics": {
    "total_organizations": 25,
    "total_users": 150,
    "total_emails_sent": 50000,
    "total_storage_gb": 150.5,
    "uptime_percentage": 99.9
  },
  "growth": {
    "organizations_growth": 0.15,
    "users_growth": 0.12,
    "emails_growth": 0.08
  },
  "performance": {
    "average_response_time_ms": 25,
    "email_delivery_rate": 99.8,
    "customer_satisfaction": 4.8
  }
}
```

---

## 🔒 Security Information

### Security Information

#### `GET /security/`

Provides security-related information and policies.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/security/
```

#### Response (200 OK)
```json
{
  "security_practices": {
    "encryption": {
      "in_transit": "TLS 1.3",
      "at_rest": "AES-256",
      "email_content": "End-to-end encryption available"
    },
    "authentication": {
      "methods": ["Token-based", "OAuth 2.0", "Two-factor authentication"],
      "password_policy": "Minimum 8 characters, complexity requirements"
    },
    "compliance": {
      "gdpr": true,
      "sox": true,
      "hipaa": false,
      "iso27001": true
    }
  },
  "privacy": {
    "data_retention": "30 days for logs, indefinite for user data",
    "data_processing": "EU-based data centers",
    "third_party_sharing": "None without explicit consent"
  },
  "incident_response": {
    "contact": "security@fayvad.com",
    "response_time": "4 hours",
    "disclosure_policy": "72 hours for confirmed breaches"
  }
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `MAINTENANCE_MODE` | 503 | System under maintenance |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_REQUEST` | 400 | Invalid request format |

---

## 🔒 Security Considerations

### Public Access
- These endpoints are designed for public access
- No sensitive information is exposed
- Rate limiting is applied to prevent abuse
- Health checks are monitored for security

### Data Privacy
- Only non-sensitive system information is exposed
- No user data is accessible through public endpoints
- Analytics data is aggregated and anonymized

### Best Practices
1. Use these endpoints for monitoring and documentation
2. Implement proper error handling for health checks
3. Monitor public endpoint usage for security
4. Keep documentation up to date

---

## 📊 Rate Limiting

### Public Endpoints Limits
- **Health checks**: 100 requests per minute
- **Documentation**: 1000 requests per hour
- **Analytics**: 100 requests per hour

### Rate Limit Headers
```
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1640995200
```

---

*This document covers all public endpoints. For authenticated endpoints, see the respective documentation files.* 