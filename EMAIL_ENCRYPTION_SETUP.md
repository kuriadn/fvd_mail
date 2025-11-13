# Email Encryption Setup

## Current Issue

Emails are being sent **without encryption (TLS/SSL)**, which means:
- ❌ Email content is transmitted in **plaintext**
- ❌ Can be intercepted during transmission
- ❌ Gmail and other providers flag as "not encrypted"
- ❌ Security/privacy risk

## Solution: Enable TLS for SMTP

### Option 1: Use Submission Port (587) with STARTTLS (Recommended)

**Django Settings:**
```python
EMAIL_HOST = 'host.docker.internal'  # or 'localhost'
EMAIL_PORT = 587  # Submission port
EMAIL_USE_TLS = True  # Enable STARTTLS
EMAIL_HOST_USER = 'd.kuria@fayvad.com'  # SMTP auth username
EMAIL_HOST_PASSWORD = 'MeMiMo@0207'  # SMTP auth password
```

**Postfix Configuration:**
- Configure `submission` service in `/etc/postfix/master.cf`
- Enable SASL authentication
- Enable TLS/STARTTLS

### Option 2: Use SMTPS Port (465) with SSL

**Django Settings:**
```python
EMAIL_HOST = 'host.docker.internal'
EMAIL_PORT = 465  # SMTPS port
EMAIL_USE_SSL = True  # Enable SSL
EMAIL_HOST_USER = 'd.kuria@fayvad.com'
EMAIL_HOST_PASSWORD = 'MeMiMo@0207'
```

### Option 3: Use Port 25 with Opportunistic TLS (Current - Not Secure)

**Current Setup:**
- Port 25 (relay port)
- No TLS enforced
- No authentication required
- **Not secure** - emails sent in plaintext

## Recommended Configuration

### 1. Postfix Submission Service (Port 587)

Edit `/etc/postfix/master.cf`:
```
submission inet n       -       y       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_sasl_type=dovecot
  -o smtpd_sasl_path=private/auth
  -o smtpd_sasl_security_options=noanonymous
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject
  -o milter_macro_daemon_name=ORIGINATING
```

### 2. Django Settings Update

```python
# Use submission port with TLS
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'd.kuria@fayvad.com'
EMAIL_HOST_PASSWORD = 'MeMiMo@0207'
```

### 3. TLS Certificates

Postfix needs TLS certificates:
- Self-signed for development (acceptable)
- Let's Encrypt for production (recommended)

## Security Benefits

✅ **Encrypted transmission** - Email content protected
✅ **Authentication required** - Only authorized users can send
✅ **Provider trust** - Gmail/others won't flag as insecure
✅ **Privacy protection** - Content can't be intercepted

## Next Steps

1. Configure Postfix submission service (port 587)
2. Enable SASL authentication
3. Set up TLS certificates
4. Update Django settings to use port 587 with TLS
5. Test email sending with encryption

