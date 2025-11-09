# Email Features API - Frontend Integration Guide

This document provides the API endpoints and integration patterns for the email features implemented in the Fayvad platform.

## Base URL
```
https://mail.fayvad.com/fayvad_api/
```

## Authentication
All endpoints require authentication using the Authorization header:
```
Authorization: Token <your_token>
```

---

## 1. API Key Management

### List User's API Keys
```http
GET /api-keys/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Production API Key",
    "created": "2024-01-15T10:30:00Z",
    "expires": "2024-12-31T23:59:59Z",
    "is_active": true
  }
]
```

### Create New API Key
```http
POST /api-keys/
```

**Request Body:**
```json
{
  "name": "New API Key",
  "expires": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New API Key",
  "key": "fayvad_abc123def456...",  // Only shown once
  "created": "2024-01-15T10:30:00Z",
  "expires": "2024-12-31T23:59:59Z",
  "is_active": true
}
```

### Update API Key
```http
PATCH /api-keys/{id}/
```

**Request Body:**
```json
{
  "name": "Updated API Key Name",
  "expires": "2025-12-31T23:59:59Z"
}
```

### Delete API Key
```http
DELETE /api-keys/{id}/
```

### Regenerate API Key
```http
POST /api-keys/{id}/regenerate/
```

**Response:**
```json
{
  "id": 1,
  "name": "Production API Key",
  "key": "fayvad_new123def456...",  // Only shown once
  "created": "2024-01-15T10:30:00Z",
  "expires": "2024-12-31T23:59:59Z"
}
```

---

## 2. Email Signatures

### Get User's Email Signature
```http
GET /email-features/signatures/
```

**Response:**
```json
{
  "id": 1,
  "text_signature": "Best regards,\nJohn Doe\nSoftware Engineer",
  "html_signature": "<p>Best regards,<br>John Doe<br>Software Engineer</p>",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Create/Update Email Signature
```http
POST /email-features/signatures/
```

**Request Body:**
```json
{
  "text_signature": "Best regards,\nJohn Doe\nSoftware Engineer",
  "html_signature": "<p>Best regards,<br>John Doe<br>Software Engineer</p>",
  "is_active": true
}
```

**Response:** Same as GET response

### Update Email Signature (Partial)
```http
PATCH /email-features/signatures/{id}/
```

**Request Body:**
```json
{
  "is_active": false
}
```

### Delete Email Signature
```http
DELETE /email-features/signatures/{id}/
```

---

## 3. Contact Management

### List Contacts
```http
GET /email-features/contacts/
```

**Query Parameters:**
- `search` (optional): Search by name or email
- `page` (optional): Page number
- `page_size` (optional): Items per page (default: 10)

**Response:**
```json
{
  "count": 25,
  "next": "https://mail.fayvad.com/fayvad_api/email-features/contacts/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1234567890",
      "company": "Tech Corp",
      "job_title": "Software Engineer",
      "notes": "Met at conference",
      "is_active": true,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Create Contact
```http
POST /email-features/contacts/
```

**Request Body:**
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane.smith@example.com",
  "phone": "+1234567891",
  "company": "Design Studio",
  "job_title": "UX Designer",
  "notes": "Colleague from previous job"
}
```

**Required Fields:** `first_name`, `last_name`, `email`

### Get Contact
```http
GET /email-features/contacts/{id}/
```

### Update Contact
```http
PATCH /email-features/contacts/{id}/
```

### Delete Contact
```http
DELETE /email-features/contacts/{id}/
```

### Import Contacts from CSV
```http
POST /email-features/contacts/import-csv/
```

**Request:** Multipart form data with CSV file

**CSV Format:**
```csv
first_name,last_name,email,phone,company,job_title,notes
John,Doe,john.doe@example.com,+1234567890,Tech Corp,Software Engineer,Met at conference
Jane,Smith,jane.smith@example.com,+1234567891,Design Studio,UX Designer,Colleague
```

**Response:**
```json
{
  "imported_count": 2,
  "errors": []
}
```

### Export Contacts to CSV
```http
GET /email-features/contacts/export-csv/
```

**Response:** CSV file download

---

## 4. Email Forwarding

### List Forwarding Rules
```http
GET /email-features/forwarding/
```

**Response:**
```json
[
  {
    "id": 1,
    "source_email": "john@company.com",
    "destination_email": "john.personal@gmail.com",
    "is_active": true,
    "keep_copy": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### Create Forwarding Rule
```http
POST /email-features/forwarding/
```

**Request Body:**
```json
{
  "source_email": "john@company.com",
  "destination_email": "john.personal@gmail.com",
  "is_active": true,
  "keep_copy": true
}
```

**Required Fields:** `source_email`, `destination_email`

### Get Forwarding Rule
```http
GET /email-features/forwarding/{id}/
```

### Update Forwarding Rule
```http
PATCH /email-features/forwarding/{id}/
```

### Delete Forwarding Rule
```http
DELETE /email-features/forwarding/{id}/
```

---

## 5. Auto-Reply/Vacation Messages

### Get Auto-Reply Settings
```http
GET /email-features/auto-reply/
```

**Response:**
```json
{
  "id": 1,
  "subject": "Out of Office",
  "content": "I am currently out of the office and will return on Monday.",
  "enabled": true,
  "from_date": "2024-01-15T10:30:00Z",
  "until_date": "2024-01-20T18:00:00Z"
}
```

### Create/Update Auto-Reply
```http
POST /email-features/auto-reply/
```

**Request Body:**
```json
{
  "subject": "Out of Office",
  "content": "I am currently out of the office and will return on Monday.",
  "enabled": true
}
```

**Required Fields:** `subject`, `content`

### Disable Auto-Reply
```http
DELETE /email-features/auto-reply/
```

**Response:**
```json
{
  "message": "Auto-reply disabled successfully"
}
```

### Get Auto-Reply History
```http
GET /email-features/auto-reply/history/
```

**Response:**
```json
{
  "history": [
    {
      "sender": "sender@example.com",
      "last_sent": "2024-01-15T14:30:00Z"
    }
  ]
}
```

---

## 6. Analytics (FBS Integration)

### Get Revenue Analytics
```http
GET /admin/analytics/revenue/
```

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "revenue": 15000.00,
  "orders": 25,
  "average_order_value": 600.00,
  "growth_rate": 12.5,
  "period": "2024-01-01 to 2024-01-31"
}
```

### Get Usage Analytics
```http
GET /admin/analytics/usage/
```

**Query Parameters:**
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
  "emails_sent": 5000,
  "storage_used_gb": 1024,
  "active_users": 150,
  "bandwidth_used": 2048,
  "period": "2024-01-01 to 2024-01-31"
}
```

### Get Client Analytics
```http
GET /admin/analytics/clients/
```

**Response:**
```json
{
  "total_clients": 25,
  "active_clients": 20,
  "new_clients_this_month": 3,
  "churn_rate": 2.5,
  "average_revenue_per_client": 600.00
}
```

---

## 7. ERP Integration (FBS)

### Get Usage Summary
```http
GET /erp/usage-summary/
```

**Response:**
```json
{
  "total_organizations": 25,
  "total_email_accounts": 150,
  "total_storage_gb": 1024,
  "monthly_revenue": 15000.00,
  "system_health": "healthy"
}
```

### Provision Organization
```http
POST /erp/provisioning/organization/
```

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "domain": "acme.com",
  "max_users": 50,
  "max_storage_gb": 100,
  "phone": "+1234567890",
  "setup_fee": 500.00,
  "organization_id": 1,
  "provision_date": "2024-01-15"
}
```

**Required Fields:** `name`, `domain`, `max_users`, `max_storage_gb`

**Response:**
```json
{
  "provisioned": true,
  "type": "organization",
  "fbs_customer_id": 12345,
  "message": "Organization Acme Corporation provisioned successfully"
}
```

### Provision Email Account
```http
POST /erp/provisioning/email-account/
```

**Request Body:**
```json
{
  "email": "john.doe@acme.com",
  "first_name": "John",
  "last_name": "Doe",
  "organization_id": 1,
  "monthly_fee": 10.00,
  "provision_date": "2024-01-15"
}
```

**Required Fields:** `email`, `first_name`, `last_name`, `organization_id`

**Response:**
```json
{
  "provisioned": true,
  "type": "email_account",
  "email": "john.doe@acme.com",
  "message": "Email account john.doe@acme.com provisioned successfully"
}
```

### Billing Webhook
```http
POST /erp/webhooks/billing/
```

**Request Body:**
```json
{
  "type": "invoice_created",
  "data": {
    "organization_id": 1,
    "date": "2024-01-15",
    "amount": 500.00,
    "reference": "INV-001",
    "quantity": 1
  }
}
```

**Response:**
```json
{
  "webhook": "processed",
  "type": "invoice_created",
  "message": "Invoice webhook processed successfully"
}
```

---

## Error Handling

### Standard Error Response Format
```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `503 Service Unavailable` - FBS service unavailable

### Field-Specific Validation Errors
```json
{
  "email": ["A contact with this email already exists."],
  "non_field_errors": ["Source and destination emails cannot be the same."]
}
```

---

## Frontend Integration Examples

### JavaScript/TypeScript Examples

#### Create API Key
```javascript
const createApiKey = async (keyData) => {
  const response = await fetch('/fayvad_api/api-keys/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(keyData)
  });
  return response.json();
};
```

#### Get Analytics
```javascript
const getRevenueAnalytics = async (dateFrom, dateTo) => {
  const params = new URLSearchParams();
  if (dateFrom) params.append('date_from', dateFrom);
  if (dateTo) params.append('date_to', dateTo);
  
  const response = await fetch(`/fayvad_api/admin/analytics/revenue/?${params}`, {
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    }
  });
  return response.json();
};
```

#### Provision Organization
```javascript
const provisionOrganization = async (orgData) => {
  const response = await fetch('/fayvad_api/erp/provisioning/organization/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(orgData)
  });
  return response.json();
};
```

### React Hook Example
```javascript
const useApiKeys = () => {
  const [apiKeys, setApiKeys] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const response = await fetch('/fayvad_api/api-keys/', {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setApiKeys(data);
    } catch (error) {
      console.error('Error fetching API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async (keyData) => {
    setLoading(true);
    try {
      const response = await fetch('/fayvad_api/api-keys/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(keyData)
      });
      const data = await response.json();
      await fetchApiKeys(); // Refresh list
      return data;
    } catch (error) {
      console.error('Error creating API key:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return {
    apiKeys,
    loading,
    fetchApiKeys,
    createApiKey
  };
};
```

---

## Rate Limiting
- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

## Security Notes
- All endpoints require authentication (except webhooks)
- User data is isolated (users can only access their own data)
- Input validation is performed on all endpoints
- CSRF protection is enabled for all POST/PUT/PATCH/DELETE requests
- API keys are hashed and never stored in plain text 