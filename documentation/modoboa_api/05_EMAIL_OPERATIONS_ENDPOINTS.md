# Email Operations Endpoints

## Overview
Email operations endpoints provide functionality for email authentication, message management, folder operations, and attachment handling. These endpoints are used by email clients and webmail interfaces.

---

## 🔐 Email Authentication

### Email Authentication

#### `POST /email/authenticate/`

Authenticates an email user for email operations.

#### Authentication
- **Required**: No
- **Permission Level**: Public

#### Request Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "username": "string",
  "password": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `username` | string | ✅ | Valid email address |
| `password` | string | ✅ | Min 8 characters |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/authenticate/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@fayvad.com",
    "password": "securepassword123"
  }'
```

#### Response (200 OK)
```json
{
  "authenticated": true,
  "user": {
    "email": "admin@fayvad.com",
    "first_name": "Admin",
    "last_name": "User"
  }
}
```

#### Response (401 Unauthorized)
```json
{
  "authenticated": false,
  "detail": "Invalid credentials"
}
```

---

## 📁 Folder Operations

### List Email Folders

#### `GET /email/folders/`

Retrieves a list of email folders for the authenticated user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/email/folders/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "folders": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "path": "INBOX",
      "unread_count": 5,
      "total_count": 1250,
      "size_bytes": 52428800
    },
    {
      "id": "Sent",
      "name": "Sent",
      "path": "Sent",
      "unread_count": 0,
      "total_count": 450,
      "size_bytes": 20971520
    },
    {
      "id": "Drafts",
      "name": "Drafts",
      "path": "Drafts",
      "unread_count": 0,
      "total_count": 3,
      "size_bytes": 1048576
    },
    {
      "id": "Trash",
      "name": "Trash",
      "path": "Trash",
      "unread_count": 0,
      "total_count": 25,
      "size_bytes": 5242880
    }
  ]
}
```

---

## 📧 Message Operations

### List Email Messages

#### `GET /email/messages/`

Retrieves a list of email messages from a specified folder.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder` | string | ❌ | Folder name (default: "INBOX") |
| `page` | integer | ❌ | Page number (default: 1) |
| `page_size` | integer | ❌ | Items per page (default: 20, max: 100) |
| `sort_by` | string | ❌ | Sort field: "date", "subject", "from" (default: "date") |
| `sort_order` | string | ❌ | Sort order: "asc", "desc" (default: "desc") |
| `unread_only` | boolean | ❌ | Filter unread messages only |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/email/messages/?folder=INBOX&page=1&page_size=10" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "count": 1250,
  "next": "https://mail.fayvad.com/fayvad_api/email/messages/?folder=INBOX&page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": 12345,
      "subject": "Welcome to Fayvad Email Platform",
      "from": "support@fayvad.com",
      "to": ["admin@fayvad.com"],
      "cc": [],
      "bcc": [],
      "date": "2025-07-28T10:00:00Z",
      "folder": "INBOX",
      "is_read": false,
      "is_flagged": false,
      "has_attachments": false,
      "size_bytes": 2048,
      "preview": "Thank you for choosing Fayvad Email Platform..."
    },
    {
      "id": 12344,
      "subject": "Monthly Newsletter - July 2025",
      "from": "newsletter@fayvad.com",
      "to": ["admin@fayvad.com"],
      "cc": [],
      "bcc": [],
      "date": "2025-07-27T15:30:00Z",
      "folder": "INBOX",
      "is_read": true,
      "is_flagged": false,
      "has_attachments": true,
      "size_bytes": 15360,
      "preview": "Here's what's new in Fayvad Email Platform this month..."
    }
  ]
}
```

### Send Email

#### `POST /email/send/`

Sends an email message.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "to": ["string"],
  "cc": ["string"],
  "bcc": ["string"],
  "subject": "string",
  "body": "string",
  "attachments": ["file"]
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `to` | array | ✅ | Array of valid email addresses |
| `cc` | array | ❌ | Array of valid email addresses |
| `bcc` | array | ❌ | Array of valid email addresses |
| `subject` | string | ✅ | Max 255 characters |
| `body` | string | ✅ | Max 10MB |
| `attachments` | array | ❌ | Array of file objects |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/send/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["john.doe@example.com"],
    "cc": ["jane.smith@example.com"],
    "subject": "Test Email",
    "body": "This is a test email sent via the Fayvad API."
  }'
```

#### Response (200 OK)
```json
{
  "sent": true,
  "message_id": "20250728100000.12345@mail.fayvad.com",
  "recipients": ["john.doe@example.com", "jane.smith@example.com"]
}
```

#### Response (400 Bad Request)
```json
{
  "sent": false,
  "detail": "Invalid email address format",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "to": ["Invalid email address: invalid@email"]
  }
}
```

### Email Actions

#### `POST /email/actions/`

Performs actions on email messages (mark as read, delete, move, etc.).

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "action": "string",
  "ids": ["integer"]
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `action` | string | ✅ | One of: "mark_read", "mark_unread", "delete", "move", "flag", "unflag" |
| `ids` | array | ✅ | Array of valid message IDs |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/actions/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "mark_read",
    "ids": [12345, 12346, 12347]
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Action performed successfully.",
  "action": "mark_read",
  "processed_count": 3,
  "message_ids": [12345, 12346, 12347]
}
```

#### Response (404 Not Found)
```json
{
  "detail": "No matching emails",
  "error_code": "MESSAGES_NOT_FOUND"
}
```

### Search Emails

#### `POST /email/search/`

Searches for email messages.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "query": "string",
  "folder": "string",
  "filters": {
    "from": "string",
    "to": "string",
    "subject": "string",
    "date_from": "string",
    "date_to": "string",
    "has_attachments": "boolean"
  }
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `query` | string | ✅ | Search query text |
| `folder` | string | ❌ | Folder to search in |
| `filters` | object | ❌ | Search filters object |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/search/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fayvad",
    "folder": "INBOX",
    "filters": {
      "date_from": "2025-07-01",
      "has_attachments": true
    }
  }'
```

#### Response (200 OK)
```json
{
  "count": 5,
  "results": [
    {
      "id": 12345,
      "subject": "Welcome to Fayvad Email Platform",
      "from": "support@fayvad.com",
      "to": ["admin@fayvad.com"],
      "date": "2025-07-28T10:00:00Z",
      "folder": "INBOX",
      "is_read": false,
      "has_attachments": false,
      "preview": "Thank you for choosing Fayvad Email Platform..."
    }
  ]
}
```

---

## 📎 Attachment Operations

### Upload Attachment

#### `POST /email/upload-attachment/`

Uploads an attachment for use in email composition.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: multipart/form-data
```

#### Request Body
Multipart form data with file

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `file` | file | ✅ | Max 25MB, allowed types: images, documents, archives |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/upload-attachment/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -F "file=@document.pdf"
```

#### Response (200 OK)
```json
{
  "detail": "Attachment uploaded successfully.",
  "attachment_id": "att_12345",
  "filename": "document.pdf",
  "size_bytes": 1048576,
  "content_type": "application/pdf"
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Attachment too large or missing.",
  "error_code": "ATTACHMENT_TOO_LARGE"
}
```

### Download Attachment

#### `GET /email/download-attachment/`

Downloads an email attachment.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Query Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `attachment_id` | string | ✅ | Attachment ID |

#### Sample Request
```bash
curl -X GET "https://mail.fayvad.com/fayvad_api/email/download-attachment/?attachment_id=att_12345" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
File download with appropriate headers:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="document.pdf"
Content-Length: 1048576
```

#### Response (404 Not Found)
```json
{
  "detail": "Attachment not found.",
  "error_code": "ATTACHMENT_NOT_FOUND"
}
```

---

## 📝 Draft Operations

### Email Draft

#### `GET /email/draft/`

Retrieves draft emails.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/email/draft/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "drafts": [
    {
      "id": 1,
      "to": ["john.doe@example.com"],
      "subject": "Draft: Project Update",
      "body": "Here's the latest update on our project...",
      "created_at": "2025-07-28T09:00:00Z",
      "updated_at": "2025-07-28T09:30:00Z"
    }
  ]
}
```

#### `POST /email/draft/`

Saves a draft email.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Body
```json
{
  "to": ["string"],
  "subject": "string",
  "body": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `to` | array | ❌ | Array of valid email addresses |
| `subject` | string | ❌ | Max 255 characters |
| `body` | string | ❌ | Max 10MB |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/draft/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["john.doe@example.com"],
    "subject": "Draft: Project Update",
    "body": "Here's the latest update on our project..."
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Draft saved successfully.",
  "draft_id": 1
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Missing required fields.",
  "error_code": "MISSING_REQUIRED_FIELDS"
}
```

---

## 🔍 Email Filters

### Email Filters

#### `GET /email/filters/`

Retrieves email filters for the user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/email/filters/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "filters": [
    {
      "id": 1,
      "name": "Spam Filter",
      "field": "from",
      "operator": "contains",
      "value": "spam@example.com",
      "action": "move",
      "target_folder": "Spam",
      "is_active": true
    },
    {
      "id": 2,
      "name": "Work Emails",
      "field": "to",
      "operator": "contains",
      "value": "work@fayvad.com",
      "action": "flag",
      "is_active": true
    }
  ]
}
```

#### `POST /email/filters/`

Creates or updates email filters.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Body
```json
{
  "filters": [
    {
      "field": "string",
      "operator": "string",
      "value": "string"
    }
  ]
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `filters` | array | ✅ | Array of filter objects |
| `field` | string | ✅ | One of: "from", "to", "subject", "body" |
| `operator` | string | ✅ | One of: "contains", "equals", "starts_with", "ends_with" |
| `value` | string | ✅ | Filter value |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email/filters/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": [
      {
        "field": "from",
        "operator": "contains",
        "value": "newsletter@"
      }
    ]
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Filter set successfully.",
  "filter_id": 3
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Invalid filter.",
  "error_code": "INVALID_FILTER"
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTHENTICATION_FAILED` | 401 | Invalid email credentials |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `FOLDER_NOT_FOUND` | 404 | Email folder not found |
| `MESSAGE_NOT_FOUND` | 404 | Email message not found |
| `ATTACHMENT_NOT_FOUND` | 404 | Attachment not found |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `ATTACHMENT_TOO_LARGE` | 400 | Attachment exceeds size limit |
| `INVALID_EMAIL_ADDRESS` | 400 | Invalid email address format |
| `MESSAGES_NOT_FOUND` | 404 | No matching messages found |
| `INVALID_FILTER` | 400 | Invalid email filter |
| `MISSING_REQUIRED_FIELDS` | 400 | Missing required fields |

---

## 🔒 Security Considerations

### Email Security
- All email operations require authentication
- Email content is encrypted in transit
- Attachments are scanned for malware
- Rate limiting is applied to prevent abuse

### Data Privacy
- Email content is only accessible to the authenticated user
- Attachments are stored securely
- Search queries are logged for security purposes

### Best Practices
1. Use HTTPS for all requests
2. Implement proper error handling
3. Validate email addresses before sending
4. Monitor attachment sizes
5. Use appropriate content types for attachments
6. Implement rate limiting for bulk operations

---

## 📊 Rate Limiting

### Email Operations Limits
- **Send emails**: 100 per hour
- **Search queries**: 1000 per hour
- **Attachment uploads**: 50 per hour
- **Bulk actions**: 10 per hour

### Rate Limit Headers
```
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1640995200
```

---

*This document covers all email operations endpoints. For other endpoint categories, see the respective documentation files.* 