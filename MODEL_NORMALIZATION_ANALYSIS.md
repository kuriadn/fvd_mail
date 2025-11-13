# Database Model Normalization Analysis (3NF)

## Issues Found

### 1. **EmailAccount** - Transitive Dependency Violation

**Problem:**
```python
class EmailAccount(models.Model):
    user = ForeignKey(User)
    organization = ForeignKey(Organization)  # ❌ REDUNDANT
    domain = ForeignKey(Domain)              # Domain already has organization FK
```

**Issue:** `organization` can be derived from `domain.organization` - violates 3NF

**Fix:** Remove `organization` FK, derive via `domain.organization`

---

### 2. **EmailMessage** - Transitive Dependency Violation

**Problem:**
```python
class EmailMessage(models.Model):
    folder = ForeignKey(EmailFolder)  # Folder has account FK
    account = ForeignKey(EmailAccount, null=True)  # ❌ REDUNDANT
```

**Issue:** `account` can be derived from `folder.account` - violates 3NF

**Fix:** Remove `account` FK, derive via `folder.account`

---

### 3. **EmailTemplate** - Transitive Dependency Violation

**Problem:**
```python
class EmailTemplate(models.Model):
    organization = ForeignKey(Organization)  # ❌ REDUNDANT
    user = ForeignKey(User)                 # User has organization FK
```

**Issue:** `organization` can be derived from `user.organization` - violates 3NF

**Fix:** Remove `organization` FK, derive via `user.organization`

---

### 4. **EmailSignature** - Transitive Dependency Violation

**Problem:**
```python
class EmailSignature(models.Model):
    user = ForeignKey(User)                 # User has organization FK
    organization = ForeignKey(Organization)  # ❌ REDUNDANT
```

**Issue:** `organization` can be derived from `user.organization` - violates 3NF

**Fix:** Remove `organization` FK, derive via `user.organization`

---

### 5. **Contact** - Transitive Dependency Violation

**Problem:**
```python
class Contact(models.Model):
    organization = ForeignKey(Organization)  # ❌ REDUNDANT
    user = ForeignKey(User)                   # User has organization FK
```

**Issue:** `organization` can be derived from `user.organization` - violates 3NF

**Fix:** Remove `organization` FK, derive via `user.organization`

---

### 6. **Document** - Transitive Dependency Violation

**Problem:**
```python
class Document(models.Model):
    organization = ForeignKey(Organization)  # ❌ REDUNDANT
    uploaded_by = ForeignKey(User)            # User has organization FK
```

**Issue:** `organization` can be derived from `uploaded_by.organization` - violates 3NF

**Fix:** Remove `organization` FK, derive via `uploaded_by.organization`

---

## Summary

**Violations Found:** 6 models with transitive dependencies

**Root Cause:** Storing redundant foreign keys that can be derived through relationships

**Impact:** 
- Data redundancy
- Update anomalies (if organization changes, need to update multiple places)
- Storage waste

**Recommendation:** Remove redundant FKs and use properties/methods to access derived relationships

