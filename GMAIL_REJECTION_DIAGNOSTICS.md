# Gmail Email Rejection Diagnostics

## Common Reasons Gmail Rejects Emails

### 1. **Missing DKIM Signature** ⚠️ CRITICAL
**Status:** NOT IMPLEMENTED
- Gmail requires DKIM signatures for authentication
- Current code sends emails without DKIM signing
- **Fix:** Implement DKIM signing in email backend or use Postfix/Dovecot DKIM

### 2. **SPF Record Issues**
**Check:**
```bash
dig TXT fayvad.com | grep spf
```
**Should include:** `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all`
- Must authorize sending IP/server
- Use `~all` (soft fail) initially, not `-all` (hard fail)

### 3. **DMARC Policy**
**Check:**
```bash
dig TXT _dmarc.fayvad.com | grep dmarc
```
**Recommended:** `v=DMARC1; p=none; rua=mailto:admin@fayvad.com`
- Start with `p=none` (monitor only)
- Don't use `p=reject` until SPF/DKIM are working

### 4. **Reverse DNS (PTR Record)**
**Check:**
```bash
dig -x 167.86.95.242
```
**Should resolve to:** `mail.fayvad.com` or similar
- Gmail checks reverse DNS
- Missing PTR = likely rejection

### 5. **IP Reputation**
- Check if sending IP is blacklisted: https://mxtoolbox.com/blacklists.aspx
- New IPs need time to build reputation
- Shared IPs can have bad reputation

### 6. **From Address Mismatch**
- `From:` must match authenticated SMTP user
- Currently using: `self.email_address` ✅ (correct)

## Quick Diagnostic Steps

1. **Check email headers** in Gmail:
   - Open rejected email → Show original
   - Look for: `Authentication-Results`
   - Check: `spf=`, `dkim=`, `dmarc=` results

2. **Test SPF:**
```bash
dig TXT fayvad.com +short | grep spf
```

3. **Test DKIM:**
```bash
dig TXT mail._domainkey.fayvad.com +short
```

4. **Test DMARC:**
```bash
dig TXT _dmarc.fayvad.com +short
```

5. **Check reverse DNS:**
```bash
dig -x 167.86.95.242 +short
```

## Immediate Actions

1. ✅ **Verify SPF record exists and includes sending IP**
2. ⚠️ **Implement DKIM signing** (or configure Postfix to sign)
3. ✅ **Set DMARC to `p=none`** (monitor mode)
4. ✅ **Verify reverse DNS** points to mail server
5. ✅ **Check IP reputation** on blacklist sites

## Notes

- **DKIM signing** is typically handled by Postfix/Dovecot, not Django
- If using Postfix, ensure DKIM is configured there
- Django just needs to send via authenticated SMTP
- Postfix should add DKIM signature before relaying

