# Guide: Adding Missing DNS Records for Email Authentication

## Purpose
Add SPF, DKIM, DMARC, and MX records to Namecheap DNS for email domains without overwriting existing records.

## Prerequisites
1. Django environment set up (virtualenv or Docker)
2. Namecheap API credentials configured:
   - `NAMECHEAP_API_USER`
   - `NAMECHEAP_API_KEY`
   - `NAMECHEAP_CLIENT_IP` (your server IP: 167.86.95.242)

## Usage

### Preview Changes (Dry Run)
```bash
# Preview for single domain
python add_missing_dns_records.py fayvad.com --dry-run

# Preview for all domains
python add_missing_dns_records.py all --dry-run
```

### Apply Changes
```bash
# Add missing records for single domain
python add_missing_dns_records.py fayvad.com

# Add missing records for all domains
python add_missing_dns_records.py all
```

## What It Does

For each domain, the script:
1. ✅ Checks existing DNS records from Namecheap
2. ✅ Identifies missing records:
   - **SPF** (TXT record at `@`)
   - **DKIM** (TXT record at `mail._domainkey`)
   - **DMARC** (TXT record at `_dmarc`)
   - **MX** (MX record at `@`)
3. ✅ Adds only missing records
4. ✅ Preserves all existing records

## Domains That Need DNS Records

Both domains need DNS records if emails are sent from them:
- **fayvad.com** - For emails like `d.kuria@fayvad.com`
- **geo.fayvad.com** - For emails like `user@geo.fayvad.com`

## DNS Records That Will Be Added

### SPF Record
```
Type: TXT
Name: @
Value: v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all
```

### DKIM Record
```
Type: TXT
Name: mail._domainkey (or selector from database)
Value: (DKIM public key from database)
```

### DMARC Record
```
Type: TXT
Name: _dmarc
Value: v=DMARC1; p=none; rua=mailto:admin@<domain>; ruf=mailto:admin@<domain>; fo=1
```

### MX Record
```
Type: MX
Name: @
Priority: 10
Value: mail.fayvad.com
```

## Important Notes

1. **Reverse DNS**: Must be configured with hosting provider (not Namecheap)
   - IP: `167.86.95.242`
   - Should resolve to: `mail.fayvad.com`

2. **DNS Propagation**: Changes take 5-30 minutes to propagate

3. **DKIM Keys**: Must be generated first if not in database
   - Run: `python generate_dkim_keys.py <domain>`

4. **Safety**: Script preserves all existing DNS records
   - Only adds missing email-related records
   - Never overwrites existing records

## Troubleshooting

### "Namecheap API not configured"
- Set environment variables or add to `.env` file
- Ensure server IP is whitelisted in Namecheap API settings

### "Domain not found in database"
- Create domain in Django admin first
- Or run: `python generate_dns_records.py <domain>` to create domain

### "DKIM not configured"
- Generate DKIM keys: `python generate_dkim_keys.py <domain>`
- Then re-run the script


