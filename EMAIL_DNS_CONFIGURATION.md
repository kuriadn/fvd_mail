# Email DNS Configuration Guide

## Mail Server Configuration

**Mail Server Hostname:** `mail.fayvad.com`  
**Mail Server IP:** `167.86.95.242`  
**Root Domain:** `fayvad.com`

---

## Required DNS Records for Email

When setting up email for a domain (e.g., `geo.fayvad.com`), the following DNS records must be configured:

### 1. **MX Record** (Mail Exchange) ✅ Required

**Purpose:** Tells other mail servers where to deliver email for your domain.

**Record:**
```
Type: MX
Name: @ (or domain name)
Priority: 10
Value: mail.fayvad.com
```

**Example for geo.fayvad.com:**
```
Type: MX
Name: geo.fayvad.com
Priority: 10
Value: mail.fayvad.com
```

**DNS Format:**
```
geo.fayvad.com.  IN  MX  10  mail.fayvad.com.
```

---

### 2. **SPF Record** (Sender Policy Framework) ✅ Required

**Purpose:** Authorizes which servers can send email on behalf of your domain.

**Record:**
```
Type: TXT
Name: @ (or domain name)
Value: v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all
```

**Example for geo.fayvad.com:**
```
Type: TXT
Name: geo.fayvad.com
Value: v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all
```

**Explanation:**
- `v=spf1` - SPF version 1
- `mx` - Allow mail servers listed in MX records
- `a:mail.fayvad.com` - Allow mail.fayvad.com A record
- `ip4:167.86.95.242` - Allow specific IP address
- `~all` - Soft fail for other servers (use `-all` for hard fail in production)

---

### 3. **DKIM Record** (DomainKeys Identified Mail) ✅ Recommended

**Purpose:** Cryptographically signs emails to prove they came from your domain.

**Record:**
```
Type: TXT
Name: mail._domainkey.geo.fayvad.com
Value: v=DKIM1; k=rsa; p=<public_key>
```

**Example:**
```
Type: TXT
Name: mail._domainkey.geo.fayvad.com
Value: v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC...
```

**How to Generate:**
1. DKIM keys are generated automatically when domain is created
2. Keys are stored in `DomainDKIM` model
3. Public key is extracted and formatted for DNS

**Note:** The selector (`mail`) can be customized per domain.

---

### 4. **DMARC Record** (Domain-based Message Authentication) ✅ Recommended

**Purpose:** Policy for handling emails that fail SPF/DKIM checks.

**Record:**
```
Type: TXT
Name: _dmarc.geo.fayvad.com
Value: v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com; ruf=mailto:admin@geo.fayvad.com; fo=1
```

**Example:**
```
Type: TXT
Name: _dmarc.geo.fayvad.com
Value: v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com; ruf=mailto:admin@geo.fayvad.com; fo=1
```

**Policy Options:**
- `p=none` - Monitor only (recommended for initial setup)
- `p=quarantine` - Quarantine failed emails
- `p=reject` - Reject failed emails (strictest)

**Reporting:**
- `rua=mailto:...` - Aggregate reports
- `ruf=mailto:...` - Forensic reports
- `fo=1` - Generate reports for all failures

---

### 5. **A Record for Mail Server** ✅ Required (on root domain)

**Purpose:** Resolves `mail.fayvad.com` to IP address.

**Record (on fayvad.com):**
```
Type: A
Name: mail
Value: 167.86.95.242
```

**DNS Format:**
```
mail.fayvad.com.  IN  A  167.86.95.242
```

**Note:** This is set on the **root domain** (`fayvad.com`), not on subdomains.

---

## Complete DNS Configuration Example

### For Domain: `geo.fayvad.com`

**Records to add:**

1. **MX Record**
   ```
   Type: MX
   Name: geo.fayvad.com
   Priority: 10
   Value: mail.fayvad.com
   ```

2. **SPF Record**
   ```
   Type: TXT
   Name: geo.fayvad.com
   Value: v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all
   ```

3. **DKIM Record** (if DKIM is enabled)
   ```
   Type: TXT
   Name: mail._domainkey.geo.fayvad.com
   Value: v=DKIM1; k=rsa; p=<public_key>
   ```

4. **DMARC Record**
   ```
   Type: TXT
   Name: _dmarc.geo.fayvad.com
   Value: v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com; ruf=mailto:admin@geo.fayvad.com; fo=1
   ```

### For Root Domain: `fayvad.com`

**Records to add:**

1. **A Record for Mail Server**
   ```
   Type: A
   Name: mail
   Value: 167.86.95.242
   ```

---

## Automated Configuration

### Using Django Code

```python
from mail.services.domain_manager import DomainManager
from mail.models import Domain

domain = Domain.objects.get(name='geo.fayvad.com')
domain_manager = DomainManager()

# Get DNS records
dns_records = domain_manager.get_dns_records(domain)

# Print records
for record_type, record in dns_records.items():
    print(f"{record_type}:")
    print(f"  Name: {record['name']}")
    print(f"  Type: {record['type']}")
    print(f"  Value: {record['value']}")
    print()
```

### Using Namecheap API

```python
from mail.services.domain_manager import NamecheapDomainService, DomainManager
from mail.models import Domain

domain = Domain.objects.get(name='geo.fayvad.com')
domain_manager = DomainManager()
namecheap = NamecheapDomainService()

# Get DNS records
dns_records = domain_manager.get_dns_records(domain)

# Convert to Namecheap format
records = []
for record_type, record in dns_records.items():
    if record_type == 'MX':
        records.append({
            'name': '@',
            'type': 'MX',
            'value': f"{record['priority']} {record['value']}",
            'ttl': 1800
        })
    elif record_type == 'SPF':
        records.append({
            'name': '@',
            'type': 'TXT',
            'value': record['value'],
            'ttl': 1800
        })
    # ... etc

# Update DNS via Namecheap API
result = namecheap.update_dns_records('geo.fayvad.com', records)
```

---

## Verification

### Check DNS Records

```bash
# Check MX record
dig MX geo.fayvad.com

# Check SPF record
dig TXT geo.fayvad.com | grep spf

# Check DKIM record
dig TXT mail._domainkey.geo.fayvad.com

# Check DMARC record
dig TXT _dmarc.geo.fayvad.com

# Check mail server A record
dig A mail.fayvad.com
```

### Using Python

```python
from mail.services.domain_manager import DomainManager
from mail.models import Domain

domain = Domain.objects.get(name='geo.fayvad.com')
domain_manager = DomainManager()

# Verify DNS configuration
results = domain_manager.verify_dns(domain)

for record_type, result in results.items():
    if result.get('configured'):
        print(f"✅ {record_type}: Configured")
        print(f"   Records: {result.get('records', [])}")
    else:
        print(f"❌ {record_type}: Not configured")
```

---

## Settings Configuration

### Django Settings

```python
# In settings.py
MAIL_SERVER_HOSTNAME = 'mail.fayvad.com'
MAIL_SERVER_IP = '167.86.95.242'
```

### Environment Variables

```bash
# In .env file
MAIL_SERVER_HOSTNAME=mail.fayvad.com
MAIL_SERVER_IP=167.86.95.242
```

---

## Common Issues

### Issue: Emails going to spam

**Solutions:**
1. ✅ Ensure SPF record is configured correctly
2. ✅ Enable DKIM signing
3. ✅ Configure DMARC policy
4. ✅ Ensure reverse DNS (PTR) is set for mail server IP
5. ✅ Use proper email authentication

### Issue: Emails not being received

**Solutions:**
1. ✅ Verify MX record points to `mail.fayvad.com`
2. ✅ Check mail server A record resolves to `167.86.95.242`
3. ✅ Verify firewall allows SMTP connections (port 25)
4. ✅ Check mail server logs

### Issue: SPF validation failing

**Solutions:**
1. ✅ Ensure SPF record includes all sending IPs
2. ✅ Check SPF syntax (use SPF validator tools)
3. ✅ Verify `~all` vs `-all` policy (use `~all` initially)

---

## Best Practices

1. **Start with `p=none` for DMARC** - Monitor before enforcing
2. **Use `~all` for SPF initially** - Soft fail before hard fail
3. **Generate DKIM keys per domain** - Better security isolation
4. **Monitor DMARC reports** - Review regularly
5. **Test before production** - Use email testing tools
6. **Keep records updated** - Update when mail server changes

---

## Testing Tools

- **SPF Validator:** https://www.spf-record.com/
- **DKIM Validator:** https://dkimvalidator.com/
- **DMARC Analyzer:** https://dmarcian.com/dmarc-xml/
- **MX Toolbox:** https://mxtoolbox.com/

---

## Summary

**Required Records:**
- ✅ MX: `mail.fayvad.com` (priority 10)
- ✅ SPF: `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all`
- ✅ A Record: `mail.fayvad.com` → `167.86.95.242` (on root domain)

**Recommended Records:**
- ✅ DKIM: Domain-specific public key
- ✅ DMARC: Policy with reporting

**Configuration:**
- Mail server: `mail.fayvad.com`
- Mail IP: `167.86.95.242`
- Root domain: `fayvad.com`

All DNS records are automatically generated by `DomainManager.get_dns_records()` and can be configured via Namecheap API!

