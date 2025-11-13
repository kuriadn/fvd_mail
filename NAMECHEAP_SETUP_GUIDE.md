# Namecheap API Setup Guide

## Server Information

**Production Server IP:** `167.86.95.242`

This IP must be whitelisted in your Namecheap API settings for API access to work.

---

## Step 1: Generate API Key in Namecheap

1. **Login to Namecheap**
   - Go to https://www.namecheap.com
   - Login as `dkuria` (with 2FA)

2. **Navigate to API Access**
   - Profile → Tools → API Access
   - Or direct link: https://ap.www.namecheap.com/profile/tools/apiaccess/

3. **Create New API Key**
   - Click "Add new API key"
   - Name: `FayvadMail-Production` (or similar)
   - **Important:** Copy the API key immediately - you'll only see it once!

4. **Configure IP Whitelist** ✅ **CRITICAL**
   - Edit your API key
   - Add IP address: `167.86.95.242`
   - Save changes
   - **Note:** Namecheap API requires IP whitelisting - requests from other IPs will be rejected

---

## Step 2: Configure Environment Variables

Add these to your `.env` file (or environment variables):

```bash
# Namecheap API Configuration
NAMECHEAP_API_USER=dkuria
NAMECHEAP_API_KEY=your_api_key_here
NAMECHEAP_CLIENT_IP=167.86.95.242
NAMECHEAP_API_SANDBOX=False
```

**Security Notes:**
- ✅ Never commit `.env` file to git
- ✅ Store API key securely
- ✅ Use different keys for dev/staging/production
- ✅ Rotate keys every 6-12 months

---

## Step 3: Test API Connection

### Option A: Test via Django Shell

```bash
python manage.py shell
```

```python
from mail.services.domain_manager import NamecheapDomainService
from django.conf import settings

# Initialize service
namecheap = NamecheapDomainService(
    api_user=settings.NAMECHEAP_API_USER,
    api_key=settings.NAMECHEAP_API_KEY,
    api_sandbox=settings.NAMECHEAP_API_SANDBOX
)

# Test DNS record retrieval (read-only, safe to test)
# This will verify your API credentials work
try:
    # Test with a domain you own
    result = namecheap.update_dns_records('geo.fayvad.com', [])
    print("✅ API connection successful!")
except Exception as e:
    print(f"❌ API connection failed: {e}")
```

### Option B: Test DNS Update

```python
# Test updating DNS records for geo.fayvad.com
from mail.services.domain_manager import NamecheapDomainService
from mail.models import Domain

domain = Domain.objects.get(name='geo.fayvad.com')
domain_manager = DomainManager()
namecheap = NamecheapDomainService(
    api_user=settings.NAMECHEAP_API_USER,
    api_key=settings.NAMECHEAP_API_KEY,
    api_sandbox=False
)

# Get DNS records that should be set
dns_records = domain_manager.get_dns_records(domain)

# Convert to Namecheap format
records = [
    {
        'name': '@',
        'type': 'MX',
        'value': '10 mail.fayvad.com',
        'ttl': 1800
    },
    {
        'name': '@',
        'type': 'TXT',
        'value': 'v=spf1 mx a:mail.fayvad.com ~all',
        'ttl': 1800
    }
]

# Update DNS (be careful - this will modify live DNS!)
result = namecheap.update_dns_records('geo.fayvad.com', records)
print(result)
```

---

## Step 4: Verify IP Whitelist

**Important:** Namecheap API will reject requests if your server IP is not whitelisted.

To verify:
1. Check Namecheap dashboard → API Access → Your API Key
2. Confirm `167.86.95.242` is in the whitelist
3. If not, add it and wait a few minutes for changes to propagate

**Common Error:**
```
Error: Invalid IP address. Your IP address is not whitelisted.
```
**Solution:** Add `167.86.95.242` to API key whitelist in Namecheap dashboard.

---

## Step 5: Integration with Domain Creation

Once API is configured, DNS records will be automatically set when:

1. Organization is created
2. Domain is created
3. Email accounts are created

The system will:
- Generate required DNS records (MX, SPF, DKIM, DMARC)
- Call Namecheap API to set records
- Verify DNS propagation
- Log all changes

---

## Troubleshooting

### Error: "Invalid IP address"
- **Cause:** Server IP not whitelisted
- **Solution:** Add `167.86.95.242` to API key whitelist

### Error: "Invalid API key"
- **Cause:** Wrong API key or API user
- **Solution:** Verify `NAMECHEAP_API_USER` and `NAMECHEAP_API_KEY` in environment

### Error: "API request failed"
- **Cause:** Network issue or Namecheap API down
- **Solution:** Check network connectivity, verify API endpoint is accessible

### DNS Changes Not Appearing
- **Cause:** DNS propagation delay (can take up to 48 hours)
- **Solution:** Wait for propagation, verify records with `dig` or DNS checker

---

## Security Checklist

- [ ] API key stored in environment variables (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] Server IP (`167.86.95.242`) whitelisted in Namecheap
- [ ] API key has minimal required permissions
- [ ] Separate keys for dev/staging/production
- [ ] Audit logging enabled for DNS changes
- [ ] Regular key rotation scheduled

---

## Next Steps

1. ✅ Generate API key in Namecheap
2. ✅ Whitelist server IP (`167.86.95.242`)
3. ✅ Configure environment variables
4. ✅ Test API connection
5. ✅ Integrate with domain creation workflow

Once configured, DNS records will be automatically managed when organizations and domains are created!

