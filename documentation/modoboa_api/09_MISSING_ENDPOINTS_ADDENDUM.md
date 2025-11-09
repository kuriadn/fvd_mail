# Missing Endpoints Addendum

This document contains the endpoints that were missing from the main documentation but are present in the actual codebase.

## 1. Organization Admin Management Endpoints

### List Organization Admins

#### `GET /admin/organizations/{id}/admins/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Lists all admins for a specific organization.

**Response**:
```json
{
  "results": []
}
```

**Sample Request**:
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/admin/organizations/1/admins/ \
  -H "Authorization: Token <your_token>"
```

### Create Organization Admin

#### `POST /admin/organizations/{id}/admins/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Creates a new admin for a specific organization.

**Response**:
```json
{
  "created": true
}
```

**Sample Request**:
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/1/admins/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json"
```

### Update Organization Admin

#### `PATCH /admin/organizations/{id}/admins/{admin_id}/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Updates an existing admin for a specific organization.

**Response**:
```json
{
  "updated": true
}
```

**Sample Request**:
```bash
curl -X PATCH https://mail.fayvad.com/fayvad_api/admin/organizations/1/admins/2/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json"
```

### Delete Organization Admin

#### `DELETE /admin/organizations/{id}/admins/{admin_id}/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Removes an admin from a specific organization.

**Response**:
```json
{
  "deleted": true
}
```

**Sample Request**:
```bash
curl -X DELETE https://mail.fayvad.com/fayvad_api/admin/organizations/1/admins/2/ \
  -H "Authorization: Token <your_token>"
```

## 2. Organization Access Control

### Set Organization Access

#### `POST /admin/organizations/{id}/set-access/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Sets access levels for a specific organization.

**Response**:
```json
{
  "access": "set"
}
```

**Sample Request**:
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/1/set-access/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json"
```

## 3. Organization Subscription Management

### Change Organization Subscription

#### `POST /admin/organizations/{id}/change-subscription/`

**Authentication**: Required  
**Permission**: Admin only  
**Description**: Changes the subscription plan for a specific organization.

**Response**:
```json
{
  "status": "changed"
}
```

**Sample Request**:
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/admin/organizations/1/change-subscription/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json"
```

## 4. Shared Role-Based Endpoints

### Role-Based Dashboard

#### `GET /dashboard/`

**Authentication**: Required  
**Permission**: Any authenticated user  
**Description**: Returns role-based dashboard data for the current user.

**Response**:
```json
{
  "dashboard": "ok"
}
```

**Sample Request**:
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/dashboard/ \
  -H "Authorization: Token <your_token>"
```

### Role-Based Notifications

#### `GET /notifications/`

**Authentication**: Required  
**Permission**: Any authenticated user  
**Description**: Returns role-based notifications for the current user.

**Response**:
```json
{
  "notifications": "ok"
}
```

**Sample Request**:
```bash
curl -X GET https://mail.fayvad.com/fayvad_api/notifications/ \
  -H "Authorization: Token <your_token>"
```

## Error Codes

These endpoints use the standard error response format:

- `400` - Bad Request
- `401` - Unauthorized  
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error 