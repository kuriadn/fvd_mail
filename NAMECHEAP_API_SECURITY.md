# Namecheap API Security Guide

## Important: API Keys vs Web Login

### ⚠️ **Critical Security Understanding**

**Your web login with 2FA does NOT protect API access.**

Namecheap API uses **separate API keys** that bypass 2FA. This is by design - APIs need to work programmatically without human interaction.

### How Namecheap API Authentication Works

1. **Web Login** (what you use in browser)
   - Username: `dkuria`
   - Password: Your password
   - 2FA: ✅ Enabled (protects web access)
   - Used for: Dashboard, manual DNS changes

2. **API Access** (separate system)
   - API User: `dkuria` (same username)
   - API Key: Separate token generated in Namecheap dashboard
   - 2FA: ❌ **NOT used** (API keys bypass 2FA)
   - IP Whitelist: ✅ Required (only specific IPs can use API)
   - Used for: Programmatic DNS management

---

## Security Implications

### ✅ **What 2FA Protects:**
- Web dashboard login
- Manual DNS changes via browser
- Account settings changes
- Domain purchases/transfers

### ❌ **What 2FA Does NOT Protect:**
- API access using API keys
- Any programmatic changes via API
- Automated DNS updates

### 🔒 **API Key Security is Critical**

If someone gets your API key:
- They can modify DNS records
- They can manage domains
- They can bypass your 2FA protection
- **They DON'T need your password or 2FA code**

---

## Best Practices for API Key Security

### 1. **Generate Separate API Keys**

**Don't use your main account's API key for production.**

Instead:
- Create a dedicated API key for your Django application
- Give it a descriptive name: `"FayvadMail-Django-Production"`
- Set appropriate permissions (DNS management only, not domain purchases)

### 2. **IP Whitelisting** ✅ **CRITICAL**

Namecheap API **requires** IP whitelisting. This is your primary security layer:

```
✅ DO: Whitelist only your production server IPs
✅ DO: Use separate keys for dev/staging/production
❌ DON'T: Whitelist 0.0.0.0/0 (all IPs)
❌ DON'T: Use same key for dev and production
```

**How to set IP whitelist:**
1. Login to Namecheap → Profile → Tools → API Access
2. Edit your API key
3. Add your server's public IP address(es)
4. Save changes

### 3. **Secure Storage**

**Never commit API keys to git!**

```python
# ✅ GOOD: Environment variables
import os
NAMECHEAP_API_USER = os.getenv('NAMECHEAP_API_USER')
NAMECHEAP_API_KEY = os.getenv('NAMECHEAP_API_KEY')
NAMECHEAP_CLIENT_IP = os.getenv('NAMECHEAP_CLIENT_IP')  # Your server's IP

# ❌ BAD: Hardcoded in code
NAMECHEAP_API_KEY = "abc123xyz"  # NEVER DO THIS
```

**Store in:**
- Environment variables (`.env` file, not committed)
- Secret management service (AWS Secrets Manager, HashiCorp Vault)
- Docker secrets (if using Docker)
- CI/CD secret variables

### 4. **Principle of Least Privilege**

**Limit API key permissions:**
- ✅ Enable: DNS management
- ✅ Enable: Domain information (read-only)
- ❌ Disable: Domain purchases
- ❌ Disable: Domain transfers
- ❌ Disable: Account modifications

### 5. **Rotate API Keys Regularly**

- Generate new keys every 6-12 months
- Revoke old keys after rotation
- Update environment variables immediately

### 6. **Monitor API Usage**

- Check Namecheap API logs regularly
- Set up alerts for unusual activity
- Review DNS changes audit trail

---

## Implementation Security Checklist

### ✅ **Secure API Key Setup**

```python
# settings.py
import os

# Namecheap API Configuration
NAMECHEAP_API_USER = os.getenv('NAMECHEAP_API_USER', '')
NAMECHEAP_API_KEY = os.getenv('NAMECHEAP_API_KEY', '')
NAMECHEAP_CLIENT_IP = os.getenv('NAMECHEAP_CLIENT_IP', '')  # Your server IP
NAMECHEAP_API_SANDBOX = os.getenv('NAMECHEAP_API_SANDBOX', 'False').lower() == 'true'

# Validation
if not all([NAMECHEAP_API_USER, NAMECHEAP_API_KEY, NAMECHEAP_CLIENT_IP]):
    logger.warning("Namecheap API credentials not configured. DNS auto-configuration disabled.")
```

### ✅ **Secure Service Implementation**

```python
class NamecheapDomainService:
    def __init__(self):
        self.api_user = settings.NAMECHEAP_API_USER
        self.api_key = settings.NAMECHEAP_API_KEY
        self.client_ip = settings.NAMECHEAP_CLIENT_IP
        
        # Validate credentials
        if not all([self.api_user, self.api_key, self.client_ip]):
            raise ValueError("Namecheap API credentials not configured")
    
    def _make_api_request(self, command, params):
        """Make API request with security logging"""
        params.update({
            'ApiUser': self.api_user,
            'ApiKey': self.api_key,
            'UserName': self.api_user,
            'ClientIp': self.client_ip,  # Required by Namecheap
            'Command': command,
        })
        
        # Log request (without exposing API key)
        logger.info(f"Namecheap API request: {command} for IP {self.client_ip}")
        
        try:
            response = requests.get(self.base_url + '/xml.response', params=params)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Namecheap API error: {e}")
            raise
```

### ✅ **Error Handling**

```python
def update_dns_records(self, domain_name, records):
    """Update DNS records with security checks"""
    try:
        # Validate input
        if not domain_name or not records:
            raise ValueError("Domain name and records required")
        
        # Check IP whitelist (Namecheap will reject if IP not whitelisted)
        if not self.client_ip:
            raise ValueError("Client IP must be configured for API access")
        
        # Make API request
        result = self._make_api_request('namecheap.domains.dns.setHosts', {
            'SLD': domain_name.split('.')[0],
            'TLD': '.'.join(domain_name.split('.')[1:]),
            # ... DNS records
        })
        
        # Log success
        logger.info(f"DNS records updated for {domain_name} via Namecheap API")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Namecheap API request failed: {e}")
        # Don't expose API key in error messages
        raise Exception("DNS update failed. Please check API configuration.")
```

---

## Security Comparison

### Current Manual Approach
- ✅ 2FA protects web login
- ✅ You control when DNS changes happen
- ❌ Slower, manual process
- ❌ Not scalable

### Programmatic API Approach
- ✅ Fast, automated
- ✅ Scalable
- ⚠️ API keys bypass 2FA (by design)
- ✅ IP whitelisting provides security layer
- ✅ Can implement additional security (rate limiting, audit logs)

---

## Recommendations

### ✅ **Proceed with API Integration IF:**

1. **You can whitelist your server IPs**
   - Namecheap requires this anyway
   - This is your primary security layer

2. **You use secure credential storage**
   - Environment variables
   - Not in git repository
   - Rotated regularly

3. **You implement audit logging**
   - Log all DNS changes
   - Monitor for unusual activity
   - Review logs regularly

4. **You use separate API keys**
   - One for production
   - One for development/testing
   - Different permissions if possible

### ❌ **Consider Hybrid Approach IF:**

- You can't whitelist server IPs reliably
- You're concerned about API key security
- You want manual review of DNS changes

---

## Action Items

1. **Generate API Key:**
   - Login to Namecheap → Profile → Tools → API Access
   - Create new API key: `"FayvadMail-Production"`
   - Note the API key (you'll only see it once!)

2. **Configure IP Whitelist:**
   - **Production Server IP:** `167.86.95.242`
   - Add this IP to API key whitelist in Namecheap dashboard
   - **Critical:** API requests will fail without IP whitelisting

3. **Store Credentials Securely:**
   ```bash
   # .env file (NOT committed to git)
   NAMECHEAP_API_USER=dkuria
   NAMECHEAP_API_KEY=your_api_key_here
   NAMECHEAP_CLIENT_IP=167.86.95.242  # Production server IP
   ```

4. **Test in Sandbox:**
   - Use Namecheap sandbox API first
   - Test DNS updates
   - Verify security works

5. **Implement Audit Logging:**
   - Log all DNS changes
   - Include user ID, timestamp, domain, records changed

---

## Summary

**Yes, you can use Namecheap API with 2FA enabled on your web login.**

**However:**
- API keys are separate from web login
- API keys bypass 2FA (by design)
- IP whitelisting is your primary security layer
- Secure credential storage is critical
- Audit logging is essential

**The security model is:**
- Web login: Protected by 2FA ✅
- API access: Protected by IP whitelisting + secure API keys ✅

This is standard for API access - the security comes from IP restrictions and secure key management, not 2FA.

