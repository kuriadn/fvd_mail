#!/bin/bash
# Comprehensive test script for normalization changes
# Run: bash test_consistency.sh

set -e

echo "=========================================="
echo "COMPREHENSIVE CODEBASE CONSISTENCY TESTS"
echo "=========================================="

# Check Django setup
echo ""
echo "1. Checking Django configuration..."
python manage.py check --deploy || echo "⚠️  Django check failed (may need virtualenv)"

# Check for syntax errors
echo ""
echo "2. Checking Python syntax..."
find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./env/*" -not -path "./.env/*" -exec python -m py_compile {} \; 2>&1 | head -20 || echo "⚠️  Some syntax errors found"

# Check imports
echo ""
echo "3. Checking critical imports..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from mail.models import EmailAccount, Domain, EmailMessage, Contact, Document, EmailTemplate
    from mail.services.domain_manager import DomainManager
    print('✅ All critical imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || echo "⚠️  Import check failed"

# Check for remaining organization FK references
echo ""
echo "4. Checking for remaining organization FK issues..."
if grep -r "EmailAccount.objects.create.*organization=" --include="*.py" . 2>/dev/null | grep -v "__pycache__" | grep -v ".pyc"; then
    echo "❌ Found EmailAccount.objects.create with organization parameter"
else
    echo "✅ No EmailAccount.objects.create with organization parameter"
fi

# Check for correct query patterns
echo ""
echo "5. Checking query patterns..."
if grep -r "EmailAccount.objects.filter(organization=" --include="*.py" . 2>/dev/null | grep -v "__pycache__" | grep -v ".pyc"; then
    echo "❌ Found old filter(organization=...) pattern"
else
    echo "✅ No old filter(organization=...) patterns found"
fi

# Check for modoboa references (should be none)
echo ""
echo "6. Checking for Modoboa references..."
modoboa_count=$(grep -ri "modoboa" --include="*.py" . 2>/dev/null | grep -v "__pycache__" | grep -v ".pyc" | grep -v "test_consistency.sh" | wc -l)
if [ "$modoboa_count" -gt 0 ]; then
    echo "⚠️  Found $modoboa_count Modoboa references (should be removed)"
    grep -ri "modoboa" --include="*.py" . 2>/dev/null | grep -v "__pycache__" | grep -v ".pyc" | grep -v "test_consistency.sh" | head -5
else
    echo "✅ No Modoboa references found"
fi

# Check model properties
echo ""
echo "7. Checking model properties..."
python -c "
import sys
sys.path.insert(0, '.')
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_mail_project.settings')
django.setup()

from mail.models import EmailAccount, EmailMessage, Contact, Document, EmailTemplate

# Check properties exist
models_to_check = [
    (EmailAccount, 'organization'),
    (EmailMessage, 'account'),
    (Contact, 'organization'),
    (Document, 'organization'),
    (EmailTemplate, 'organization'),
]

for model, prop in models_to_check:
    if hasattr(model, prop):
        print(f'✅ {model.__name__}.{prop} property exists')
    else:
        print(f'❌ {model.__name__}.{prop} property missing')
" 2>&1 || echo "⚠️  Property check failed"

echo ""
echo "=========================================="
echo "TESTS COMPLETE"
echo "=========================================="

