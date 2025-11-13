# ⚠️ URGENT: DNS Records Restoration Needed

## Problem

When updating DNS for `geo.fayvad.com`, the Namecheap API `setHosts` command **REPLACED ALL DNS records** on `fayvad.com`, removing:

- ❌ `digital.fayvad.com` DNS records
- ❌ `mfariji.fayvad.com` DNS records  
- ❌ `geo.fayvad.com` website DNS records (A/CNAME)
- ❌ Any other subdomain DNS records

## Root Cause

The Namecheap API `setHosts` command **REPLACES ALL DNS records**, it doesn't merge them. When we called it with only the geo email records, it deleted everything else.

## Immediate Action Required

### Option 1: Restore from Namecheap Dashboard (FASTEST)

1. **Login to Namecheap**
   - Go to https://www.namecheap.com
   - Login as `dkuria`

2. **Check DNS Records**
   - Domain List → `fayvad.com` → Advanced DNS
   - See what records currently exist

3. **Restore Missing Records**

   **For digital.fayvad.com:**
   - Add A record or CNAME record for `digital` host
   - (You'll need to know the original IP/target)

   **For mfariji.fayvad.com:**
   - Add A record or CNAME record for `mfariji` host
   - (You'll need to know the original IP/target)

   **For geo.fayvad.com website:**
   - Add A record or CNAME record for `geo` host (if it had a website)
   - Note: Email records (MX, SPF, DKIM, DMARC) are already set

### Option 2: Check Namecheap DNS History

1. **Namecheap Dashboard**
   - Domain List → `fayvad.com` → Advanced DNS
   - Check if there's a "History" or "Backup" feature
   - Some DNS providers keep backups

### Option 3: Restore from Backup/Records

If you have:
- DNS backup files
- Previous DNS configuration exports
- Server logs showing DNS queries
- Email records of DNS changes

Use these to restore the missing records.

## Current DNS Records

Run this to see what's currently configured:

```bash
python restore_dns_records.py fayvad.com
```

## Prevention: Fixed Script

The `update_subdomain_dns.py` script has been updated to:
- ✅ Retrieve ALL existing DNS records BEFORE updating
- ✅ Preserve ALL non-email records
- ✅ Only replace email records for the specific subdomain being updated
- ✅ Warn if no existing records are found

## Next Steps

1. **Immediate:** Restore missing DNS records manually in Namecheap dashboard
2. **Verify:** Check that all subdomains work
3. **Test:** Use the fixed script with `--dry-run` before any future updates
4. **Document:** Keep a backup of DNS records for future reference

## DNS Records That Should Exist

Based on your report, these subdomains need DNS records:

### digital.fayvad.com
- Type: A or CNAME
- Host: `digital`
- Value: (original IP or target)

### mfariji.fayvad.com  
- Type: A or CNAME
- Host: `mfariji`
- Value: (original IP or target)

### geo.fayvad.com (website)
- Type: A or CNAME
- Host: `geo`
- Value: (original IP or target)
- Note: Email records (MX, SPF, DKIM, DMARC) are already configured

## Contact

If you need help restoring specific records, provide:
- Original IP addresses or targets for each subdomain
- Record types (A, CNAME, etc.)
- Any other DNS records that were lost

