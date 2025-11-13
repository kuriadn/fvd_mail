# Email Testing Guide

## Overview

This guide explains how to test email sending and receiving for `geo.fayvad.com` email accounts.

## Test Scenario

1. **kuria@geo.fayvad.com** → **admin@geo.fayvad.com** (Bootcamp inquiry)
2. **admin@geo.fayvad.com** → **services@geo.fayvad.com** (Forward)
3. **services@geo.fayvad.com** → **kuria@geo.fayvad.com** (Response, CC admin)

## Prerequisites

- Email accounts created and active
- Passwords available (from `email_passwords_geo_fayvad_com.txt`)
- SMTP server running on `mail.fayvad.com`
- Postfix configured and accepting connections
- Let's Encrypt certificate installed

## Testing Methods

### Method 1: Using Django Test Script

```bash
# From host (not Docker)
python3 test_email_simple.py
```

**Note:** This requires:
- SMTP server accessible from host
- Proper SSL certificate configuration
- Email credentials configured

### Method 2: Using Web Email Client

1. **Login to webmail:**
   - Go to: `https://mail.fayvad.com` (or your webmail URL)
   - Login as: `kuria@geo.fayvad.com`
   - Password: (from password file)

2. **Send email:**
   - Compose new email
   - To: `admin@geo.fayvad.com`
   - Subject: "Bootcamp Inquiry"
   - Body: (bootcamp inquiry message)
   - Send

3. **Check admin inbox:**
   - Login as: `admin@geo.fayvad.com`
   - Check inbox for email from kuria
   - Forward to: `services@geo.fayvad.com`

4. **Check services inbox:**
   - Login as: `services@geo.fayvad.com`
   - Check inbox for forwarded email
   - Reply to: `kuria@geo.fayvad.com`
   - CC: `admin@geo.fayvad.com`

5. **Verify delivery:**
   - Check kuria inbox for response
   - Check admin inbox for CC copy

### Method 3: Using Email Client (Thunderbird, Outlook, etc.)

**IMAP Settings:**
- Server: `mail.fayvad.com`
- Port: 993 (SSL) or 143 (TLS)
- Username: `kuria@geo.fayvad.com` (full email)
- Password: (from password file)

**SMTP Settings:**
- Server: `mail.fayvad.com`
- Port: 587 (TLS) or 465 (SSL)
- Username: `kuria@geo.fayvad.com` (full email)
- Password: (from password file)
- Authentication: Required
- Encryption: TLS/SSL

### Method 4: Using Command Line (swaks, mailx, etc.)

```bash
# Install swaks (Swiss Army Knife for SMTP)
# Ubuntu/Debian: sudo apt-get install swaks
# macOS: brew install swaks

# Send email from kuria to admin
swaks \
  --to admin@geo.fayvad.com \
  --from kuria@geo.fayvad.com \
  --server mail.fayvad.com \
  --port 587 \
  --auth LOGIN \
  --auth-user kuria@geo.fayvad.com \
  --auth-password 'PASSWORD_HERE' \
  --tls \
  --header "Subject: Bootcamp Inquiry" \
  --body "Dear Admin, I am writing to express my keen interest..."
```

## Email Accounts

From `email_passwords_geo_fayvad_com.txt`:

- **kuria@geo.fayvad.com**
  - Password: `*h^3mr0&N80b`
  
- **admin@geo.fayvad.com**
  - Password: `%PHg5JErPj*f`
  
- **services@geo.fayvad.com**
  - Password: `XXcKlXlH^%1I`

## Troubleshooting

### SSL Certificate Errors

If you see SSL certificate errors:

1. **Check certificate:**
   ```bash
   openssl s_client -connect mail.fayvad.com:587 -starttls smtp
   ```

2. **Verify certificate is valid:**
   - Should show Let's Encrypt certificate
   - Certificate chain should be complete

3. **For testing (not production):**
   - Can temporarily disable SSL verification
   - Not recommended for production use

### Connection Errors

If connection fails:

1. **Check mail server is running:**
   ```bash
   telnet mail.fayvad.com 587
   # or
   nc -zv mail.fayvad.com 587
   ```

2. **Check firewall:**
   - Port 587 (SMTP submission) should be open
   - Port 993 (IMAP SSL) should be open
   - Port 143 (IMAP TLS) should be open

3. **Check Postfix configuration:**
   - Postfix should be listening on port 587
   - SASL authentication should be enabled
   - TLS should be configured

### Authentication Errors

If authentication fails:

1. **Verify passwords:**
   - Check password file
   - Ensure passwords are correct
   - Passwords may have been reset

2. **Check Dovecot authentication:**
   - Dovecot should be configured for SASL
   - Password hashes should match

3. **Check email account status:**
   ```python
   python manage.py shell
   >>> from mail.models import EmailAccount
   >>> EmailAccount.objects.filter(email='kuria@geo.fayvad.com').first().is_active
   ```

## Verification Checklist

- [ ] Email sent from kuria to admin
- [ ] Email received in admin inbox
- [ ] Email forwarded from admin to services
- [ ] Email received in services inbox
- [ ] Response sent from services to kuria (CC admin)
- [ ] Response received in kuria inbox
- [ ] CC copy received in admin inbox

## Next Steps

After successful testing:

1. Document any issues found
2. Update email configuration if needed
3. Set up email monitoring/alerts
4. Configure email backups
5. Set up email archiving (if required)

## Security Notes

- **Never commit password files to git**
- **Use secure password storage in production**
- **Enable SPF, DKIM, DMARC** (already configured)
- **Use TLS/SSL for all connections**
- **Regularly update passwords**
- **Monitor email logs for suspicious activity**

