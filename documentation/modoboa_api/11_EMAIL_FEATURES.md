# Email Features API Documentation

This document covers the new email features implemented in the Fayvad API: Email Signatures, Contact Management, Email Forwarding, and Auto-Reply/Vacation Messages.

## Table of Contents

1. [Email Signatures](#email-signatures)
2. [Contact Management](#contact-management)
3. [Email Forwarding](#email-forwarding)
4. [Auto-Reply/Vacation Messages](#auto-reply-vacation-messages)

---

## Email Signatures

### Overview
Email signatures allow users to set up personalized text and HTML signatures that are automatically appended to outgoing emails.

### Endpoints

#### Get Email Signature
**`GET /email-features/signatures/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve the current user's email signature settings.

**Response**:
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

**Sample Request**:
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/email-features/signatures/ \
  -H "Authorization: Token <your_token>"
```

#### Create/Update Email Signature
**`POST /email-features/signatures/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Create or update the current user's email signature.

**Request Body**:
```json
{
  "text_signature": "Best regards,\nJohn Doe\nSoftware Engineer",
  "html_signature": "<p>Best regards,<br>John Doe<br>Software Engineer</p>",
  "is_active": true
}
```

**Response**: Same as GET response

**Sample Request**:
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email-features/signatures/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text_signature": "Best regards,\nJohn Doe\nSoftware Engineer",
    "html_signature": "<p>Best regards,<br>John Doe<br>Software Engineer</p>",
    "is_active": true
  }'
```

#### Update Email Signature
**`PATCH /email-features/signatures/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Partially update the email signature.

**Request Body**:
```json
{
  "is_active": false
}
```

#### Delete Email Signature
**`DELETE /email-features/signatures/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Delete the email signature.

---

## Contact Management

### Overview
Contact management allows users to maintain a personal address book with contact information for easy access when composing emails.

### Endpoints

#### List Contacts
**`GET /email-features/contacts/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve all contacts for the current user.

**Query Parameters**:
- `search` (optional): Search contacts by name or email
- `page` (optional): Page number for pagination
- `page_size` (optional): Number of contacts per page

**Response**:
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

#### Create Contact
**`POST /email-features/contacts/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Create a new contact.

**Request Body**:
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

**Required Fields**: `first_name`, `last_name`, `email`  
**Optional Fields**: `phone`, `company`, `job_title`, `notes`

#### Get Contact
**`GET /email-features/contacts/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve a specific contact.

#### Update Contact
**`PATCH /email-features/contacts/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Update a contact.

#### Delete Contact
**`DELETE /email-features/contacts/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Delete a contact.

#### Import Contacts from CSV
**`POST /email-features/contacts/import_csv/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Import contacts from a CSV file.

**Request**: Multipart form data with CSV file

**CSV Format**:
```csv
first_name,last_name,email,phone,company,job_title,notes
John,Doe,john.doe@example.com,+1234567890,Tech Corp,Software Engineer,Met at conference
Jane,Smith,jane.smith@example.com,+1234567891,Design Studio,UX Designer,Colleague
```

**Response**:
```json
{
  "imported_count": 2,
  "errors": []
}
```

#### Export Contacts to CSV
**`GET /email-features/contacts/export_csv/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Export all contacts to CSV format.

**Response**: CSV file download

---

## Email Forwarding

### Overview
Email forwarding allows users to set up rules to automatically forward incoming emails to other email addresses.

### Endpoints

#### List Forwarding Rules
**`GET /email-features/forwarding/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve all email forwarding rules for the current user.

**Response**:
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

#### Create Forwarding Rule
**`POST /email-features/forwarding/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Create a new email forwarding rule.

**Request Body**:
```json
{
  "source_email": "john@company.com",
  "destination_email": "john.personal@gmail.com",
  "is_active": true,
  "keep_copy": true
}
```

**Required Fields**: `source_email`, `destination_email`  
**Optional Fields**: `is_active` (default: true), `keep_copy` (default: true)

**Validation Rules**:
- Source and destination emails cannot be the same
- Duplicate forwarding rules are not allowed

#### Get Forwarding Rule
**`GET /email-features/forwarding/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve a specific forwarding rule.

#### Update Forwarding Rule
**`PATCH /email-features/forwarding/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Update a forwarding rule.

#### Delete Forwarding Rule
**`DELETE /email-features/forwarding/{id}/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Delete a forwarding rule.

---

## Auto-Reply/Vacation Messages

### Overview
Auto-reply functionality allows users to set up automatic responses when they are away or unavailable, using Modoboa's built-in auto-reply system.

### Endpoints

#### Get Auto-Reply Settings
**`GET /email-features/auto-reply/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve current auto-reply settings.

**Response**:
```json
{
  "id": 1,
  "subject": "Out of Office",
  "content": "I am currently out of the office and will return on Monday. For urgent matters, please contact my colleague.",
  "enabled": true,
  "from_date": "2024-01-15T10:30:00Z",
  "until_date": "2024-01-20T18:00:00Z"
}
```

**Sample Request**:
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/email-features/auto-reply/ \
  -H "Authorization: Token <your_token>"
```

#### Create/Update Auto-Reply
**`POST /email-features/auto-reply/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Create or update auto-reply settings.

**Request Body**:
```json
{
  "subject": "Out of Office",
  "content": "I am currently out of the office and will return on Monday. For urgent matters, please contact my colleague.",
  "enabled": true
}
```

**Required Fields**: `subject`, `content`  
**Optional Fields**: `enabled` (default: false)

**Sample Request**:
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/email-features/auto-reply/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Out of Office",
    "content": "I am currently out of the office and will return on Monday.",
    "enabled": true
  }'
```

#### Disable Auto-Reply
**`DELETE /email-features/auto-reply/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Disable auto-reply functionality.

**Response**:
```json
{
  "message": "Auto-reply disabled successfully"
}
```

#### Get Auto-Reply History
**`GET /email-features/auto-reply/history/`**

**Authentication**: Required  
**Permission**: Authenticated user  
**Description**: Retrieve auto-reply history (who received auto-replies).

**Response**:
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

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error": "Subject and content are required"
}
```

#### 401 Unauthorized
```json
{
  "error": "Authentication credentials were not provided"
}
```

#### 404 Not Found
```json
{
  "error": "No mailbox found for user"
}
```

#### 503 Service Unavailable
```json
{
  "error": "Auto-reply functionality not available"
}
```

### Field-Specific Validation Errors

#### Contact Email Validation
```json
{
  "email": ["A contact with this email already exists."]
}
```

#### Forwarding Rule Validation
```json
{
  "non_field_errors": ["Source and destination emails cannot be the same."]
}
```

---

## Rate Limiting

All email features endpoints are subject to the standard rate limiting:
- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

---

## Security Considerations

1. **User Isolation**: All endpoints are scoped to the authenticated user's data only
2. **Input Validation**: All user inputs are validated and sanitized
3. **CSRF Protection**: All POST/PUT/PATCH/DELETE requests require CSRF tokens
4. **File Upload Security**: CSV imports are validated for file type and content

---

## Integration Notes

### Auto-Reply Integration
The auto-reply functionality integrates with Modoboa's existing `modoboa_postfix_autoreply` extension:
- Uses existing `ARmessage` and `ARhistoric` models
- Maintains compatibility with Modoboa's auto-reply system
- Gracefully handles cases where the extension is not installed

### Email Signature Integration
Email signatures are designed to integrate with email composition systems:
- Supports both plain text and HTML formats
- Can be easily integrated with email clients and webmail interfaces
- Maintains user preferences across sessions

### Contact Management Integration
Contact management provides:
- CSV import/export functionality for easy data migration
- Search capabilities for quick contact lookup
- Structured data for integration with email composition interfaces

### Email Forwarding Integration
Email forwarding rules:
- Integrate with mail server configuration
- Support both forwarding with and without keeping copies
- Maintain user control over forwarding preferences 