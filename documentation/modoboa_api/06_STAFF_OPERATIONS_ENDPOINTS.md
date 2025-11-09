# Staff Operations Endpoints

## Overview
Staff operations endpoints allow individual users to manage their personal profiles, change passwords, and view their personal usage statistics. These endpoints are accessible to all authenticated users for their own data.

---

## 👤 Profile Management

### Staff Profile

#### `GET /me/profile/`

Retrieves the current user's profile information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/me/profile/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
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
    "department": "IT",
    "employee_id": "EMP001",
    "hire_date": "2025-01-15"
  },
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "domain_name": "fayvad.com"
  },
  "role": "admin",
  "last_login": "2025-07-28T09:00:00Z",
  "date_joined": "2025-01-15T10:00:00Z"
}
```

---

## 🔐 Password Management

### Change Password

#### `POST /me/change-password/`

Changes the current user's password.

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
  "current_password": "string",
  "new_password": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `current_password` | string | ✅ | Current password verification |
| `new_password` | string | ✅ | Min 8 characters, different from current |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/me/change-password/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldpassword123",
    "new_password": "newsecurepassword456"
  }'
```

#### Response (200 OK)
```json
{
  "detail": "Password changed successfully.",
  "password_changed_at": "2025-07-28T10:00:00Z"
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Password change failed",
  "error_code": "PASSWORD_CHANGE_FAILED",
  "field_errors": {
    "current_password": ["Current password is incorrect."],
    "new_password": ["New password must be different from current password."]
  }
}
```

---

## 📊 Personal Usage

### Personal Usage

#### `GET /me/usage/`

Retrieves the current user's personal usage statistics.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/me/usage/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "email": "admin@fayvad.com",
    "name": "Admin User"
  },
  "email_usage": {
    "total_emails_sent": 1250,
    "total_emails_received": 3420,
    "emails_sent_this_month": 45,
    "emails_received_this_month": 120,
    "average_emails_per_day": 4.5
  },
  "storage_usage": {
    "used_mb": 2048,
    "quota_mb": 1024,
    "percentage": 200.0,
    "over_quota": true,
    "files_count": 1250,
    "folders_count": 15
  },
  "activity": {
    "last_login": "2025-07-28T09:00:00Z",
    "login_count_this_month": 25,
    "average_session_duration_minutes": 45,
    "most_active_day": "Monday",
    "most_active_hour": 14
  },
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "role": "admin",
    "member_since": "2025-01-15T10:00:00Z"
  }
}
```

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Token not provided |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `USER_NOT_FOUND` | 404 | User not found |
| `PASSWORD_CHANGE_FAILED` | 400 | Password change failed |
| `CURRENT_PASSWORD_INCORRECT` | 400 | Current password is incorrect |
| `NEW_PASSWORD_INVALID` | 400 | New password validation failed |
| `PASSWORD_TOO_WEAK` | 400 | Password does not meet security requirements |

---

## 🔒 Security Considerations

### Password Security
- Passwords must meet minimum complexity requirements
- Current password verification is required
- Password change history is logged
- Failed password attempts are monitored

### Data Privacy
- Users can only access their own profile data
- Personal usage statistics are isolated per user
- Sensitive information is encrypted

### Best Practices
1. Use strong, unique passwords
2. Enable two-factor authentication when available
3. Regularly review usage statistics
4. Keep profile information up to date
5. Monitor login activity

---

*This document covers all staff operations endpoints. For other endpoint categories, see the respective documentation files.* 