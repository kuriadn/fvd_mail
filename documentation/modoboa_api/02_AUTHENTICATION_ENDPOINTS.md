# Authentication Endpoints

## Overview
Authentication endpoints handle user login, logout, token management, and current user information.

---

## 🔐 Login

### `POST /auth/login/`

Authenticates a user and returns an access token.

#### Authentication
- **Required**: No
- **Permission Level**: Public

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
| `username` | string | ✅ | Max 150 characters, alphanumeric |
| `password` | string | ✅ | Min 8 characters |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@fayvad.com",
    "password": "securepassword123"
  }'
```

#### Response (200 OK)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "admin@fayvad.com"
}
```

#### Response (400 Bad Request)
```json
{
  "detail": "Username and password required.",
  "error_code": "MISSING_CREDENTIALS"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Invalid credentials or inactive user.",
  "error_code": "AUTHENTICATION_FAILED"
}
```

---

## 🚪 Logout

### `POST /auth/logout/`

Invalidates the current user's authentication token.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Request Body
None required

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/auth/logout/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "detail": "Logged out."
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided.",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

---

## 🔄 Refresh Token

### `POST /auth/refresh/`

Refreshes the current user's authentication token.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Request Body
None required

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/auth/refresh/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided.",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

---

## 👤 Get Current User

### `GET /auth/me/`

Returns the current authenticated user's profile information.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Authenticated User

#### Request Headers
```
Authorization: Token <your_token>
```

#### Query Parameters
None

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/auth/me/ \
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
    "department": "IT"
  },
  "organization": {
    "id": 1,
    "name": "Fayvad Inc",
    "domain_name": "fayvad.com"
  },
  "role": "admin"
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided.",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

---

## ✏️ Update Current User

### `PATCH /auth/me/`

Updates the current authenticated user's profile information.

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
  "first_name": "string",
  "last_name": "string",
  "email": "string",
  "phone_number": "string",
  "secondary_email": "string",
  "language": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `first_name` | string | ❌ | Max 30 characters |
| `last_name` | string | ❌ | Max 30 characters |
| `email` | string | ❌ | Valid email format |
| `phone_number` | string | ❌ | Valid phone format |
| `secondary_email` | string | ❌ | Valid email format |
| `language` | string | ❌ | ISO 639-1 language code |

#### Sample Request
```bash
curl -X PATCH https://mail.fayvad.com/fayvad_api/auth/me/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890"
  }'
```

#### Response (200 OK)
```json
{
  "id": 1,
  "username": "admin@fayvad.com",
  "email": "admin@fayvad.com",
  "first_name": "John",
  "last_name": "Doe",
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
```

#### Response (400 Bad Request)
```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "field_errors": {
    "email": ["Enter a valid email address."],
    "phone_number": ["Enter a valid phone number."]
  }
}
```

#### Response (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided.",
  "error_code": "AUTHENTICATION_REQUIRED"
}
```

---

## 🔑 API Key Management

### Create API Key

#### `POST /users/{id}/create-api-key/`

Creates a new API key for the specified user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin or Self

#### Request Headers
```
Authorization: Token <your_token>
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "string"
}
```

#### Field Validation
| Field | Type | Required | Validation Rules |
|-------|------|----------|------------------|
| `name` | string | ✅ | Max 100 characters, unique per user |

#### Sample Request
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/users/1/create-api-key/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production API Key"
  }'
```

#### Response (201 Created)
```json
{
  "id": 1,
  "name": "Production API Key",
  "key": "fayvad_1234567890abcdef1234567890abcdef12345678",
  "created": "2025-07-28T10:00:00Z",
  "expires": null,
  "is_active": true
}
```

### List API Keys

#### `GET /users/{id}/api-keys/`

Lists all API keys for the specified user.

#### Authentication
- **Required**: ✅ Token
- **Permission Level**: Admin or Self

#### Request Headers
```
Authorization: Token <your_token>
```

#### Sample Request
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/users/1/api-keys/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

#### Response (200 OK)
```json
[
  {
    "id": 1,
    "name": "Production API Key",
    "created": "2025-07-28T10:00:00Z",
    "expires": null,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Development API Key",
    "created": "2025-07-27T15:30:00Z",
    "expires": "2025-08-27T15:30:00Z",
    "is_active": true
  }
]
```

---

## 🔒 Security Considerations

### Token Security
- Tokens are 40-character alphanumeric strings
- Store tokens securely (environment variables, secure storage)
- Never expose tokens in client-side code
- Rotate tokens regularly

### API Key Security
- API keys are generated as SHA-256 hashes
- Keys are only shown once upon creation
- Use descriptive names for API keys
- Set expiration dates for temporary access

### Best Practices
1. Use HTTPS for all requests
2. Implement proper error handling
3. Log authentication attempts
4. Monitor for suspicious activity
5. Use appropriate user roles
6. Regularly audit API key usage

---

## 📝 Error Codes

| Error Code | HTTP Status | Description |
|------------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | Token not provided |
| `AUTHENTICATION_FAILED` | 401 | Invalid credentials |
| `INACTIVE_USER` | 401 | User account is inactive |
| `MISSING_CREDENTIALS` | 400 | Username or password missing |
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `API_KEY_EXISTS` | 400 | API key with same name exists |
| `API_KEY_EXPIRED` | 401 | API key has expired |

---

*For more information about user management and permissions, see the User Management documentation.* 