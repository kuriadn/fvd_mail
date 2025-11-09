# Organization Management Endpoints

## Overview
Organization management endpoints allow organization administrators to manage their organization's email accounts, view usage statistics, manage subscriptions, and handle organization-specific operations.

---

## 📧 Email Account Management

### List Email Accounts

#### `GET /org/email-accounts/`

Retrieves a list of email accounts for the current organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

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
| `search` | string | ❌ | Search by email address |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/org/email-accounts/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "email": "admin@fayvad.com",
      "first_name": "Admin",
      "last_name": "User",
      "usage_mb": 2048,
      "quota": 1073741824
    },
    {
      "id": 2,
      "email": "john.doe@fayvad.com",
      "first_name": "John",
      "last_name": "Doe",
      "usage_mb": 512,
      "quota": 1073741824
    }
  ]
}
```

### Create Email Account

#### `POST /org/email-accounts/`

Creates a new email account for the organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "address": "string",
  "domain": "integer",
  "quota": "integer"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `address` | string | ✅ | Valid email local part, max 254 characters |
| `domain` | integer | ✅ | Valid domain ID for organization |
| `quota` | integer | ❌ | Min 1MB, default organization default |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/org/email-accounts/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "jane.smith",
    "domain": 1,
    "quota": 1073741824
  }'
```

#### Response (201 Created)
```json
{
  "id": 3,
  "email": "jane.smith@fayvad.com",
  "first_name": "",
  "last_name": "",
  "usage_mb": 0,
  "quota": 1073741824
}
```

### Get Email Account

#### `GET /org/email-accounts/{id}/`

Retrieves details of a specific email account.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Path Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | ✅ | Email account ID |

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/email-accounts/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "id": 1,
  "email": "admin@fayvad.com",
  "first_name": "Admin",
  "last_name": "User",
  "usage_mb": 2048,
  "quota": 1073741824
}
```

### Update Email Account

#### `PATCH /org/email-accounts/{id}/`

Updates an email account's information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Request Body
```json
{
  "quota": "integer"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `quota` | integer | ❌ | Min 1MB, max organization limit |

#### Sample Request
```bash
curl -X PATCH https://mail.fayvad.com/fayvad_api/org/email-accounts/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "quota": 2147483648
  }'
```

### Delete Email Account

#### `DELETE /org/email-accounts/{id}/`

Deletes an email account.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X DELETE https://mail.fayvad.com/fayvad_api/org/email-accounts/1/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (204 No Content)
Email account deleted successfully.

### Reset Email Account Password

#### `POST /org/email-accounts/{id}/reset-password/`

Resets an email account password.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

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
curl -X POST https://mail.fayvad.com/fayvad_api/org/email-accounts/1/reset-password/ \
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

### Bulk Operations

#### Bulk Create Email Accounts

##### `POST /org/email-accounts/bulk-create/`

Creates multiple email accounts at once.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Request Body
```json
{
  "accounts": [
    {
      "address": "string",
      "quota": "integer"
    }
  ]
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `accounts` | array | ✅ | Array of account objects |
| `address` | string | ✅ | Valid email local part |
| `quota` | integer | ❌ | Min 1MB, default organization default |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/org/email-accounts/bulk-create/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "accounts": [
      {
        "address": "user1",
        "quota": 1073741824
      },
      {
        "address": "user2",
        "quota": 1073741824
      }
    ]
  }'
```

#### Response (201 Created)
```json
{
  "detail": "Email accounts created successfully.",
  "created_count": 2,
  "account_ids": [4, 5]
}
```

#### Bulk Deactivate Email Accounts

##### `POST /org/email-accounts/bulk-deactivate/`

Deactivates multiple email accounts at once.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Request Body
```json
{
  "account_ids": ["integer"]
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `account_ids` | array | ✅ | Array of valid account IDs |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/org/email-accounts/bulk-deactivate/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "account_ids": [1, 2, 3]
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Email accounts deactivated successfully.",
  "deactivated_count": 3,
  "account_ids": [1, 2, 3]
}
```

---

## 📊 Organization Limits & Usage

### Organization Limits

#### `GET /org/limits/`

Retrieves the current organization's limits and usage.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/limits/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "domain_name": "fayvad.com"
  },
  "limits": {
    "max_users": 50,
    "max_storage_gb": 50,
    "current_users": 15,
    "current_storage_gb": 2.5
  },
  "usage": {
    "user_percentage": 30.0,
    "storage_percentage": 5.0,
    "remaining_users": 35,
    "remaining_storage_gb": 47.5
  }
}
```

### Organization Dashboard

#### `GET /org/dashboard/`

Retrieves organization dashboard data.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/dashboard/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "domain_name": "fayvad.com",
    "is_active": true
  },
  "stats": {
    "total_accounts": 15,
    "active_accounts": 14,
    "inactive_accounts": 1,
    "total_storage_mb": 2560,
    "average_storage_per_account": 170.67
  },
  "recent_activity": [
    {
      "type": "account_created",
      "email": "newuser@fayvad.com",
      "timestamp": "2025-07-28T09:30:00Z"
    },
    {
      "type": "password_reset",
      "email": "admin@fayvad.com",
      "timestamp": "2025-07-28T08:15:00Z"
    }
  ]
}
```

### Organization Quota Usage

#### `GET /org/usage/quotas/`

Retrieves detailed quota usage information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/usage/quotas/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "storage_usage": {
    "total_used_mb": 2560,
    "total_limit_mb": 51200,
    "percentage": 5.0,
    "accounts_over_quota": 0
  },
  "account_usage": [
    {
      "email": "admin@fayvad.com",
      "used_mb": 2048,
      "quota_mb": 1024,
      "percentage": 200.0,
      "over_quota": true
    },
    {
      "email": "john.doe@fayvad.com",
      "used_mb": 512,
      "quota_mb": 1024,
      "percentage": 50.0,
      "over_quota": false
    }
  ]
}
```

### Organization Email Stats

#### `GET /org/usage/email-stats/`

Retrieves email statistics for the organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/usage/email-stats/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "period": "last_30_days",
  "stats": {
    "total_emails_sent": 1250,
    "total_emails_received": 3420,
    "average_emails_per_day": 41.67,
    "spam_emails": 45,
    "bounced_emails": 12
  },
  "top_senders": [
    {
      "email": "admin@fayvad.com",
      "count": 450
    },
    {
      "email": "john.doe@fayvad.com",
      "count": 320
    }
  ],
  "top_recipients": [
    {
      "email": "admin@fayvad.com",
      "count": 1200
    },
    {
      "email": "support@fayvad.com",
      "count": 890
    }
  ]
}
```

---

## 💳 Subscription Management

### Organization Subscription

#### `GET /org/subscription/`

Retrieves the current organization's subscription information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/subscription/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "subscription": {
    "id": 1,
    "plan_name": "Business Pro",
    "plan_id": 2,
    "status": "active",
    "current_period_start": "2025-07-01T00:00:00Z",
    "current_period_end": "2025-08-01T00:00:00Z",
    "amount": 99.99,
    "currency": "USD",
    "billing_cycle": "monthly"
  },
  "features": {
    "max_users": 50,
    "max_storage_gb": 50,
    "advanced_security": true,
    "priority_support": true,
    "api_access": true
  },
  "next_billing": {
    "date": "2025-08-01T00:00:00Z",
    "amount": 99.99
  }
}
```

### Organization Subscription History

#### `GET /org/subscription/history/`

Retrieves the organization's subscription history.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/org/subscription/history/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 12,
      "plan_name": "Business Pro",
      "amount": 99.99,
      "currency": "USD",
      "billing_date": "2025-07-01T00:00:00Z",
      "status": "paid",
      "invoice_url": "https://billing.fayvad.com/invoice/12345"
    },
    {
      "id": 11,
      "plan_name": "Business Starter",
      "amount": 49.99,
      "currency": "USD",
      "billing_date": "2025-06-01T00:00:00Z",
      "status": "paid",
      "invoice_url": "https://billing.fayvad.com/invoice/12344"
    }
  ]
}
```

---

## 🏢 Organization Profile

### Organization Profile

#### `GET /org/profile/`

Retrieves the organization's profile information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/org/profile/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "domain_name": "fayvad.com",
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z"
  },
  "contact_info": {
    "primary_email": "admin@fayvad.com",
    "phone": "+1234567890",
    "address": "123 Business St, City, State 12345"
  },
  "settings": {
    "timezone": "America/New_York",
    "language": "en",
    "date_format": "MM/DD/YYYY"
  }
}
```

---

## 👥 Organization Users

### Organization Users

#### `GET /org/users/`

Retrieves a list of users in the organization.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Org Admin

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `is_active` | boolean | ❌ | Filter by active status |
| `search` | string | ❌ | Search by name or email |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/org/users/?page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin@fayvad.com",
      "email": "admin@fayvad.com",
      "first_name": "Admin",
      "last_name": "User",
      "is_active": true,
      "role": "org_admin",
      "last_login": "2025-07-28T09:00:00Z"
    },
    {
      "id": 2,
      "username": "john.doe@fayvad.com",
      "email": "john.doe@fayvad.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "role": "user",
      "last_login": "2025-07-27T15:30:00Z"
    }
  ]
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `ORGANIZATION_NOT_FOUND` | 404 | Organization not found |
| `EMAIL_ACCOUNT_NOT_FOUND` | 404 | Email account not found |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `EMAIL_ACCOUNT_ALREADY_EXISTS` | 400 | Email account already exists |
| `QUOTA_EXCEEDED` | 400 | Organization limits exceeded |
| `DOMAIN_NOT_ACCESSIBLE` | 403 | Domain not accessible to organization |
| `BULK_OPERATION_FAILED` | 400 | Bulk operation failed |
| `SUBSCRIPTION_REQUIRED` | 402 | Subscription required for operation |
| `ACCOUNT_LIMIT_REACHED` | 400 | Maximum number of accounts reached |

---

## 🔒 Security Considerations

### Organization Isolation
- Organization admins can only access their own organization's data
- Email accounts are scoped to the organization's domains
- Usage statistics are isolated per organization

### Data Validation
- All email addresses must belong to the organization's domains
- Quota limits are enforced at the organization level
- Bulk operations are rate-limited to prevent abuse

### Best Practices
1. Regularly monitor usage and quotas
2. Implement proper password policies
3. Use bulk operations for efficiency
4. Monitor account activity
5. Keep subscription information up to date

---

*This document covers all organization management endpoints. For system administration endpoints, see the System Administration documentation.* 