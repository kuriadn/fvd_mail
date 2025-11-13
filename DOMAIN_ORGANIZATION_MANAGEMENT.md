# Domain and Organization Management

## 🎯 **Overview**

You can manage domains and organizations using:
1. **Django Models** - Store domain/organization data
2. **Management Commands** - Configure Postfix/Dovecot
3. **Namecheap API** - Domain registration (optional)
4. **DNS Management** - SPF, DKIM, DMARC configuration

---

## 📊 **Architecture**

```
Django Admin Portal
    ↓
Django Models (Domain, Organization, EmailAccount)
    ↓
Management Commands
    ↓
Postfix/Dovecot Configuration
    ↓
Email Server (Postfix/Dovecot)
```

**Direct Django integration!**

---

## 🏗️ **Components**

### **1. Django Models** ✅ (Already Exist)

- `Organization` - Business clients
- `Domain` - Email domains
- `EmailAccount` - Email accounts
- `DomainDKIM` - DKIM configuration

### **2. Domain Manager Service** ✅ (Created)

`mail/services/domain_manager.py` provides:
- `create_domain()` - Create domain + configure Postfix/Dovecot
- `create_email_account()` - Create account + configure mailboxes
- `get_dns_records()` - Get DNS records needed
- `verify_dns()` - Verify DNS configuration

### **3. Management Commands** ✅ (Created)

- `python manage.py create_domain` - Create domain
- `python manage.py create_email_account` - Create email account

### **4. Namecheap Integration** ✅ (Created)

`NamecheapDomainService` for domain registration (optional)

---

## 🚀 **Usage**

### **Create Organization**

```python
from organizations.models import Organization

org = Organization.objects.create(
    name='Acme Corporation',
    domain_name='acme.com',
    max_users=50,
    max_storage_gb=100,
    is_active=True
)
```

### **Create Domain**

```bash
# Via management command
python manage.py create_domain acme.com --organization-id 1

# Or via Django
from mail.models import Domain
from mail.services.domain_manager import DomainManager

domain_manager = DomainManager()
domain = domain_manager.create_domain(
    domain_name='acme.com',
    organization=org,
    quota=0,  # Unlimited
    default_mailbox_quota=1024  # 1GB per mailbox
)
```

**What this does:**
1. ✅ Creates `Domain` in Django database
2. ✅ Configures Postfix virtual domain
3. ✅ Configures Dovecot domain
4. ✅ Generates DKIM keys
5. ✅ Creates mail directory structure

### **Create Email Account**

```bash
# Via management command
python manage.py create_email_account john@acme.com \
    --password secret123 \
    --user-id 1 \
    --organization-id 1 \
    --first-name John \
    --last-name Doe

# Or via Django
from mail.services.domain_manager import DomainManager

domain_manager = DomainManager()
account = domain_manager.create_email_account(
    email='john@acme.com',
    password='secret123',
    domain=domain,
    user=user,
    organization=org,
    first_name='John',
    last_name='Doe',
    quota_mb=2048  # 2GB
)
```

**What this does:**
1. ✅ Creates `EmailAccount` in Django database
2. ✅ Creates system user (if needed)
3. ✅ Configures Postfix virtual mailbox
4. ✅ Configures Dovecot mailbox
5. ✅ Creates Maildir structure

---

## 🌐 **DNS Configuration**

### **Get DNS Records**

```python
from mail.services.domain_manager import DomainManager

domain_manager = DomainManager()
dns_records = domain_manager.get_dns_records(domain)

# Returns:
# {
#     'MX': {'name': 'acme.com', 'type': 'MX', 'priority': 10, 'value': 'mail.fayvad.com'},
#     'SPF': {'name': 'acme.com', 'type': 'TXT', 'value': 'v=spf1 mx a:mail.fayvad.com ~all'},
#     'DKIM': {'name': 'mail._domainkey.acme.com', 'type': 'TXT', 'value': '...'},
#     'DMARC': {'name': '_dmarc.acme.com', 'type': 'TXT', 'value': 'v=DMARC1; p=none; ...'}
# }
```

### **Verify DNS**

```python
dns_status = domain_manager.verify_dns(domain)

# Returns:
# {
#     'MX': {'configured': True, 'records': ['10 mail.fayvad.com']},
#     'SPF': {'configured': True, 'records': ['v=spf1 mx a:mail.fayvad.com ~all']},
#     'DKIM': {'configured': False, 'records': []}
# }
```

---

## 🏢 **Admin Portal Integration**

### **Example Implementation**

**Previous approach:**
```python
# admin_portal/views.py
# Previous approach using external API
created_org = external_api_client.create_organization(token, org_data)
```

**Current approach:**
```python
# admin_portal/views.py
from organizations.models import Organization
from mail.services.domain_manager import DomainManager

# Create organization
org = Organization.objects.create(
    name=form.cleaned_data['name'],
    domain_name=form.cleaned_data['domain_name'],
    max_users=form.cleaned_data['max_users'],
    max_storage_gb=form.cleaned_data['max_storage_gb'],
    is_active=True
)

# Create domain
domain_manager = DomainManager()
domain = domain_manager.create_domain(
    domain_name=form.cleaned_data['domain_name'],
    organization=org
)
```

---

## 📋 **Complete Workflow**

### **1. Create Organization**

```python
org = Organization.objects.create(
    name='Rental Properties Ltd',
    domain_name='rentalproperties.co.ke',
    max_users=20,
    max_storage_gb=50
)
```

### **2. Create Domain**

```bash
python manage.py create_domain rentalproperties.co.ke --organization-id 1
```

### **3. Configure DNS**

Add DNS records from `get_dns_records()` to domain registrar (Namecheap, etc.)

### **4. Create Email Accounts**

```bash
python manage.py create_email_account admin@rentalproperties.co.ke \
    --password secure123 \
    --organization-id 1 \
    --first-name Admin \
    --last-name User
```

### **5. Verify Setup**

```python
domain_manager.verify_dns(domain)  # Check DNS
# Test email sending/receiving
```

---

## 🔧 **Postfix Configuration**

The domain manager automatically configures:

### **Virtual Mailbox Domains**

`/etc/postfix/virtual_mailbox_domains`:
```
acme.com OK
rentalproperties.co.ke OK
```

### **Virtual Mailboxes**

`/etc/postfix/virtual_mailboxes`:
```
admin@acme.com acme.com/admin/
john@acme.com acme.com/john/
```

### **Reload Postfix**

```bash
sudo postfix reload
```

---

## 📁 **Dovecot Configuration**

The domain manager automatically creates:

### **Mail Directory Structure**

```
/var/mail/vhosts/
├── acme.com/
│   ├── admin/
│   │   ├── cur/
│   │   ├── new/
│   │   └── tmp/
│   └── john/
│       ├── cur/
│       ├── new/
│       └── tmp/
└── rentalproperties.co.ke/
    └── admin/
        ├── cur/
        ├── new/
        └── tmp/
```

---

## 🌐 **Namecheap Integration (Optional)**

### **Register Domain**

```python
from mail.services.domain_manager import NamecheapDomainService

namecheap = NamecheapDomainService(
    api_user='your_username',
    api_key='your_api_key',
    api_sandbox=True  # False for production
)

result = namecheap.register_domain(
    domain_name='example.com',
    years=1,
    first_name='John',
    last_name='Doe',
    email='admin@example.com',
    # ... other registration details
)
```

### **Update DNS Records**

```python
dns_records = [
    {'name': '@', 'type': 'MX', 'value': '10 mail.fayvad.com'},
    {'name': '@', 'type': 'TXT', 'value': 'v=spf1 mx a:mail.fayvad.com ~all'},
    # ... more records
]

namecheap.update_dns_records('example.com', dns_records)
```

---

## ✅ **Benefits**

| Feature | External API | Django + Postfix/Dovecot |
|---------|---------|--------------------------|
| **Domain Management** | Via API | Direct Django models |
| **Account Creation** | Via API | Management commands |
| **DNS Configuration** | Manual | Automated + Namecheap API |
| **Postfix Config** | Via external API | Direct configuration |
| **Dovecot Config** | Via external API | Direct configuration |
| **Control** | Limited | Full control |
| **Complexity** | High | Low |
| **Reliability** | Variable | High |

---

## 🎯 **Next Steps**

1. ✅ Domain manager service created
2. ✅ Management commands created
3. ⏭️ Update admin portal views to use Django models
4. ⏭️ Test domain creation
5. ⏭️ Test email account creation
6. ⏭️ Configure Namecheap API (optional)
7. ✅ All dependencies removed

---

## 📝 **Example: Complete Setup**

```python
# 1. Create organization
org = Organization.objects.create(
    name='My Business',
    domain_name='mybusiness.co.ke',
    max_users=10,
    max_storage_gb=50
)

# 2. Create domain
from mail.services.domain_manager import DomainManager
domain_manager = DomainManager()
domain = domain_manager.create_domain('mybusiness.co.ke', org)

# 3. Get DNS records
dns_records = domain_manager.get_dns_records(domain)
# Configure these in Namecheap or your registrar

# 4. Create email accounts
account = domain_manager.create_email_account(
    email='admin@mybusiness.co.ke',
    password='secure123',
    domain=domain,
    user=user,
    organization=org
)

# 5. Verify DNS
dns_status = domain_manager.verify_dns(domain)
```

**That's it! Direct Django integration!** 🎉

