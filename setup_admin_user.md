# User Management & Synchronization

## Current Status

**Database Reset Issue**: The Django database was reset/recreated, causing existing users to be lost.

**Current Users**:
- `d.kuria` - System user (recreated manually)

## User Synchronization

### Problem
Django users and Modoboa users need to be kept in sync, but there's currently no automatic synchronization mechanism.

### Current Solution
Use the management command to manually sync known users:

```bash
# Check what would be done
python manage.py sync_modoboa_users --dry-run

# Actually sync users
python manage.py sync_modoboa_users
```

### Known System Users
- **d.kuria** / **MeMiMo@0207** - Primary system user

### Future Implementation Needed

**Phase 3 Priority**: Implement automatic user synchronization between Django and Modoboa:

1. **API Endpoint**: Create Modoboa API endpoint to list all users
2. **Sync Command**: Automated command to sync users periodically
3. **Webhook Integration**: Real-time sync when users are created/modified in Modoboa
4. **SSO Integration**: Single sign-on between Django and Modoboa

### Manual User Creation

For immediate needs, create users manually:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.create_user(
    username='username',
    email='user@domain.com',
    password='password'
)
user.is_active = True
user.save()
```

## Recommendations

1. **Backup Database**: Always backup before major changes
2. **User Documentation**: Maintain list of all system users
3. **Sync Implementation**: Prioritize automatic user sync in Phase 3
4. **Admin Credentials**: Store admin credentials securely for API access