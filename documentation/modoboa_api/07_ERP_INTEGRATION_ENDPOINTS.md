# ERP Integration Endpoints

## Overview
ERP integration endpoints provide functionality for integrating with external ERP systems, handling usage summaries, provisioning, and billing webhooks. These endpoints are designed for system-to-system communication.

---

## 📊 Usage Summary

### Usage Summary

#### `GET /erp/usage-summary/`

Retrieves a comprehensive usage summary for ERP integration.

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
| `organization_id` | integer | ❌ | Specific organization ID |
| `start_date` | string | ❌ | Start date (YYYY-MM-DD) |
| `end_date` | string | ❌ | End date (YYYY-MM-DD) |
| `include_details` | boolean | ❌ | Include detailed breakdown |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/erp/usage-summary/?start_date=2025-07-01&end_date=2025-07-31" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "period": {
    "start_date": "2025-07-01",
    "end_date": "2025-07-31"
  },
  "summary": {
    "total_organizations": 25,
    "active_organizations": 23,
    "suspended_organizations": 2,
    "total_users": 150,
    "active_users": 142,
    "total_storage_gb": 150.5,
    "total_revenue": 2500.00
  },
  "organizations": [
    {
      "id": 1,
      "name": "Fayvad Inc",
      "odoo_customer_id": 12345,
      "users": {
        "total": 15,
        "active": 14,
        "inactive": 1
      },
      "storage": {
        "used_gb": 2.5,
        "limit_gb": 50.0,
        "percentage": 5.0
      },
      "subscription": {
        "plan_name": "Business Pro",
        "amount": 99.99,
        "status": "active"
      }
    }
  ],
  "billing_events": [
    {
      "id": 1,
      "organization_id": 1,
      "event_type": "user_added",
      "event_date": "2025-07-15",
      "quantity": 1,
      "unit_price": 5.00,
      "description": "Additional user added",
      "odoo_synced": true
    }
  ]
}
```

---

## 🏢 Provisioning

### Provision Organization

#### `POST /erp/provision/organization/`

Provisions a new organization from ERP system.

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
  "organization_data": {
    "name": "string",
    "domain": "string",
    "odoo_customer_id": "integer",
    "max_users": "integer",
    "max_storage_gb": "integer",
    "plan_id": "integer",
    "contact_info": {
      "primary_email": "string",
      "phone": "string",
      "address": "string"
    }
  }
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `name` | string | ✅ | Max 200 characters |
| `domain` | string | ✅ | Valid domain format |
| `odoo_customer_id` | integer | ✅ | Unique Odoo customer ID |
| `max_users` | integer | ❌ | Min 1, default 10 |
| `max_storage_gb` | integer | ❌ | Min 1, default 50 |
| `plan_id` | integer | ❌ | Valid subscription plan ID |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/erp/provision/organization/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_data": {
      "name": "Acme Corporation",
      "domain": "acme.com",
      "odoo_customer_id": 67890,
      "max_users": 100,
      "max_storage_gb": 100,
      "plan_id": 2,
      "contact_info": {
        "primary_email": "admin@acme.com",
        "phone": "+1234567890",
        "address": "123 Business St, City, State 12345"
      }
    }
  }'
```

#### Response (201 Created)
```json
{
  "provisioned": true,
  "organization": {
    "id": 2,
    "name": "Acme Corporation",
    "domain_name": "acme.com",
    "odoo_customer_id": 67890,
    "max_users": 100,
    "max_storage_gb": 100,
    "is_active": true,
    "created_at": "2025-07-28T10:00:00Z"
  },
  "subscription": {
    "id": 2,
    "plan_name": "Business Pro",
    "status": "active",
    "amount": 99.99
  },
  "provisioning_details": {
    "domain_created": true,
    "dns_records_generated": true,
    "initial_admin_created": true
  }
}
```

### Provision Email Account

#### `POST /erp/provision/email-account/`

Provisions a new email account from ERP system.

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
  "email_account_data": {
    "organization_id": "integer",
    "address": "string",
    "domain": "integer",
    "quota": "integer",
    "user_info": {
      "first_name": "string",
      "last_name": "string",
      "password": "string"
    }
  }
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `organization_id` | integer | ✅ | Valid organization ID |
| `address` | string | ✅ | Valid email local part |
| `domain` | integer | ✅ | Valid domain ID for organization |
| `quota` | integer | ❌ | Min 1MB, default organization default |
| `first_name` | string | ❌ | Max 30 characters |
| `last_name` | string | ❌ | Max 30 characters |
| `password` | string | ❌ | Min 8 characters |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/erp/provision/email-account/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "email_account_data": {
      "organization_id": 2,
      "address": "john.doe",
      "domain": 2,
      "quota": 1073741824,
      "user_info": {
        "first_name": "John",
        "last_name": "Doe",
        "password": "securepassword123"
      }
    }
  }'
```

#### Response (201 Created)
```json
{
  "provisioned": true,
  "email_account": {
    "id": 3,
    "email": "john.doe@acme.com",
    "first_name": "John",
    "last_name": "Doe",
    "quota": 1073741824,
    "organization_id": 2
  },
  "provisioning_details": {
    "mailbox_created": true,
    "user_profile_created": true,
    "quota_set": true
  }
}
```

---

## 💳 Billing Webhooks

### Billing Webhook

#### `POST /erp/webhooks/billing/`

Receives billing webhooks from ERP system.

#### Authentication
- **Required**: ✅ Webhook signature
- **Permission Level**: Webhook

#### Request Headers
```
Content-Type: application/json
X-Webhook-Signature: <signature>
```

#### Request Body
```json
{
  "event_type": "string",
  "organization_id": "integer",
  "billing_data": {
    "amount": "decimal",
    "currency": "string",
    "description": "string",
    "invoice_id": "string"
  },
  "timestamp": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `event_type` | string | ✅ | One of: "subscription_created", "subscription_updated", "subscription_cancelled", "payment_received", "payment_failed" |
| `organization_id` | integer | ✅ | Valid organization ID |
| `amount` | decimal | ❌ | Positive decimal value |
| `currency` | string | ❌ | ISO 4217 currency code |
| `description` | string | ❌ | Max 500 characters |
| `invoice_id` | string | ❌ | Unique invoice identifier |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/erp/webhooks/billing/ \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: sha256=abc123..." \
  -d '{
    "event_type": "payment_received",
    "organization_id": 2,
    "billing_data": {
      "amount": 99.99,
      "currency": "USD",
      "description": "Monthly subscription payment",
      "invoice_id": "INV-2025-001"
    },
    "timestamp": "2025-07-28T10:00:00Z"
  }'
```

#### Response (200 OK)
```json
{
  "processed": true,
  "webhook_id": "webhook_12345",
  "organization_id": 2,
  "event_type": "payment_received",
  "processed_at": "2025-07-28T10:00:01Z"
}
```

#### Response (400 Bad Request)
```json
{
  "processed": false,
  "error": "Invalid webhook signature",
  "error_code": "INVALID_SIGNATURE"
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `ORGANIZATION_NOT_FOUND` | 404 | Organization not found |
| `DOMAIN_NOT_FOUND` | 404 | Domain not found |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `ORGANIZATION_ALREADY_EXISTS` | 400 | Organization with same domain exists |
| `ODOO_CUSTOMER_ID_EXISTS` | 400 | Odoo customer ID already exists |
| `EMAIL_ACCOUNT_ALREADY_EXISTS` | 400 | Email account already exists |
| `PROVISIONING_FAILED` | 500 | Organization/account provisioning failed |
| `INVALID_WEBHOOK_SIGNATURE` | 400 | Invalid webhook signature |
| `WEBHOOK_PROCESSING_FAILED` | 500 | Webhook processing failed |

---

## 🔒 Security Considerations

### Webhook Security
- All webhooks require signature verification
- Webhook signatures use HMAC-SHA256
- Webhook URLs are unique per organization
- Failed webhook attempts are logged

### Data Validation
- All ERP data is validated before processing
- Organization provisioning includes domain verification
- Email account provisioning enforces quota limits

### Best Practices
1. Use HTTPS for all webhook communications
2. Implement proper signature verification
3. Handle webhook failures gracefully
4. Monitor provisioning success rates
5. Keep ERP data synchronized

---

## 🔄 Data Synchronization

### Billing Events
- Billing events are automatically synced to ERP
- Failed syncs are retried with exponential backoff
- Sync status is tracked and reported

### Organization Data
- Organization changes are synced to ERP
- User count changes trigger billing events
- Storage usage is reported periodically

---

*This document covers all ERP integration endpoints. For other endpoint categories, see the respective documentation files.* 