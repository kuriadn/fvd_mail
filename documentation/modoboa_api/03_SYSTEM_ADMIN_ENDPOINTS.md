# System Administration Endpoints

## Overview
System administration endpoints provide full system management capabilities for superusers. These endpoints handle organization management, user management, domain management, analytics, and system health monitoring.

---

## 🏢 Organization Management

### List Organizations

#### `GET /admin/organizations/`

Retrieves a list of all organizations in the system.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Headers
```
Authorization: Token <your_token>
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `is_active` | boolean | ❌ | Filter by active status |
| `search` | string | ❌ | Search by organization name |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/admin/organizations/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 25,
  "next": "https://mail.fayvad.com/fayvad_api/admin/organizations/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Fayvad Inc",
      "domain_name": "fayvad.com",
      "current_users": 15,
      "storage_usage": {
        "used_mb": 2048,
        "limit_mb": 51200,
        "percentage": 4.0
      },
      "max_users": 50,
      "max_storage_gb": 50,
      "is_active": true,
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### Create Organization

#### `POST /admin/organizations/`

Creates a new organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "string",
  "domain": "integer",
  "max_users": "integer",
  "max_storage_gb": "integer",
  "is_active": "boolean"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `name` | string | ✅ | Max 200 characters |
| `domain` | integer | ✅ | Valid domain ID |
| `max_users` | integer | ❌ | Min 1, default 10 |
| `max_storage_gb` | integer | ❌ | Min 1, default 50 |
| `is_active` | boolean | ❌ | Default true |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corporation",
    "domain": 2,
    "max_users": 100,
    "max_storage_gb": 100,
    "is_active": true
  }'
```

#### Response (201 Created)
```json
{
  "id": 2,
  "name": "Acme Corporation",
  "domain_name": "acme.com",
  "current_users": 0,
  "storage_usage": {
    "used_mb": 0,
    "limit_mb": 102400,
    "percentage": 0.0
  },
  "max_users": 100,
  "max_storage_gb": 100,
  "is_active": true,
  "created_at": "2025-07-28T10:00:00Z"
}
```

### Get Organization

#### `GET /admin/organizations/{id}/`

Retrieves details of a specific organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | ✅ | Organization ID |

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/admin/organizations/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "id": 1,
  "name": "Fayvad Inc",
  "domain_name": "fayvad.com",
  "current_users": 15,
  "storage_usage": {
    "used_mb": 2048,
    "limit_mb": 51200,
    "percentage": 4.0
  },
  "max_users": 50,
  "max_storage_gb": 50,
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Update Organization

#### `PATCH /admin/organizations/{id}/`

Updates an organization's information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Body
```json
{
  "name": "string",
  "max_users": "integer",
  "max_storage_gb": "integer",
  "is_active": "boolean"
}
```

#### Sample Request
```bash
curl -X PATCH https://mail.fayvad.com/fayvad_api/admin/organizations/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "max_users": 75,
    "max_storage_gb": 75
  }'
```

### Delete Organization

#### `DELETE /admin/organizations/{id}/`

Deletes an organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X DELETE https://mail.fayvad.com/fayvad_api/admin/organizations/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (204 No Content)
Organization deleted successfully.

### Activate Organization

#### `POST /admin/organizations/{id}/activate/`

Activates a suspended organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/1/activate/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "detail": "Organization activated successfully.",
  "organization_id": 1
}
```

### Suspend Organization

#### `POST /admin/organizations/{id}/suspend/`

Suspends an organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/1/suspend/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "detail": "Organization suspended successfully.",
  "organization_id": 1
}
```

### Bulk Operations

#### Bulk Suspend Organizations

##### `POST /admin/organizations/bulk-suspend/`

Suspends multiple organizations at once.

#### Request Body
```json
{
  "ids": ["integer"]
}
```

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/bulk-suspend/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "ids": [1, 2, 3]
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Organizations suspended successfully.",
  "suspended_count": 3,
  "organization_ids": [1, 2, 3]
}
```

#### Bulk Activate Organizations

##### `POST /admin/organizations/bulk-activate/`

Activates multiple organizations at once.

#### Request Body
```json
{
  "ids": ["integer"]
}
```

### Update Organization Limits

#### `POST /admin/organizations/{id}/update-limits/`

Updates organization limits.

#### Request Body
```json
{
  "email_limit": "integer",
  "storage_limit": "integer"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `email_limit` | integer | ❌ | Min 1 |
| `storage_limit` | integer | ❌ | Min 1 |

---

## 👥 User Management

### List Users

#### `GET /users/`

Retrieves a list of all users in the system.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `is_active` | boolean | ❌ | Filter by active status |
| `search` | string | ❌ | Search by username or email |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/users/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 50,
  "next": "https://mail.fayvad.com/fayvad_api/users/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin@fayvad.com",
      "email": "admin@fayvad.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "is_staff": true,
      "is_superuser": true,
      "phone_number": "+1234567890",
      "secondary_email": "admin-backup@fayvad.com",
      "tfa_enabled": false,
      "language": "en",
      "business_profile": {
        "organization": "Fayvad Inc",
        "position": "System Administrator",
        "department": "IT"
      },
      "organization": {
        "id": 1,
        "name": "Fayvad Inc",
        "domain_name": "fayvad.com"
      },
      "role": "admin"
    }
  ]
}
```

### Create User

#### `POST /users/`

Creates a new user.

#### Request Body
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "first_name": "string",
  "last_name": "string",
  "is_active": "boolean"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `username` | string | ✅ | Max 150 characters, unique |
| `email` | string | ✅ | Valid email format, unique |
| `password` | string | ✅ | Min 8 characters |
| `first_name` | string | ❌ | Max 30 characters |
| `last_name` | string | ❌ | Max 30 characters |
| `is_active` | boolean | ❌ | Default true |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/users/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe@acme.com",
    "email": "john.doe@acme.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true
  }'
```

#### Response (201 Created)
```json
{
  "id": 2,
  "username": "john.doe@acme.com",
  "email": "john.doe@acme.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "phone_number": null,
  "secondary_email": null,
  "tfa_enabled": false,
  "language": "en",
  "business_profile": null,
  "organization": null,
  "role": "user"
}
```

### Get User

#### `GET /users/{id}/`

Retrieves details of a specific user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin or Self

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/users/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### Update User

#### `PATCH /users/{id}/`

Updates a user's information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin or Self

#### Request Body
```json
{
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "is_active": "boolean"
}
```

### Delete User

#### `DELETE /users/{id}/`

Deletes a user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Bulk Operations

#### Bulk Create Users

##### `POST /users/bulk-create/`

Creates multiple users at once.

#### Request Body
```json
{
  "users": [
    {
      "username": "string",
      "email": "string",
      "password": "string"
    }
  ]
}
```

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/users/bulk-create/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "users": [
      {
        "username": "user1@acme.com",
        "email": "user1@acme.com",
        "password": "password123"
      },
      {
        "username": "user2@acme.com",
        "email": "user2@acme.com",
        "password": "password123"
      }
    ]
  }'
```

#### Response (201 Created)
```json
{
  "detail": "Users created successfully.",
  "created_count": 2,
  "user_ids": [3, 4]
}
```

#### Bulk Deactivate Users

##### `POST /users/bulk-deactivate/`

Deactivates multiple users at once.

#### Request Body
```json
{
  "user_ids": ["integer"]
}
```

### Invite User

#### `POST /users/invite/`

Sends an invitation to create a user account.

#### Request Body
```json
{
  "email": "string",
  "role": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `email` | string | ✅ | Valid email format |
| `role` | string | ❌ | One of: "user", "org_admin", "admin" |

### Reset Password

#### `POST /users/{id}/reset-password/`

Resets a user's password.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Body
```json
{
  "new_password": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `new_password` | string | ✅ | Min 8 characters |

---

## 🌐 Domain Management

### List Domains

#### `GET /domains/`

Retrieves a list of all domains.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `is_active` | boolean | ❌ | Filter by active status |
| `search` | string | ❌ | Search by domain name |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/domains/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "fayvad.com",
      "type": "domain",
      "enabled": true,
      "quota": 0,
      "default_mailbox_quota": 0,
      "message_limit": 0,
      "created": "2025-01-15T10:00:00Z",
      "modified": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### Create Domain

#### `POST /domains/`

Creates a new domain.

#### Request Body
```json
{
  "name": "string",
  "type": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `name` | string | ✅ | Valid domain format |
| `type` | string | ❌ | One of: "domain", "relaydomain" |

### Get Domain

#### `GET /domains/{id}/`

Retrieves details of a specific domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Update Domain

#### `PATCH /domains/{id}/`

Updates a domain's information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Delete Domain

#### `DELETE /domains/{id}/`

Deletes a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Domain Operations

#### Enable Domain

##### `POST /domains/{id}/enable/`

Enables a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/domains/1/enable/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "detail": "Domain enabled successfully.",
  "domain_id": 1
}
```

#### Disable Domain

##### `POST /domains/{id}/disable/`

Disables a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### DNS Management

#### Check Domain DNS

##### `GET /domains/{id}/dns-check/`

Checks the DNS configuration for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/domains/1/dns-check/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "domain": "fayvad.com",
  "mx_records": [
    {
      "record": "mail.fayvad.com",
      "priority": 10,
      "status": "valid"
    }
  ],
  "spf_record": {
    "record": "v=spf1 include:mail.fayvad.com ~all",
    "status": "valid"
  },
  "dkim_record": {
    "record": "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...",
    "status": "valid"
  },
  "dmarc_record": {
    "record": "v=DMARC1; p=quarantine; rua=mailto:dmarc@fayvad.com",
    "status": "valid"
  }
}
```

#### Verify Domain DNS

##### `POST /domains/{id}/verify-dns/`

Verifies the DNS configuration for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### DNS Record Generation

#### Generate SPF Record

##### `POST /domains/{id}/generate-spf/`

Generates an SPF record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/domains/1/generate-spf/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "domain": "fayvad.com",
  "spf_record": "v=spf1 include:mail.fayvad.com ~all",
  "instructions": "Add this TXT record to your DNS configuration"
}
```

#### Generate DKIM Record

##### `POST /domains/{id}/generate-dkim/`

Generates a DKIM record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Generate DMARC Record

##### `POST /domains/{id}/generate-dmarc/`

Generates a DMARC record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### DNS Record Verification

#### Verify SPF Record

##### `POST /domains/{id}/verify-spf/`

Verifies the SPF record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Verify DKIM Record

##### `POST /domains/{id}/verify-dkim/`

Verifies the DKIM record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Verify DMARC Record

##### `POST /domains/{id}/verify-dmarc/`

Verifies the DMARC record for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Get Domain Mailboxes

#### `GET /domains/{id}/mailboxes/`

Retrieves all mailboxes for a domain.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/domains/1/mailboxes/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "domain": "fayvad.com",
  "mailboxes": [
    {
      "id": 1,
      "address": "admin",
      "email": "admin@fayvad.com",
      "quota": 1073741824,
      "usage_mb": 2048
    }
  ],
  "total_count": 1
}
```

---

## 📊 Analytics & Reporting

### Revenue Analytics

#### `GET /admin/analytics/revenue/`

Retrieves revenue analytics data.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start_date` | string | ❌ | Start date (YYYY-MM-DD) |
| `end_date` | string | ❌ | End date (YYYY-MM-DD) |
| `period` | string | ❌ | Period: "daily", "weekly", "monthly" |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/admin/analytics/revenue/?start_date=2025-01-01&end_date=2025-07-28" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "period": "monthly",
  "start_date": "2025-01-01",
  "end_date": "2025-07-28",
  "data": [
    {
      "month": "2025-01",
      "revenue": 15000.00,
      "new_subscriptions": 5,
      "cancellations": 1,
      "churn_rate": 0.2
    }
  ],
  "summary": {
    "total_revenue": 105000.00,
    "total_subscriptions": 35,
    "average_revenue_per_subscription": 3000.00
  }
}
```

### Usage Analytics

#### `GET /admin/analytics/usage/`

Retrieves usage analytics data.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/admin/analytics/usage/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "storage_usage": {
    "total_used_gb": 150.5,
    "total_limit_gb": 1000.0,
    "percentage": 15.05
  },
  "email_usage": {
    "total_accounts": 150,
    "active_accounts": 142,
    "inactive_accounts": 8
  },
  "organizations": {
    "total": 25,
    "active": 23,
    "suspended": 2
  }
}
```

### Client Analytics

#### `GET /admin/analytics/clients/`

Retrieves client analytics data.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Intelligence Reports

#### `GET /admin/reports/intelligence/`

Retrieves intelligence reports.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### System Health Reports

#### `GET /admin/reports/system-health/`

Retrieves system health reports.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

---

## 🏥 Health & Monitoring

### Detailed System Health

#### `GET /admin/health/`

Retrieves detailed system health information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/admin/health/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-07-28T10:00:00Z",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 15,
      "connections": 5
    },
    "storage": {
      "status": "healthy",
      "available_gb": 850.5,
      "used_gb": 149.5
    },
    "email_delivery": {
      "status": "healthy",
      "queue_size": 0,
      "delivery_rate": 99.9
    },
    "modoboa": {
      "status": "healthy",
      "version": "2.0.0",
      "uptime_hours": 720
    }
  },
  "alerts": []
}
```

### System Alerts

#### `GET /admin/health/alerts/`

Retrieves system alerts.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### System Logs

#### `GET /admin/health/logs/`

Retrieves system logs.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `level` | string | ❌ | Log level: "DEBUG", "INFO", "WARNING", "ERROR" |
| `start_date` | string | ❌ | Start date (YYYY-MM-DD) |
| `end_date` | string | ❌ | End date (YYYY-MM-DD) |
| `limit` | integer | ❌ | Number of log entries (default: 100, max: 1000) |

### Component Health Checks

#### Modoboa Health

##### `GET /admin/health/modoboa/`

Checks Modoboa service health.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Database Health

##### `GET /admin/health/database/`

Checks database health.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Storage Health

##### `GET /admin/health/storage/`

Checks storage health.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Email Delivery Health

##### `GET /admin/health/email-delivery/`

Checks email delivery health.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### Configure Notifications

#### `GET /admin/health/notifications/`

Retrieves notification configuration.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### `POST /admin/health/notifications/`

Updates notification configuration.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Body
```json
{
  "email_alerts": "boolean",
  "webhook_url": "string",
  "alert_levels": ["string"]
}
```

---

## 📈 Usage & Statistics

### System Email Usage

#### `GET /admin/email-usage/`

Retrieves system-wide email usage statistics.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/admin/email-usage/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "total_accounts": 150,
  "active_accounts": 142,
  "inactive_accounts": 8,
  "storage_usage": {
    "total_used_gb": 150.5,
    "total_limit_gb": 1000.0,
    "percentage": 15.05
  },
  "organizations": {
    "total": 25,
    "active": 23,
    "suspended": 2
  }
}
```

### System Storage Usage

#### `GET /admin/storage-usage/`

Retrieves system-wide storage usage statistics.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

### All Email Accounts

#### `GET /admin/email-accounts/`

Retrieves all email accounts in the system.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `organization` | integer | ❌ | Filter by organization ID |
| `domain` | integer | ❌ | Filter by domain ID |
| `is_active` | boolean | ❌ | Filter by active status |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/admin/email-accounts/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 150,
  "next": "https://mail.fayvad.com/fayvad_api/admin/email-accounts/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@fayvad.com",
      "first_name": "Admin",
      "last_name": "User",
      "usage_mb": 2048,
      "quota": 1073741824,
      "organization": {
        "id": 1,
        "name": "Fayvad Inc"
      },
      "domain": {
        "id": 1,
        "name": "fayvad.com"
      }
    }
  ]
}
```

### Admin Reset Password

#### `POST /admin/email-accounts/{id}/reset-password/`

Resets an email account password.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin

#### Request Body
```json
{
  "new_password": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `new_password` | string | ✅ | Min 8 characters |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/email-accounts/1/reset-password/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "newsecurepassword123"
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Password reset successfully.",
  "email_account_id": 1
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `ORGANIZATION_NOT_FOUND` | 404 | Organization not found |
| `USER_NOT_FOUND` | 404 | User not found |
| `DOMAIN_NOT_FOUND` | 404 | Domain not found |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `ORGANIZATION_ALREADY_EXISTS` | 400 | Organization with same domain exists |
| `USER_ALREADY_EXISTS` | 400 | User with same username/email exists |
| `DOMAIN_ALREADY_EXISTS` | 400 | Domain already exists |
| `QUOTA_EXCEEDED` | 400 | Organization limits exceeded |
| `DNS_VERIFICATION_FAILED` | 400 | Domain DNS verification failed |
| `BULK_OPERATION_FAILED` | 400 | Bulk operation failed |

---

*This document covers all system administration endpoints. For organization-specific endpoints, see the Organization Management documentation.* 