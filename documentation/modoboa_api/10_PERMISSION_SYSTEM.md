# Permission System Documentation

## Overview

The Fayvad API implements a comprehensive role-based access control (RBAC) system that properly separates System Administrators from Organization Administrators.

## Permission Classes

### 1. IsSystemAdmin
- **Purpose**: System Administrators only
- **Scope**: System-wide operations
- **Usage**: Admin-only endpoints

### 2. IsOrganizationAdminOrSystemAdmin  
- **Purpose**: Both Organization and System Administrators
- **Scope**: Organization management within their scope
- **Usage**: Organization dashboard, limits, profile management

### 3. CanManageEmailAccounts
- **Purpose**: Email account operations
- **Behavior**: 
  - System Admins: All email accounts
  - Organization Admins: Only their organization's accounts

### 4. CanManageOrganization
- **Purpose**: Organization-specific resources
- **Behavior**:
  - System Admins: All organizations
  - Organization Admins: Own organization only

## Role Hierarchy

```
System Administrator (is_staff=True)
├── Full system access
├── Manage all organizations
├── Manage all email accounts
└── System-wide operations

Organization Administrator (domain admin access)
├── Manage own organization only
├── Manage email accounts in their domains
├── Organization dashboard access
└── No system-wide access

Regular User
├── Personal profile management
├── Personal usage statistics
└── No admin operations
```

## Security Benefits

1. **Complete Role Separation**: Organization admins have zero system admin privileges
2. **Data Isolation**: Organization admins only access their own data
3. **Principle of Least Privilege**: Each role has minimal required permissions
4. **Multi-tenancy**: Clean separation between organizations

## Implementation

The system uses Modoboa's domain-based access control:
- `Domain.objects.get_for_admin(user)` returns accessible domains
- Organization admins only access domains within their organization
- System admins access all domains

## Migration

**Before**: All admin endpoints used `IsAdminUser` (system admin only)
**After**: Proper role-based permissions with organization isolation

Organization admins can now manage their own resources while system admins retain full system access. 