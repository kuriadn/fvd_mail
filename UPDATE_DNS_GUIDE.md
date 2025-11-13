# DNS Records Update Guide

## Overview

This guide explains how to update DNS records (MX, SPF, DKIM, DMARC) for domains to use `mail.fayvad.com` as the mail server.

**Mail Server:** `mail.fayvad.com` (167.86.95.242)

---

## Quick Start

### Update Single Domain

```bash
# Preview changes (dry-run)
python update_dns_records.py geo.fayvad.com --dry-run

# Apply changes
python update_dns_records.py geo.fayvad.com
```

### Update All Domains

```bash
# Preview all changes
python update_dns_records.py --all --dry-run

# Apply to all domains
python update_dns_records.py --all
```

---

## What Gets Updated

### 1. **MX Record**
- **Old:** (whatever was configured)
- **New:** `mail.fayvad.com` (priority 10)

### 2. **SPF Record**
- **Old:** (existing SPF or none)
- **New:** `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all`

### 3. **DKIM Record**
- **Old:** (existing DKIM or none)
- **New:** Domain-specific DKIM key (if generated)

### 4. **DMARC Record**
- **Old:** (existing DMARC or none)
- **New:** `v=DMARC1; p=none; rua=mailto:admin@<domain>; ruf=mailto:admin@<domain>; fo=1`

---

## Safety Features

### ✅ **Preserves Non-Email Records**

The script automatically:
- Retrieves existing DNS records
- Identifies email-related records (MX, SPF, DKIM, DMARC)
- Preserves all non-email records (A, CNAME, etc.)
- Only updates email-related records

### ✅ **Dry-Run Mode**

Always test first:
```bash
python update_dns_records.py geo.fayvad.com --dry-run
```

This shows what would be changed **without making any changes**.

---

## Step-by-Step: Update geo.fayvad.com

### Step 1: Preview Changes

```bash
python update_dns_records.py geo.fayvad.com --dry-run
```

**Output shows:**
- Current DNS records
- New DNS records to be set
- What will be preserved
- What will be updated

### Step 2: Apply Changes

```bash
python update_dns_records.py geo.fayvad.com
```

**What happens:**
1. Generates DNS records for `mail.fayvad.com`
2. Retrieves existing DNS records
3. Merges them (preserves non-email records)
4. Updates via Namecheap API
5. Confirms success

### Step 3: Verify

```bash
# Check MX record
dig MX geo.fayvad.com

# Check SPF record
dig TXT geo.fayvad.com | grep spf

# Check DMARC record
dig TXT _dmarc.geo.fayvad.com
```

**Expected Results:**
- MX: `mail.fayvad.com` (priority 10)
- SPF: `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all`
- DMARC: `v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com...`

---

## Updating Multiple Domains

### Update All Enabled Domains

```bash
# Preview all
python update_dns_records.py --all --dry-run

# Apply to all
python update_dns_records.py --all
```

**Domains that will be updated:**
- All domains with `enabled=True` in database
- Domains that have organizations

---

## Troubleshooting

### Error: "IP address not whitelisted"

**Solution:**
1. Go to Namecheap → Profile → Tools → API Access
2. Edit your API key
3. Ensure `167.86.95.242` is whitelisted
4. Save and wait a few minutes

### Error: "Invalid API key"

**Solution:**
1. Check `.env` file has correct `NAMECHEAP_API_KEY`
2. Verify API key in Namecheap dashboard
3. Ensure API key is active

### Error: "Could not retrieve existing records"

**Warning:** This means the script cannot see existing DNS records.

**What happens:**
- Script will still update DNS
- **BUT** it will REPLACE ALL DNS records
- Non-email records may be lost

**Solution:**
- Check Namecheap API permissions
- Verify domain is registered with Namecheap
- Check API credentials

### DNS Changes Not Appearing

**Wait Time:**
- DNS changes can take 5 minutes to 48 hours to propagate
- Usually takes 15-30 minutes

**Verify:**
```bash
dig MX geo.fayvad.com
dig TXT geo.fayvad.com
```

---

## Example Output

```
======================================================================
DNS Records Update Tool
======================================================================
Mail Server: mail.fayvad.com
Mail IP: 167.86.95.242

======================================================================
Updating DNS for: geo.fayvad.com
======================================================================

📋 Generating DNS records...

📝 DNS Records to Configure:
  MX:    mail.fayvad.com (priority 10)
  SPF:   v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all
  DKIM:  Not configured (keys not generated)
  DMARC: v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com; ruf=mailto:admin@geo.fayvad.com; fo=1

📤 Records to send to Namecheap API: 3
  1. MX @: mail.fayvad.com...
  2. TXT @: v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all...
  3. TXT _dmarc: v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com...

🔍 Retrieving existing DNS records...
  ✅ Found 5 existing records
  Will preserve non-email records and update email records

🚀 Updating DNS records via Namecheap API...
  Merging: 5 existing + 3 new = 8 total records
✅ DNS records updated successfully

⏳ DNS changes may take a few minutes to propagate
   Verify with: dig MX geo.fayvad.com
```

---

## Important Notes

1. **Always use `--dry-run` first** to preview changes
2. **DNS propagation takes time** - be patient
3. **Non-email records are preserved** automatically
4. **DKIM requires keys** - generate them first if needed
5. **Verify after updating** - use `dig` commands

---

## Next Steps After Updating

1. **Wait for DNS propagation** (15-30 minutes)
2. **Verify DNS records** using `dig` commands
3. **Test email sending** from the domain
4. **Check email delivery** - ensure emails aren't going to spam
5. **Monitor DMARC reports** (if configured)

---

## Summary

**To update DNS for geo.fayvad.com:**

```bash
# 1. Preview
python update_dns_records.py geo.fayvad.com --dry-run

# 2. Apply
python update_dns_records.py geo.fayvad.com

# 3. Verify
dig MX geo.fayvad.com
dig TXT geo.fayvad.com
```

**All DNS records will be updated to use `mail.fayvad.com`!** ✅

