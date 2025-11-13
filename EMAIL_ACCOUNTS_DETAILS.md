# Email Accounts Details - Master Reference

**⚠️ SECURITY WARNING**: This file contains sensitive email account information.  
**DO NOT commit this file to version control.**  
**Store securely and restrict access.**

---

## Last Updated
Generated: 2025-01-XX

---

## Primary Domain: fayvad.com

### System Admin Account
- **Email**: `d.kuria@fayvad.com` (or `d.kuria` as username)
- **Password**: `MeMiMo@0207`
- **Role**: System Admin / Django User
- **Status**: Active
- **Notes**: Used for Django authentication and API access

---

## Subdomain: geo.fayvad.com

### Domain Information
- **Domain**: geo.fayvad.com
- **Organization**: Fayvad Geosolutions Ltd
- **Created**: 2025-11-12

### Email Accounts

#### 1. Admin Account
- **Email**: `admin@geo.fayvad.com`
- **Username**: `admin_geo_fayvad_com`
- **Password**: `%PHg5JErPj*f`
- **Status**: Active
- **Quota**: 1024 MB (1 GB)

#### 2. Info Account
- **Email**: `info@geo.fayvad.com`
- **Username**: `info`
- **Password**: `pqltf8px&J@$`
- **Status**: Active
- **Quota**: 1024 MB (1 GB)

#### 3. Kuria Account
- **Email**: `kuria@geo.fayvad.com`
- **Username**: `kuria`
- **Password**: `*h^3mr0&N80b`
- **Status**: Active
- **Quota**: 1024 MB (1 GB)

#### 4. Services Account
- **Email**: `services@geo.fayvad.com`
- **Username**: `services`
- **Password**: `XXcKlXlH^%1I`
- **Status**: Active
- **Quota**: 1024 MB (1 GB)

---

## Email Server Configuration

### IMAP Settings (Receiving Emails)
- **Server**: `mail.fayvad.com`
- **Port**: 993 (SSL) or 143 (TLS)
- **Username**: Full email address (e.g., `kuria@geo.fayvad.com`)
- **Password**: Account password (from above)
- **Encryption**: SSL/TLS required

### SMTP Settings (Sending Emails)
- **Server**: `mail.fayvad.com`
- **Port**: 587 (TLS) or 465 (SSL)
- **Username**: Full email address (e.g., `kuria@geo.fayvad.com`)
- **Password**: Account password (from above)
- **Authentication**: Required
- **Encryption**: TLS/SSL required

---

## Webmail Access

### Webmail URL
- **URL**: `https://mail.fayvad.com` (or your configured webmail URL)
- **Login**: Use full email address and password

---

## API Access

### Django API Authentication
- **Username**: `d.kuria`
- **Password**: `MeMiMo@0207`
- **API Base URL**: `https://mail.fayvad.com/fayvad_api`
- **Token Endpoint**: `/auth/login/`

### Example API Login
```bash
curl -X POST https://mail.fayvad.com/fayvad_api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "d.kuria",
    "password": "MeMiMo@0207"
  }'
```

---

## Password Management

### Password Reset
To reset an email account password:
1. Use Django admin or API endpoint
2. Update password hash in database
3. Update Dovecot password file (if using Dovecot)
4. Update Postfix virtual mailbox (if needed)

### Password Storage
- Passwords are stored as hashes in Django database
- Dovecot password hashes stored separately
- Never store plain text passwords in production

---

## Security Notes

1. **Never commit passwords to git**
2. **Use secure password storage in production**
3. **Enable SPF, DKIM, DMARC** (already configured)
4. **Use TLS/SSL for all connections**
5. **Regularly update passwords**
6. **Monitor email logs for suspicious activity**
7. **Restrict access to this file**

---

## Related Files

- `email_passwords_geo_fayvad_com.txt` - Original geo.fayvad.com passwords
- `creation_org_email_geosolution` - Creation log for geo.fayvad.com accounts
- `EMAIL_TEST_GUIDE.md` - Testing guide with email accounts
- `setup_admin_user.md` - Admin user setup instructions

---

## Additional Domains

### digital.fayvad.com
- Email accounts: (To be documented)

### mfariji.fayvad.com
- Email accounts: (To be documented)

### driving.fayvad.com
- Email accounts: (To be documented)

---

## Quick Reference

### Most Used Accounts
- **System Admin**: `d.kuria` / `MeMiMo@0207`
- **Geo Admin**: `admin@geo.fayvad.com` / `%PHg5JErPj*f`
- **Geo Kuria**: `kuria@geo.fayvad.com` / `*h^3mr0&N80b`

### Testing Accounts
- **Geo Services**: `services@geo.fayvad.com` / `XXcKlXlH^%1I`
- **Geo Info**: `info@geo.fayvad.com` / `pqltf8px&J@$`

---

**Note**: This file should be updated whenever new email accounts are created or passwords are changed.

