# Testing Guide - Normalization & Consistency

## Quick Start

### 1. **Pre-Test: Check Migration Readiness**
```bash
python manage.py shell < check_migration_readiness.py
```
**Expected:** ✅ All checks passed! Models are ready for migration.

### 2. **Create Migrations** (First Time Only)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. **Run Consistency Checks**
```bash
bash test_consistency.sh
```
**Checks:**
- Django configuration
- Python syntax
- Critical imports
- Query patterns
- Model properties

### 4. **Run Full Normalization Tests**
```bash
python manage.py shell < test_normalization.py
```
**Or:**
```bash
python test_normalization.py
```

**Tests:**
- ✅ EmailAccount.organization derived from domain
- ✅ EmailMessage.account derived from folder
- ✅ Contact.organization derived from user
- ✅ Document.organization derived from uploaded_by
- ✅ EmailTemplate.organization derived from user
- ✅ Queries with domain__organization
- ✅ Null organization handling
- ✅ DomainManager.create_email_account signature

---

## Test Files Created

1. **`test_normalization.py`** - Comprehensive model tests
2. **`test_consistency.sh`** - Quick consistency checks
3. **`check_migration_readiness.py`** - Pre-migration validation
4. **`TEST_PLAN.md`** - Detailed manual testing checklist

---

## What Gets Tested

### **Model Properties**
- `EmailAccount.organization` → derived from `domain.organization`
- `EmailMessage.account` → derived from `folder.account`
- `Contact.organization` → derived from `user.organization`
- `Document.organization` → derived from `uploaded_by.organization`
- `EmailTemplate.organization` → derived from `user.organization`
- `EmailSignature.organization` → derived from `user.organization`

### **Queries**
- `EmailAccount.objects.filter(domain__organization=org)`
- `EmailAccount.objects.select_related('domain', 'domain__organization')`
- `Contact.objects.filter(user=user)`
- `Document.objects.filter(uploaded_by=user)`

### **Edge Cases**
- User without organization → properties return `None`
- Null handling in `__str__` methods
- Query performance with select_related

---

## Expected Test Results

### ✅ **All Tests Should Pass**

```
============================================================
COMPREHENSIVE NORMALIZATION TESTS
============================================================

TEST: EmailAccount.organization derived from domain
✅ EmailAccount.organization property works correctly

TEST: EmailMessage.account derived from folder
✅ EmailMessage.account property works correctly

TEST: Contact.organization derived from user
✅ Contact.organization property works correctly

TEST: Document.organization derived from uploaded_by
✅ Document.organization property works correctly

TEST: EmailTemplate.organization derived from user
✅ EmailTemplate.organization property works correctly

TEST: Queries with domain__organization
✅ Query filter(domain__organization=org) works: 2 accounts
✅ select_related('domain', 'domain__organization') works

TEST: Null organization handling
✅ Contact handles null organization correctly
✅ EmailTemplate handles null organization correctly

TEST: DomainManager.create_email_account signature
✅ DomainManager.create_email_account signature correct

============================================================
TEST SUMMARY
============================================================
Passed: 8/8
✅ ALL TESTS PASSED!
```

---

## Troubleshooting

### **Import Errors**
```bash
# Activate virtual environment first
source venv/bin/activate  # or your venv path
python manage.py shell < test_normalization.py
```

### **Migration Issues**
```bash
# Check pending migrations
python manage.py showmigrations

# Create migrations
python manage.py makemigrations mail

# Apply migrations
python manage.py migrate
```

### **Database Issues**
```bash
# Reset database (WARNING: Deletes all data)
python manage.py flush

# Or recreate migrations
rm mail/migrations/0*.py
python manage.py makemigrations
python manage.py migrate
```

### **Property Not Found**
- Check model file has `@property` decorator
- Verify property name matches exactly
- Check for typos in property definition

### **Query Errors**
- Verify using `domain__organization` not `organization`
- Check select_related includes all needed relationships
- Verify foreign keys exist in database

---

## Manual Testing Checklist

See `TEST_PLAN.md` for detailed manual testing steps including:
- Model relationships
- Views (admin portal, business)
- API endpoints
- Management commands
- Edge cases

---

## Next Steps After Tests Pass

1. ✅ Run migrations: `python manage.py migrate`
2. ✅ Test in development environment
3. ✅ Test admin portal views
4. ✅ Test API endpoints
5. ✅ Test business views
6. ✅ Deploy to staging
7. ✅ Test in production

---

## Support

If tests fail:
1. Check error messages carefully
2. Verify migrations are applied
3. Check database schema matches models
4. Review `CODEBASE_CONSISTENCY_FIXES.md` for changes made
5. Check `MODEL_NORMALIZATION_SUMMARY.md` for model changes

