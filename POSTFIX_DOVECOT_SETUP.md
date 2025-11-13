# Using Postfix + Dovecot with Django

## ✅ **Perfect Setup!**

You already have **Postfix** (SMTP) and **Dovecot** (IMAP) running on your server. This is the **ideal setup** for Django email operations!

## 🎯 **Architecture**

```
Django App → Postfix (SMTP) → Internet
Django App → Dovecot (IMAP) ← Internet
```

**Direct connection to your email servers!**

## 🔧 **Configuration**

### **1. Postfix (SMTP - Sending Emails)**

Postfix typically runs on:
- **Port 25**: Local relay (no auth needed)
- **Port 587**: Submission port (with auth)

For Django, use **port 25** for localhost connections (simplest):

```python
# settings.py
EMAIL_HOST = 'localhost'  # Postfix on same server
EMAIL_PORT = 25           # Postfix default relay port
EMAIL_USE_TLS = False     # Not needed for localhost:25
EMAIL_HOST_USER = ''      # Empty for localhost relay
EMAIL_HOST_PASSWORD = ''  # Empty for localhost relay
```

### **2. Dovecot (IMAP - Receiving Emails)**

Dovecot typically runs on:
- **Port 143**: Plain IMAP
- **Port 993**: IMAP over SSL

For Django, use **port 143** for localhost (or 993 with SSL):

```python
# settings.py
EMAIL_IMAP_HOST = 'localhost'  # Dovecot on same server
EMAIL_IMAP_PORT = 143          # Plain IMAP (or 993 for SSL)
EMAIL_IMAP_USE_SSL = False     # True for port 993, False for 143
```

## 📝 **Email Account Setup**

### **1. Create Email Account in Django**

```python
from mail.models import EmailAccount, Domain, Organization

# Get or create domain
domain = Domain.objects.get_or_create(name='fayvad.com')[0]

# Get user's organization
org = request.user.organization

# Create email account
email_account = EmailAccount.objects.create(
    user=request.user,
    organization=org,
    domain=domain,
    email='d.kuria@fayvad.com',
    first_name='David',
    last_name='Kuria',
    is_active=True
)
```

### **2. Create Corresponding System User**

Postfix/Dovecot need system users. Create them:

```bash
# Create system user for email account
sudo useradd -m -s /bin/bash d.kuria
sudo passwd d.kuria  # Set password: MeMiMo@0207

# Or use existing user if already created
```

### **3. Configure Postfix for Virtual Mailboxes**

If using virtual mailboxes (recommended), configure Postfix:

```bash
# /etc/postfix/main.cf
virtual_mailbox_domains = mysql:/etc/postfix/mysql-virtual-mailbox-domains.cf
virtual_mailbox_maps = mysql:/etc/postfix/mysql-virtual-mailbox-maps.cf
virtual_alias_maps = mysql:/etc/postfix/mysql-virtual-alias-maps.cf
```

Or use simple local delivery:

```bash
# /etc/postfix/main.cf
mydestination = $myhostname, localhost.$mydomain, localhost, fayvad.com
```

### **4. Configure Dovecot**

```bash
# /etc/dovecot/dovecot.conf
mail_location = maildir:~/Maildir
protocols = imap
```

## 🚀 **Usage**

### **Send Email**

```python
from mail.services import DjangoEmailService
from mail.models import EmailAccount

# Get email account
email_account = EmailAccount.objects.get(email='d.kuria@fayvad.com')

# Initialize service
email_service = DjangoEmailService(email_account)

# Send email
result = email_service.send_email(
    to_emails=['recipient@example.com'],
    subject='Hello from Django',
    body_text='Plain text body',
    body_html='<p>HTML body</p>'
)

if result['success']:
    print("Email sent via Postfix!")
```

### **Receive Email**

```python
# Receive emails from Dovecot
result = email_service.receive_emails(folder_name='INBOX', limit=50)

if result['success']:
    print(f"Synced {result['count']} emails from Dovecot")
```

### **Sync Emails (Cron Job)**

```bash
# Add to crontab
*/5 * * * * cd /path/to/project && python manage.py sync_emails --email d.kuria@fayvad.com
```

## 🔍 **Testing**

### **Test Postfix Connection**

```bash
# Test SMTP connection
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test body', 'd.kuria@fayvad.com', ['test@example.com'])
```

### **Test Dovecot Connection**

```bash
# Test IMAP connection
python manage.py shell
>>> from mail.services import DjangoEmailService
>>> from mail.models import EmailAccount
>>> account = EmailAccount.objects.get(email='d.kuria@fayvad.com')
>>> service = DjangoEmailService(account)
>>> result = service.receive_emails(limit=5)
>>> print(result)
```

## 📊 **Benefits**

| Feature | Postfix/Dovecot | External API | AWS SES |
|---------|----------------|-------------|---------|
| **Cost** | ✅ Free | ✅ Free | ⚠️ Pay per email |
| **Control** | ✅ Full | ⚠️ Limited | ❌ None |
| **Setup** | ⚠️ Medium | ❌ Complex | ✅ Easy |
| **Reliability** | ✅ High | ⚠️ Variable | ✅ High |
| **Local** | ✅ Yes | ✅ Yes | ❌ No |

## 🔐 **Security Considerations**

1. **Postfix**: Configure `mynetworks` to allow only localhost
2. **Dovecot**: Use SSL (port 993) for production
3. **Passwords**: Store encrypted in Django database
4. **Firewall**: Only expose necessary ports

## 🎯 **Recommended Configuration**

### **Development (localhost)**

```python
# settings.py
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

EMAIL_IMAP_HOST = 'localhost'
EMAIL_IMAP_PORT = 143
EMAIL_IMAP_USE_SSL = False
```

### **Production (with SSL)**

```python
# settings.py
EMAIL_HOST = 'localhost'
EMAIL_PORT = 587  # Submission port
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'd.kuria@fayvad.com'
EMAIL_HOST_PASSWORD = 'encrypted_password'

EMAIL_IMAP_HOST = 'localhost'
EMAIL_IMAP_PORT = 993  # IMAP over SSL
EMAIL_IMAP_USE_SSL = True
```

## ✅ **Next Steps**

1. ✅ Configuration updated in `settings.py`
2. ✅ Email service supports Postfix/Dovecot
3. ⏭️ Test Postfix connection
4. ⏭️ Test Dovecot connection
5. ⏭️ Create email accounts in Django
6. ⏭️ Set up email sync cron job
7. ✅ Django compose view implemented

---

**This is the simplest and most cost-effective approach!** 🎉

