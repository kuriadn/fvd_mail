# Sync Emails Command - Fixed

## ✅ Changes Made

### 1. Fixed Import Issue
- Resolved circular import between `mail/services.py` and `mail/services/__init__.py`
- Command now imports `DjangoEmailService` directly from `mail/services.py`

### 2. Enhanced Folder Organization
- Syncs standard folders: INBOX, Sent, Drafts, Spam, Trash, Junk
- Automatically categorizes folders by type:
  - `INBOX` → `inbox`
  - `Sent` → `sent`
  - `Drafts` → `drafts`
  - `Spam`/`Junk` → `spam`
  - `Trash`/`Deleted` → `trash`
  - Others → `custom`

### 3. Improved Sync Logic
- Syncs ALL messages (not just unread)
- Checks for existing messages to avoid duplicates
- Handles missing folders gracefully
- Case-insensitive folder matching

### 4. Better Error Handling
- Skips folders that don't exist (no errors)
- Provides clear status messages
- Shows count per folder

## Usage

### Sync all folders for an account:
```bash
python manage.py sync_emails --email d.kuria@fayvad.com --password MeMiMo@0207
```

### Sync specific folder:
```bash
python manage.py sync_emails --email d.kuria@fayvad.com --password MeMiMo@0207 --folder INBOX
```

### Sync all accounts:
```bash
python manage.py sync_emails --password MeMiMo@0207
```

## Note: Docker Connection

When running in Docker, IMAP connection may fail because it tries to connect to `localhost`. 

**Solution**: Run on host or configure `EMAIL_IMAP_HOST` to use `host.docker.internal` for Docker.

## Folder Structure Created

After sync, Django will have:
- `EmailFolder` records for each folder
- `EmailMessage` records organized by folder
- Proper folder types and counts

## Example Output

```
Syncing emails for d.kuria@fayvad.com...
  ✓ INBOX: 16 emails synced
  ✓ Sent: 5 emails synced
  - Drafts: No new emails
  - Spam: No new emails
  - Trash: No new emails
  - Junk: No new emails

✓ Total: 21 emails synced
```

