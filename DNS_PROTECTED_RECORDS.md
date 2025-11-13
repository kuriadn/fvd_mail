# DNS Protected Records - Master Configuration Guide

## ⚠️ CRITICAL: Never Delete These Records

This document defines ALL DNS records that must be preserved. **Any DNS update script MUST preserve these records.**

---

## Server Information

- **Primary IP Address**: `167.86.95.242`
- **Mail Server Hostname**: `mail.fayvad.com`
- **Mail Server IP**: `167.86.95.242`

---

## Protected Domains and Subdomains

### Primary Domain
- **fayvad.com** (Root domain)

### Subdomains (MUST NEVER BE DELETED)
1. **geo.fayvad.com** - Geosolutions website + email
2. **digital.fayvad.com** - Digital services website + email
3. **mfariji.fayvad.com** - Mfariji website + email
4. **rental.fayvad.com** - Rental services website
5. **college.fayvad.com** - College services website
6. **driving.fayvad.com** - Driving services website + email

---

## Email-Enabled Domains

These domains have email services and require **MX, SPF, DKIM, DMARC** records:

1. **fayvad.com** ✅
2. **geo.fayvad.com** ✅
3. **digital.fayvad.com** ✅
4. **mfariji.fayvad.com** ✅
5. **driving.fayvad.com** ✅

**Note**: `rental.fayvad.com` and `college.fayvad.com` do NOT have email services.

---

## Complete DNS Configuration

### 1. fayvad.com (Root Domain)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `@` | A | `167.86.95.242` | 1800 | Root domain |
| `www` | A | `167.86.95.242` | 1800 | Main website |
| `mail` | A | `167.86.95.242` | 1800 | Mail server |

#### MX Records (Email)
| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `@` | MX | 10 | `mail.fayvad.com` | 1800 |

#### TXT Records (Email Authentication)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `@` | TXT | `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all` | 1800 |
| `mail._domainkey` | TXT | `v=DKIM1; k=rsa; p=<DKIM_PUBLIC_KEY>` | 1800 |
| `_dmarc` | TXT | `v=DMARC1; p=none; rua=mailto:admin@fayvad.com; ruf=mailto:admin@fayvad.com; fo=1` | 1800 |

---

### 2. geo.fayvad.com (Subdomain - Website + Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `geo` | A | `167.86.95.242` | 1800 | Geosolutions website |

**Note**: Must be A record (not CNAME) because it has email records.

#### MX Records (Email)
| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `geo` | MX | 10 | `mail.fayvad.com` | 1800 |

#### TXT Records (Email Authentication)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `geo` | TXT | `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all` | 1800 |
| `mail._domainkey.geo` | TXT | `v=DKIM1; k=rsa; p=<DKIM_PUBLIC_KEY>` | 1800 |
| `_dmarc.geo` | TXT | `v=DMARC1; p=none; rua=mailto:admin@geo.fayvad.com; ruf=mailto:admin@geo.fayvad.com; fo=1` | 1800 |

#### CNAME Records (Optional)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `www.geo` | CNAME | `geo.fayvad.com` | 1800 |

---

### 3. digital.fayvad.com (Subdomain - Website + Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `digital` | A | `167.86.95.242` | 1800 | Digital services website |

**Note**: Must be A record (not CNAME) because it has email records.

#### MX Records (Email)
| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `digital` | MX | 10 | `mail.fayvad.com` | 1800 |

#### TXT Records (Email Authentication)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `digital` | TXT | `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all` | 1800 |
| `mail._domainkey.digital` | TXT | `v=DKIM1; k=rsa; p=<DKIM_PUBLIC_KEY>` | 1800 |
| `_dmarc.digital` | TXT | `v=DMARC1; p=none; rua=mailto:admin@digital.fayvad.com; ruf=mailto:admin@digital.fayvad.com; fo=1` | 1800 |

#### CNAME Records (Optional)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `www.digital` | CNAME | `digital.fayvad.com` | 1800 |

---

### 4. mfariji.fayvad.com (Subdomain - Website + Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `mfariji` | A | `167.86.95.242` | 1800 | Mfariji website |

**Note**: Must be A record (not CNAME) because it has email records.

#### MX Records (Email)
| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `mfariji` | MX | 10 | `mail.fayvad.com` | 1800 |

#### TXT Records (Email Authentication)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `mfariji` | TXT | `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all` | 1800 |
| `mail._domainkey.mfariji` | TXT | `v=DKIM1; k=rsa; p=<DKIM_PUBLIC_KEY>` | 1800 |
| `_dmarc.mfariji` | TXT | `v=DMARC1; p=none; rua=mailto:admin@mfariji.fayvad.com; ruf=mailto:admin@mfariji.fayvad.com; fo=1` | 1800 |

#### CNAME Records (Optional)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `www.mfariji` | CNAME | `mfariji.fayvad.com` | 1800 |

---

### 5. driving.fayvad.com (Subdomain - Website + Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `driving` | A | `167.86.95.242` | 1800 | Driving services website |

**Note**: Must be A record (not CNAME) because it has email records.

#### MX Records (Email)
| Host | Type | Priority | Value | TTL |
|------|------|----------|-------|-----|
| `driving` | MX | 10 | `mail.fayvad.com` | 1800 |

#### TXT Records (Email Authentication)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `driving` | TXT | `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all` | 1800 |
| `mail._domainkey.driving` | TXT | `v=DKIM1; k=rsa; p=<DKIM_PUBLIC_KEY>` | 1800 |
| `_dmarc.driving` | TXT | `v=DMARC1; p=none; rua=mailto:admin@driving.fayvad.com; ruf=mailto:admin@driving.fayvad.com; fo=1` | 1800 |

#### CNAME Records (Optional)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `www.driving` | CNAME | `driving.fayvad.com` | 1800 |

---

### 6. rental.fayvad.com (Subdomain - Website Only, NO Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `rental` | A | `167.86.95.242` | 1800 | Rental services website |

**Note**: Can be A record or CNAME (no email records).

#### CNAME Records (Alternative)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `rental` | CNAME | `www.fayvad.com` | 1800 |
| `www.rental` | CNAME | `rental.fayvad.com` | 1800 |

**No email records required** (no MX, SPF, DKIM, DMARC).

---

### 7. college.fayvad.com (Subdomain - Website Only, NO Email)

#### A Records
| Host | Type | Value | TTL | Purpose |
|------|------|-------|-----|---------|
| `college` | A | `167.86.95.242` | 1800 | College services website |

**Note**: Can be A record or CNAME (no email records).

#### CNAME Records (Alternative)
| Host | Type | Value | TTL |
|------|------|-------|-----|
| `college` | CNAME | `www.fayvad.com` | 1800 |
| `www.college` | CNAME | `college.fayvad.com` | 1800 |

**No email records required** (no MX, SPF, DKIM, DMARC).

---

## DNS Record Summary by Type

### A Records (Required)
- `@` (fayvad.com) → `167.86.95.242`
- `www` → `167.86.95.242`
- `mail` → `167.86.95.242`
- `geo` → `167.86.95.242`
- `digital` → `167.86.95.242`
- `mfariji` → `167.86.95.242`
- `driving` → `167.86.95.242`
- `rental` → `167.86.95.242` (or CNAME)
- `college` → `167.86.95.242` (or CNAME)

### MX Records (Email Domains Only)
- `@` (fayvad.com) → `mail.fayvad.com` (priority 10)
- `geo` → `mail.fayvad.com` (priority 10)
- `digital` → `mail.fayvad.com` (priority 10)
- `mfariji` → `mail.fayvad.com` (priority 10)
- `driving` → `mail.fayvad.com` (priority 10)

### SPF Records (Email Domains Only)
All email domains use: `v=spf1 mx a:mail.fayvad.com ip4:167.86.95.242 ~all`

- `@` (fayvad.com) TXT
- `geo` TXT
- `digital` TXT
- `mfariji` TXT
- `driving` TXT

### DKIM Records (Email Domains Only)
- `mail._domainkey` (fayvad.com) TXT
- `mail._domainkey.geo` TXT
- `mail._domainkey.digital` TXT
- `mail._domainkey.mfariji` TXT
- `mail._domainkey.driving` TXT

**Note**: DKIM public keys must be generated and stored in database.

### DMARC Records (Email Domains Only)
- `_dmarc` (fayvad.com) TXT
- `_dmarc.geo` TXT
- `_dmarc.digital` TXT
- `_dmarc.mfariji` TXT
- `_dmarc.driving` TXT

---

## Safety Guidelines for DNS Scripts

### ⚠️ CRITICAL RULES

1. **NEVER call `setHosts` without retrieving existing records first**
   - Always call `getHosts` before `setHosts`
   - If `getHosts` fails, **ABORT** the operation

2. **ALWAYS preserve existing records**
   - Merge new records with existing records
   - Never replace all records with only new ones

3. **ALWAYS use dry-run mode first**
   - Test with `--dry-run` before applying changes
   - Verify what will be added/removed

4. **PROTECTED RECORDS LIST**
   - Before any DNS update, check against this document
   - Ensure all protected records are preserved

5. **EMAIL DOMAINS REQUIRE SPECIAL HANDLING**
   - Email domains need A records (not CNAME)
   - Email domains need MX, SPF, DKIM, DMARC records
   - Non-email domains can use CNAME

---

## Script Safety Checklist

Before running any DNS update script:

- [ ] Script retrieves existing records first (`getHosts`)
- [ ] Script merges new records with existing records
- [ ] Script checks for protected records (this document)
- [ ] Script has dry-run mode
- [ ] Script aborts if existing records can't be retrieved
- [ ] Script warns if no existing records found
- [ ] Script preserves all non-email records (A, CNAME, etc.)
- [ ] Script only adds missing email records (doesn't replace)

---

## Backup and Restore Procedures

### Before Making DNS Changes

1. **Export current DNS records**
   ```bash
   python export_dns_records.py fayvad.com > dns_backup_$(date +%Y%m%d).txt
   ```

2. **Verify protected records exist**
   ```bash
   python verify_protected_records.py
   ```

3. **Run dry-run**
   ```bash
   python update_dns_script.py --dry-run
   ```

### After Making DNS Changes

1. **Verify all protected records still exist**
   ```bash
   python verify_protected_records.py
   ```

2. **Check DNS propagation**
   ```bash
   dig A fayvad.com +short
   dig MX fayvad.com +short
   ```

### If DNS Records Are Deleted

1. **Stop all DNS update scripts immediately**
2. **Restore from backup**
   ```bash
   python restore_dns_records.py --from-backup dns_backup_YYYYMMDD.txt
   ```
3. **Or restore using restore script**
   ```bash
   python restore_all_dns.py --apply
   ```

---

## DKIM Key Management

### Domains Requiring DKIM Keys

1. **fayvad.com** - Generate if missing
2. **geo.fayvad.com** - Generate if missing
3. **digital.fayvad.com** - Generate if missing
4. **mfariji.fayvad.com** - Generate if missing
5. **driving.fayvad.com** - Generate if missing

### Generate DKIM Keys

```bash
# For a specific domain
python generate_dkim_keys.py fayvad.com

# For all email domains
python generate_dkim_keys.py all
```

### Verify DKIM Keys

```bash
# Check if DKIM keys exist in database
python verify_dkim_keys.py

# Check DNS records
dig TXT mail._domainkey.fayvad.com +short
```

---

## Reverse DNS (PTR) Configuration

**Important**: Reverse DNS must be configured with hosting provider (not Namecheap).

- **IP**: `167.86.95.242`
- **Should resolve to**: `mail.fayvad.com`

**Contact hosting provider** to set PTR record.

---

## Testing DNS Configuration

### Test A Records
```bash
dig A fayvad.com +short
dig A www.fayvad.com +short
dig A geo.fayvad.com +short
dig A digital.fayvad.com +short
dig A mfariji.fayvad.com +short
dig A driving.fayvad.com +short
dig A rental.fayvad.com +short
dig A college.fayvad.com +short
```

### Test MX Records (Email Domains)
```bash
dig MX fayvad.com +short
dig MX geo.fayvad.com +short
dig MX digital.fayvad.com +short
dig MX mfariji.fayvad.com +short
dig MX driving.fayvad.com +short
```

### Test SPF Records
```bash
dig TXT fayvad.com +short | grep spf
dig TXT geo.fayvad.com +short | grep spf
dig TXT digital.fayvad.com +short | grep spf
dig TXT mfariji.fayvad.com +short | grep spf
dig TXT driving.fayvad.com +short | grep spf
```

### Test DKIM Records
```bash
dig TXT mail._domainkey.fayvad.com +short
dig TXT mail._domainkey.geo.fayvad.com +short
dig TXT mail._domainkey.digital.fayvad.com +short
dig TXT mail._domainkey.mfariji.fayvad.com +short
dig TXT mail._domainkey.driving.fayvad.com +short
```

### Test DMARC Records
```bash
dig TXT _dmarc.fayvad.com +short
dig TXT _dmarc.geo.fayvad.com +short
dig TXT _dmarc.digital.fayvad.com +short
dig TXT _dmarc.mfariji.fayvad.com +short
dig TXT _dmarc.driving.fayvad.com +short
```

---

## Quick Reference: Protected Records

### Never Delete These Hosts
- `@` (root domain)
- `www`
- `mail`
- `geo`
- `digital`
- `mfariji`
- `driving`
- `rental`
- `college`
- `mail._domainkey` (and variants)
- `_dmarc` (and variants)

### Email Domains (Require Full Email Records)
- `fayvad.com`
- `geo.fayvad.com`
- `digital.fayvad.com`
- `mfariji.fayvad.com`
- `driving.fayvad.com`

### Website-Only Domains (No Email Records)
- `rental.fayvad.com`
- `college.fayvad.com`

---

## Contact and Maintenance

**Last Updated**: 2025-01-XX

**Maintained By**: System Administrator

**For Questions**: Contact system administrator before making DNS changes

**Emergency DNS Restoration**: See `DNS_RESTORATION_URGENT.md`

---

## Appendix: Namecheap API Notes

### Important API Behavior

- **`setHosts` REPLACES ALL DNS records** - Never call without retrieving existing records first
- **`getHosts` must succeed** - If it fails, abort the operation
- **Always merge records** - Never send only new records

### API Safety Pattern

```python
# 1. Get existing records
existing_records, error = get_existing_dns_records(namecheap, domain_name)
if error or existing_records is None:
    abort("Cannot retrieve existing records - aborting to prevent data loss")

# 2. Merge with new records
all_records = list(existing_records)
# Add new records to all_records (avoid duplicates)

# 3. Send all records
setHosts(all_records)  # Includes existing + new
```

---

**END OF DOCUMENT**


