# MSME Email Solution Documentation

## Overview

This document describes the complete email solution for Micro, Small, and Medium Enterprises (MSME) built on Django with Modoboa backend. The system provides professional email communication capabilities for business operations.

## Features

✅ **Email Authentication** - Secure login with business credentials
✅ **Send Emails** - Compose and send professional business emails
✅ **Receive Emails** - Access incoming business correspondence
✅ **Email Attachments** - Upload and send business documents (Modoboa integration)
✅ **Email Organization** - Manage emails in folders
✅ **Email Search** - Find specific business communications
✅ **Email Actions** - Mark read/unread, delete, move emails (IMAP operations)
✅ **Business Workflow** - Complete email communication cycle

## Authentication

### 1. User Authentication

```bash
POST /fayvad_api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**Response:**
```json
{
  "token": "your_auth_token",
  "user_id": 123,
  "username": "your_username"
}
```

### 2. Email Service Authentication

```bash
POST /fayvad_api/email/auth/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "email": "your_email@domain.com",
  "password": "your_email_password"
}
```

**Response:**
```json
{
  "authenticated": true,
  "user_id": 123
}
```

## Sending Emails

### Basic Email Sending

```bash
POST /fayvad_api/email/send/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "to_emails": ["client@company.com"],
  "cc_emails": ["colleague@company.com"],
  "bcc_emails": ["backup@company.com"],
  "subject": "Business Proposal Discussion",
  "body": "Dear Client,\n\nPlease find our business proposal attached.\n\nBest regards,\nYour Company"
}
```

**Response:**
```json
{
  "sent": true,
  "message_id": "<unique-message-id@domain.com>",
  "timestamp": "2025-11-09T18:26:41Z"
}
```

### Email with Attachments

```bash
# Step 1: Upload attachment
POST /fayvad_api/email/attachments/upload/
Authorization: Token your_auth_token
Content-Type: multipart/form-data

file: [business_proposal.pdf]

# Response: {"uploaded": true, "filename": "business_proposal.pdf", "attachment_id": 0}
# Implementation: Uses Modoboa's attachment handling with secure temporary file storage

# Step 2: Send email with attachment
POST /fayvad_api/email/send/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "to_emails": ["client@company.com"],
  "subject": "Business Proposal",
  "body": "Please review the attached proposal.",
  "attachment_ids": [0]
}
```

## Receiving Emails

### Get Email Folders

```bash
GET /fayvad_api/email/folders/
Authorization: Token your_auth_token
```

**Response:**
```json
{
  "folders": [
    {
      "name": "INBOX",
      "type": "inbox",
      "unseen": 3,
      "total": 25
    }
  ]
}
```

### Get Emails from Folder

```bash
GET /fayvad_api/email/messages/?folder=INBOX&limit=50&page=1
Authorization: Token your_auth_token
```

**Response:**
```json
{
  "messages": [
    {
      "id": "123",
      "subject": "Re: Business Proposal",
      "sender": "client@company.com",
      "sender_name": "John Client",
      "from_display": "John Client <client@company.com>",
      "to_recipients": ["your_email@domain.com"],
      "date_received": "2025-11-09T21:27:49Z",
      "date_sent": "2025-11-09T21:25:00Z",
      "is_read": false,
      "is_starred": false,
      "has_attachments": true,
      "size_bytes": 2048,
      "body_text": "Thank you for the proposal...",
      "body_html": "<p>Thank you for the proposal...</p>",
      "snippet": "Thank you for the proposal...",
      "folder": "INBOX",
      "message_id": "<message-id@client.com>",
      "uid": "12345"
    }
  ],
  "total": 25,
  "page": 1,
  "has_next": true,
  "has_prev": false
}
```

## Email Management

### Email Actions

#### Mark Emails as Read

```bash
POST /fayvad_api/email/actions/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "action": "mark_read",
  "ids": ["1", "2", "3"],
  "folder": "INBOX"
}
```

**Response:**
```json
{
  "success": true,
  "action": "mark_read",
  "message_ids": ["1", "2", "3"]
}
```

#### Mark Emails as Unread

```bash
POST /fayvad_api/email/actions/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "action": "mark_unread",
  "ids": ["1"],
  "folder": "INBOX"
}
```

**Response:**
```json
{
  "success": true,
  "action": "mark_unread",
  "message_ids": ["1"]
}
```

#### Delete Emails

```bash
POST /fayvad_api/email/actions/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "action": "delete",
  "ids": ["5", "6"],
  "folder": "INBOX"
}
```

**Response:**
```json
{
  "success": true,
  "action": "delete",
  "message_ids": ["5", "6"]
}
```

#### Move Emails

```bash
POST /fayvad_api/email/actions/
Authorization: Token your_auth_token
Content-Type: application/json

{
  "action": "move",
  "ids": ["7"],
  "folder": "INBOX",
  "destination": "Archive"
}
```

**Response:**
```json
{
  "success": true,
  "action": "move",
  "message_ids": ["7"]
}
```

**Supported Actions:**
- `mark_read` - Mark emails as read
- `mark_unread` - Mark emails as unread
- `delete` - Delete emails (moves to trash if available)
- `move` - Move emails to different folder

**Implementation:** Direct IMAP operations with proper error handling and status verification.

### Search Emails

```bash
GET /fayvad_api/email/search/?query=business&folder=INBOX
Authorization: Token your_auth_token
```

**Response:**
```json
{
  "results": [
    {
      "id": "123",
      "subject": "Business Proposal",
      "sender": "client@company.com",
      "date_received": "2025-11-09T21:27:49Z",
      "is_read": false,
      "has_attachments": true
    }
  ],
  "total": 5,
  "query": "business",
  "folder": "INBOX",
  "limited": false
}
```

## Attachment Management

### Download Attachment

```bash
GET /fayvad_api/email/attachments/download/?id=attachment_id
Authorization: Token your_auth_token
```

## Business Use Cases

### 1. Client Communication

```bash
# Send professional email to client
POST /fayvad_api/email/send/
{
  "to_emails": ["client@company.com"],
  "subject": "Project Update",
  "body": "Dear Client,\n\nProject is progressing well.\n\nBest regards,\nYour Company"
}
```

### 2. Document Sharing

```bash
# Upload invoice
POST /fayvad_api/email/attachments/upload/
file: [invoice.pdf]

# Send with attachment
POST /fayvad_api/email/send/
{
  "to_emails": ["client@company.com"],
  "subject": "Invoice #12345",
  "body": "Please find attached invoice.",
  "attachment_ids": [0]
}
```

### 3. Team Collaboration

```bash
# Send internal update
POST /fayvad_api/email/send/
{
  "to_emails": ["team@company.com"],
  "cc_emails": ["manager@company.com"],
  "subject": "Weekly Status Update",
  "body": "Team,\n\nHere's this week's progress..."
}
```

### 4. Customer Support

```bash
# Check for customer inquiries
GET /fayvad_api/email/messages/?folder=INBOX

# Mark urgent customer email as read
POST /fayvad_api/email/actions/
{
  "action": "mark_read",
  "ids": ["1"],
  "folder": "INBOX"
}

# Respond to customer
POST /fayvad_api/email/send/
{
  "to_emails": ["customer@email.com"],
  "subject": "Re: Support Request",
  "body": "Dear Customer,\n\nThank you for contacting us..."
}

# Archive resolved customer emails
POST /fayvad_api/email/actions/
{
  "action": "move",
  "ids": ["1"],
  "folder": "INBOX",
  "destination": "Archive"
}
```

### 5. Email Organization

```bash
# Mark important emails as unread for follow-up
POST /fayvad_api/email/actions/
{
  "action": "mark_unread",
  "ids": ["2", "3"],
  "folder": "INBOX"
}

# Clean up spam/old emails
POST /fayvad_api/email/actions/
{
  "action": "delete",
  "ids": ["10", "11", "12"],
  "folder": "INBOX"
}
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login/` | POST | User authentication |
| `/email/auth/` | POST | Email service authentication |
| `/email/send/` | POST | Send email |
| `/email/folders/` | GET | Get email folders |
| `/email/messages/` | GET | Get emails from folder |
| `/email/actions/` | POST | Email actions (mark_read/mark_unread/delete/move) |
| `/email/search/` | GET | Search emails |
| `/email/attachments/upload/` | POST | Upload attachment |
| `/email/attachments/download/` | GET | Download attachment |

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `400` - Bad request (missing parameters, invalid data)
- `401` - Unauthorized (invalid credentials)
- `404` - Not found
- `500` - Server error

Error responses include descriptive messages:

```json
{
  "error": "Specific error description"
}
```

## Security Features

- **Token-based authentication** for API access
- **Email credential encryption** for IMAP/SMTP operations
- **Session-based attachment storage** with automatic cleanup
- **Input validation** on all endpoints
- **Secure password handling** (never stored in plain text)

## Business Benefits

✅ **Professional Communication** - Send/receive business emails
✅ **Document Management** - Share files securely via email
✅ **Customer Relations** - Manage client communications
✅ **Team Collaboration** - Internal email coordination
✅ **Search & Organization** - Find and manage emails efficiently
✅ **Cost Effective** - Full email solution without external services
✅ **Scalable** - Support growing business email needs

## Cursor/Python Integration

For developers using Cursor IDE or Python scripts:

### Python API Client Example

```python
import requests

class FayvadEmailClient:
    def __init__(self, base_url="http://localhost:8000/fayvad_api"):
        self.base_url = base_url
        self.token = None
        self.headers = {}

    def authenticate(self, username, password, email, email_password):
        """Authenticate user and email service"""
        # User authentication
        response = requests.post(f"{self.base_url}/auth/login/", json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Token {self.token}"}

        # Email authentication
        response = requests.post(f"{self.base_url}/email/auth/", json={
            "email": email,
            "password": email_password
        }, headers=self.headers)
        response.raise_for_status()
        return True

    def send_email(self, to_emails, subject, body, attachment_ids=None):
        """Send email with optional attachments"""
        data = {
            "to_emails": to_emails,
            "subject": subject,
            "body": body
        }
        if attachment_ids:
            data["attachment_ids"] = attachment_ids

        response = requests.post(f"{self.base_url}/email/send/",
                               json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_messages(self, folder="INBOX", limit=50):
        """Get emails from folder"""
        params = {"folder": folder, "limit": limit, "page": 1}
        response = requests.get(f"{self.base_url}/email/messages/",
                              params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def upload_attachment(self, file_path):
        """Upload file attachment"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.base_url}/email/attachments/upload/",
                                   files=files, headers=self.headers)
            response.raise_for_status()
            return response.json()

# Usage example
client = FayvadEmailClient()
client.authenticate("your_username", "password", "email@domain.com", "email_password")

# Send email
result = client.send_email(
    to_emails=["recipient@company.com"],
    subject="Business Proposal",
    body="Please find attached our proposal."
)
print(f"Email sent: {result}")

# Get messages
messages = client.get_messages()
print(f"Found {len(messages['messages'])} emails")
```

### Testing in Cursor

```python
# Quick test script for Cursor
import requests

BASE_URL = "http://localhost:8000/fayvad_api"

def test_email_system():
    # Authenticate
    auth_response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": "test_user",
        "password": "test_pass"
    })

    if auth_response.status_code == 200:
        token = auth_response.json()["token"]
        headers = {"Authorization": f"Token {token}"}

        # Test email auth
        email_auth = requests.post(f"{BASE_URL}/email/auth/", json={
            "email": "test@email.com",
            "password": "email_pass"
        }, headers=headers)

        if email_auth.status_code == 200:
            # Test sending
            send_result = requests.post(f"{BASE_URL}/email/send/", json={
                "to_emails": ["test@example.com"],
                "subject": "Test from Cursor",
                "body": "Testing email integration"
            }, headers=headers)

            print("✅ Email system working!" if send_result.status_code == 200 else "❌ Send failed")
        else:
            print("❌ Email auth failed")
    else:
        print("❌ User auth failed")

if __name__ == "__main__":
    test_email_system()
```

## Implementation Status

✅ **All Critical Features Working:**
- Email authentication (user + email credentials)
- Send emails with attachments
- Receive and read emails
- Email organization (folders, search)
- Email actions (mark read/unread/delete/move) - **FIXED**
- Attachment upload/download - **FIXED** (hybrid database/session system)
- Business workflow integration

⚠️ **Minor Issues:**
- Email search functionality needs refinement (non-critical for business use)

**Tested and Verified:**
- End-to-end email communication
- Real IMAP/SMTP operations
- Modoboa integration working
- Production-ready for MSME businesses

**Recent Fixes:**
- ✅ **Delete Action**: Now properly marks messages as deleted and expunges
- ✅ **Attachment Download**: Full file download with proper headers (hybrid database/session system)
- ✅ **Attachment Upload**: Returns correct attachment IDs for download
- ℹ️ **Sent Folder**: Normal SMTP behavior (emails not auto-saved to IMAP Sent)

## Getting Started

1. **Register business account** with email credentials
2. **Authenticate** using login and email auth endpoints
3. **Send test email** to verify configuration
4. **Start business communications**

## Support

For technical issues or questions about the email solution, contact your system administrator or refer to the API documentation.
