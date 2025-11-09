# 🚨 Modoboa fayvad_api Integration Issues - Fix Request

## 📋 **Project Overview**

We are building a **Django-based email platform** that uses **Modoboa as the email server backend**. Our Django application provides a modern web interface for email management, while Modoboa handles the actual IMAP/SMTP operations.

### **Architecture**
```
User → Django Web App (fayvad_mail) → Modoboa fayvad_api → Email Server
                                      ↓
                             PostgreSQL Database (shared)
```

### **Current Setup**
- **Modoboa**: Running on `localhost:8000` with fayvad_api endpoints
- **Django App**: Will run on `localhost:8005` and call Modoboa API
- **Database**: Shared PostgreSQL with proper user permissions
- **Authentication**: Token-based API authentication working

---

## ✅ **WORKING FEATURES**

### **1. Authentication**
```bash
✅ POST /fayvad_api/auth/login/
   Body: {"username": "user", "password": "pass"}
   Response: {"token": "xxx", "user_id": 1, "username": "user"}
```

### **2. User Management**
```bash
✅ GET /fayvad_api/users/
   Returns: List of all users with details
✅ GET /fayvad_api/auth/me/
   Returns: Current authenticated user details
```

### **3. Organization Management**
```bash
✅ GET /fayvad_api/admin/organizations/
   Returns: List of organizations with usage stats
✅ POST /fayvad_api/organization-admins/
   Creates: Organization administrators
```

### **4. Domain Management**
```bash
✅ GET /fayvad_api/domains/
   Returns: List of domains with quotas and settings
```

### **5. Email Accounts**
```bash
✅ GET /fayvad_api/org/email-accounts/
   Returns: Organization email accounts with quotas
```

---

## ❌ **BROKEN FEATURES - NEED FIXES**

### **1. Email Sending**
```bash
❌ POST /fayvad_api/email/send/
   Current: {"error": "Missing required fields"}
   Expected: {"sent": true, "message_id": "xxx"}
```

**Expected Request Format:**
```json
{
  "to_emails": ["recipient@example.com"],
  "cc_emails": ["cc@example.com"], 
  "bcc_emails": ["bcc@example.com"],
  "subject": "Email Subject",
  "body": "Email content here",
  "attachments": [] // optional
}
```

**Expected Response:**
```json
{
  "sent": true,
  "message_id": "<generated-message-id@example.com>",
  "timestamp": "2025-01-09T16:40:00Z"
}
```

### **2. Email Folders**
```bash
❌ GET /fayvad_api/email/folders/
   Current: {"error": "Failed to retrieve folders"}
   Expected: {"folders": [...]}
```

**Expected Response:**
```json
{
  "folders": [
    {
      "id": "INBOX",
      "name": "Inbox", 
      "unread_count": 5,
      "total_count": 25
    },
    {
      "id": "Sent",
      "name": "Sent",
      "unread_count": 0, 
      "total_count": 10
    },
    {
      "id": "Drafts",
      "name": "Drafts",
      "unread_count": 0,
      "total_count": 2
    },
    {
      "id": "Trash", 
      "name": "Trash",
      "unread_count": 0,
      "total_count": 0
    }
  ]
}
```

### **3. Email Messages**
```bash
❌ GET /fayvad_api/email/messages/?folder=INBOX&limit=50&page=1
   Current: {"error": "Failed to retrieve messages"}
   Expected: {"messages": [...], "total": 100, "page": 1, "has_next": true}
```

**Expected Response:**
```json
{
  "messages": [
    {
      "id": "123",
      "subject": "Email Subject",
      "sender": "sender@example.com",
      "sender_name": "Sender Name", 
      "from_display": "Sender Name <sender@example.com>",
      "to_recipients": ["recipient@example.com"],
      "cc_recipients": [],
      "bcc_recipients": [],
      "date_received": "2025-01-09T10:30:00Z",
      "date_sent": "2025-01-09T10:25:00Z",
      "is_read": false,
      "is_starred": false,
      "has_attachments": false,
      "size_bytes": 2048,
      "body_text": "Plain text content...",
      "body_html": "<p>HTML content...</p>",
      "snippet": "Email preview text...",
      "folder": "INBOX",
      "message_id": "<message-id@example.com>",
      "uid": "12345"
    }
  ],
  "total": 150,
  "page": 1,
  "has_next": true,
  "has_prev": false
}
```

### **4. Email Actions**
```bash
❌ POST /fayvad_api/email/actions/
   Expected: Mark read/unread, delete, move emails
```

**Expected Request:**
```json
{
  "action": "mark_read", // or "mark_unread", "delete", "move"
  "ids": ["123", "124", "125"],
  "folder": "Trash" // only for move action
}
```

**Expected Response:**
```json
{
  "success": true,
  "action": "mark_read",
  "processed": 3,
  "total": 3
}
```

### **5. Email Search**
```bash
❌ GET /fayvad_api/email/search/?query=test&folder=INBOX
   Expected: Search results
```

---

## 🔧 **REQUIRED FIXES**

### **1. IMAP/SMTP Integration**
- **Issue**: Email operations fail because IMAP/SMTP backend is not working
- **Fix**: Ensure Modoboa can connect to and manage email accounts via IMAP/SMTP
- **Test**: User should be able to send/receive emails through Modoboa

### **2. API Endpoint Implementation**  
- **Issue**: Email API endpoints return errors instead of data
- **Fix**: Implement proper IMAP/SMTP operations in fayvad_api endpoints
- **Reference**: Look at existing working endpoints (users, organizations, domains)

### **3. Database Integration**
- **Issue**: Email data not being stored/retrieved from database
- **Fix**: Ensure email messages, folders, and metadata are properly stored
- **Tables**: Check email_message, email_folder, email_attachment tables

### **4. Authentication Context**
- **Issue**: Email operations don't use authenticated user's context
- **Fix**: Ensure API calls use the authenticated user's email account
- **Context**: Each user should only see their own emails

---

## 🧪 **TESTING SCENARIO**

### **Test User**: `d.kuria@fayvad.com` / `MeMiMo@0207`
### **Expected Workflow**:

1. **Login** → ✅ Working (gets token)
2. **Get Folders** → ❌ Should show INBOX, Sent, etc.
3. **Get Messages** → ❌ Should show user's emails  
4. **Send Email** → ❌ Should send from user's account
5. **Check Sent** → ❌ Should appear in Sent folder

### **Current Results**:
- ✅ Authentication: Token received
- ❌ Folders: "Failed to retrieve folders"  
- ❌ Messages: "Failed to retrieve messages"
- ❌ Send: "Missing required fields"

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **For Modoboa Developers**:

- [ ] **Configure IMAP/SMTP** for test user accounts
- [ ] **Implement** `/fayvad_api/email/folders/` endpoint
- [ ] **Implement** `/fayvad_api/email/messages/` endpoint  
- [ ] **Implement** `/fayvad_api/email/send/` endpoint
- [ ] **Implement** `/fayvad_api/email/actions/` endpoint
- [ ] **Implement** `/fayvad_api/email/search/` endpoint
- [ ] **Test** with user `d.kuria@fayvad.com`
- [ ] **Verify** email send/receive functionality

### **API Response Standards**:
- [ ] **Consistent JSON format** across all endpoints
- [ ] **Proper HTTP status codes** (200, 201, 400, 401, 404)
- [ ] **Error messages** in `{"error": "description"}` format
- [ ] **Pagination** support for large result sets
- [ ] **Authentication required** for email operations

---

## 🔗 **Integration Points**

### **Django App Expectations**:
- Calls Modoboa API with Bearer tokens
- Handles JSON responses and errors gracefully
- Supports file uploads for attachments
- Implements real-time updates for new emails

### **Database Schema** (if needed):
- `email_message`, `email_folder`, `email_attachment` tables
- Proper foreign keys to user accounts
- Indexing for performance

---

## 📞 **Contact & Support**

**Project**: Fayvad Mail - Django Email Platform  
**Issue**: Modoboa fayvad_api email operations not working  
**Priority**: High (blocks core email functionality)  
**Test User**: d.kuria@fayvad.com / MeMiMo@0207  

Please implement the missing email functionality so our Django application can provide a complete email experience to users.

---

**Thank you for your help in making this integration work!** 🚀
