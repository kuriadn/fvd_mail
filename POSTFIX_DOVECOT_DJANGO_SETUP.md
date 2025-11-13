# Postfix/Dovecot Django Integration

## Overview

Postfix and Dovecot are configured to query Django database directly.

## Changes Made

### 1. Database Schema
- Added `password_hash` field to `EmailAccount` model
- Stores password in SHA512-CRYPT format (compatible with Dovecot)
- Migration: `mail/migrations/0007_add_password_hash.py`

### 2. Postfix Configuration Files

**`/etc/postfix/virtual_mailboxes.cf`**
- Queries Django `mail_emailaccount` table
- Returns maildir path: `/var/vmail/{domain}/{username}/`

**`/etc/postfix/virtual_domains.cf`**
- Queries Django `mail_domain` table
- Returns domain name if enabled

**`/etc/postfix/virtual_aliases.cf`**
- Queries Django `mail_emailaccount` table
- Returns email address for aliases

### 3. Dovecot Configuration File

**`/etc/dovecot/dovecot-sql.conf.ext`**
- Password query: Uses `password_hash` from `mail_emailaccount`
- User query: Returns maildir path, uid, gid
- Iterate query: Lists all active email accounts

## Setup Instructions

### Step 1: Run Migration Script
```bash
# Create account in Django (if needed)
python manage.py create_email_account d.kuria@fayvad.com --user-id 1 --password YourPassword
```

### Step 2: Apply Configs
```bash
# Run config script (requires sudo)
sudo bash postfix_dovecot_django_configs.sh
```

### Step 3: Test Configuration
```bash
# Test Postfix virtual mailbox lookup
sudo postmap -q d.kuria@fayvad.com pgsql:/etc/postfix/virtual_mailboxes.cf

# Test Postfix virtual domain lookup
sudo postmap -q fayvad.com pgsql:/etc/postfix/virtual_domains.cf

# Check Dovecot config syntax
sudo doveconf -n
```

### Step 4: Reload Services
```bash
# Reload Postfix
sudo postfix reload

# Restart Dovecot
sudo systemctl restart dovecot

# Check status
sudo systemctl status dovecot
```

## Password Management

### Creating New Accounts
When creating email accounts via `DomainManager.create_email_account()`:
- Password is automatically hashed using SHA512-CRYPT
- Hash is stored in `EmailAccount.password_hash`
- Compatible with Dovecot authentication

### Updating Passwords
To update a password:
```python
from mail.models import EmailAccount
import crypt

account = EmailAccount.objects.get(email='user@domain.com')
account.password_hash = crypt.crypt(new_password, crypt.mksalt(crypt.METHOD_SHA512))
account.save()
```

## Database Connection

- **Database**: `fayvad_mail_db`
- **User**: `fayvad`
- **Password**: `MeMiMo@0207`
- **Host**: `localhost`

## Mail Directory Structure

```
/var/vmail/
  └── {domain}/
      └── {username}/
          ├── cur/
          ├── new/
          └── tmp/
```

## Security Notes

1. Config files have restricted permissions (600)
2. Password hashes stored securely (SHA512-CRYPT)
3. Only active accounts are queried (`is_active=true`)
4. Only enabled domains are queried (`enabled=true`)

## Troubleshooting

### Postfix Issues
- Check logs: `sudo tail -f /var/log/mail.log`
- Test queries: `sudo postmap -q <email> pgsql:/etc/postfix/virtual_mailboxes.cf`
- Verify DB connection: `psql -U fayvad -d fayvad_mail_db -c "SELECT email FROM mail_emailaccount;"`

### Dovecot Issues
- Check logs: `sudo tail -f /var/log/dovecot.log`
- Test config: `sudo doveconf -n`
- Verify password hash exists: `psql -U fayvad -d fayvad_mail_db -c "SELECT email, password_hash IS NOT NULL FROM mail_emailaccount WHERE email='d.kuria@fayvad.com';"`

### Common Issues
1. **Password hash missing**: Run migration script again
2. **Permission denied**: Check file permissions (should be 600)
3. **DB connection failed**: Verify PostgreSQL is running and credentials are correct

## Rollback

If needed, restore legacy configs:
```bash
sudo cp /etc/postfix/virtual_mailboxes.cf.backup /etc/postfix/virtual_mailboxes.cf
sudo cp /etc/postfix/virtual_domains.cf.backup /etc/postfix/virtual_domains.cf
sudo cp /etc/postfix/virtual_aliases.cf.backup /etc/postfix/virtual_aliases.cf
sudo cp /etc/dovecot/dovecot-sql.conf.ext.backup /etc/dovecot/dovecot-sql.conf.ext
sudo postfix reload
sudo systemctl restart dovecot
```

