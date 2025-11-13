# Comprehensive Test Plan

## Test Execution

### 1. **Quick Consistency Check**
```bash
bash test_consistency.sh
```
Checks:
- Django configuration
- Python syntax
- Critical imports
- Query patterns
- Model properties

### 2. **Full Normalization Tests** (Requires Django shell)
```bash
python manage.py shell < test_normalization.py
```
Or:
```bash
python test_normalization.py
```

Tests:
- ✅ EmailAccount.organization derived from domain
- ✅ EmailMessage.account derived from folder
- ✅ Contact.organization derived from user
- ✅ Document.organization derived from uploaded_by
- ✅ EmailTemplate.organization derived from user
- ✅ Queries with domain__organization
- ✅ Null organization handling
- ✅ DomainManager.create_email_account signature

### 3. **Manual Testing Checklist**

#### **A. Model Relationships**
- [ ] Create Organization → Domain → EmailAccount
- [ ] Verify `account.organization` returns correct org
- [ ] Create EmailFolder → EmailMessage
- [ ] Verify `message.account` returns correct account
- [ ] Create Contact with user (with/without org)
- [ ] Verify `contact.organization` works correctly

#### **B. Queries**
- [ ] `EmailAccount.objects.filter(domain__organization=org)` works
- [ ] `EmailAccount.objects.select_related('domain', 'domain__organization')` works
- [ ] `Contact.objects.filter(user=user)` works
- [ ] `Document.objects.filter(uploaded_by=user)` works

#### **C. Views**
- [ ] Admin portal: Organizations list
- [ ] Admin portal: Organization detail (shows email accounts)
- [ ] Admin portal: Domains list
- [ ] Admin portal: Users list
- [ ] Business: Dashboard loads
- [ ] Business: Contacts list
- [ ] Business: Documents list

#### **D. API Endpoints**
- [ ] `/fayvad_api/admin/email-accounts/` returns accounts with organization
- [ ] `/fayvad_api/org-admin/email-accounts/` filters by organization
- [ ] `/fayvad_api/org-admin/dashboard/` shows correct counts

#### **E. Management Commands**
- [ ] `python manage.py create_domain --name test.com --organization-id 1`
- [ ] `python manage.py create_email_account user@test.com --user-id 1`
- [ ] Verify account created without organization parameter

### 4. **Database Migration**

Before testing, create and run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. **Edge Cases**

- [ ] User without organization → Contact.organization returns None
- [ ] User without organization → EmailTemplate.organization returns None
- [ ] Domain without organization (shouldn't happen, but test)
- [ ] EmailAccount without domain (shouldn't happen, but test)

### 6. **Performance**

- [ ] Queries use select_related where appropriate
- [ ] No N+1 queries in admin portal views
- [ ] Organization property access is efficient

## Expected Results

✅ All model properties work correctly
✅ All queries use new relationship paths
✅ No broken imports or references
✅ Views load without errors
✅ API endpoints return correct data
✅ Management commands work without organization parameter

## Troubleshooting

If tests fail:
1. Check migrations: `python manage.py showmigrations`
2. Check for syntax errors: `python -m py_compile mail/models.py`
3. Check imports: `python manage.py shell` then `from mail.models import *`
4. Check database: Verify foreign keys exist

