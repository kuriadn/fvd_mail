# Docker Testing Guide

## Prerequisites

- Docker 2+ (Docker Compose v2)
- Docker Compose v2.37.3+ (verified)

## Quick Start

### Run All Tests
```bash
chmod +x run_tests_docker.sh
./run_tests_docker.sh all
```

### Run Specific Tests
```bash
# Migration readiness check
./run_tests_docker.sh migration

# Consistency checks
./run_tests_docker.sh consistency

# Normalization tests
./run_tests_docker.sh normalization

# Django unit tests
./run_tests_docker.sh django-tests
```

## Test Services

The `docker-compose.test.yml` defines these services:

1. **`db`** - PostgreSQL test database
2. **`test`** - Django unit tests
3. **`test_normalization`** - Normalization model tests
4. **`test_consistency`** - Quick consistency checks
5. **`check_migration`** - Migration readiness validation

## Manual Docker Commands

### Build Test Image
```bash
docker compose -f docker-compose.test.yml build test
```

### Run Single Test Service
```bash
# Normalization tests
docker compose -f docker-compose.test.yml up --build test_normalization

# Consistency check
docker compose -f docker-compose.test.yml up --build test_consistency

# Migration check
docker compose -f docker-compose.test.yml up --build check_migration
```

### Run Tests with Shell Access
```bash
# Start database
docker compose -f docker-compose.test.yml up -d db

# Run migrations
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate

# Run specific test script
docker compose -f docker-compose.test.yml run --rm test python test_normalization.py

# Interactive shell
docker compose -f docker-compose.test.yml run --rm test bash
```

### Cleanup
```bash
# Stop and remove containers
docker compose -f docker-compose.test.yml down

# Remove volumes (clears test database)
docker compose -f docker-compose.test.yml down -v

# Remove images
docker compose -f docker-compose.test.yml down --rmi all
```

## Test Workflow

### 1. **First Time Setup**
```bash
# Build test image
docker compose -f docker-compose.test.yml build test

# Start database
docker compose -f docker-compose.test.yml up -d db

# Wait for database to be ready
sleep 5

# Run migrations
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
```

### 2. **Run Tests**
```bash
# All tests
./run_tests_docker.sh all

# Or individual tests
./run_tests_docker.sh normalization
```

### 3. **View Results**
Test output is shown in real-time. Exit codes:
- `0` = All tests passed
- `1` = Some tests failed

## Environment Variables

Test environment uses:
- `DEBUG=1`
- `FAYVAD_MAIL_DB_HOST=db` (Docker service name)
- `FAYVAD_MAIL_DB_NAME=fayvad_mail_test_db`
- `FAYVAD_MAIL_DB_USER=fayvad`
- `FAYVAD_MAIL_DB_PASSWORD=test_password`

## Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker compose -f docker-compose.test.yml ps db

# Check database logs
docker compose -f docker-compose.test.yml logs db

# Test connection
docker compose -f docker-compose.test.yml run --rm test python -c "
from django.db import connection
connection.ensure_connection()
print('Database connected!')
"
```

### Test Container Issues
```bash
# Rebuild test image
docker compose -f docker-compose.test.yml build --no-cache test

# Check test container logs
docker compose -f docker-compose.test.yml logs test_normalization

# Run with verbose output
docker compose -f docker-compose.test.yml run --rm test python test_normalization.py -v
```

### Clean Slate
```bash
# Remove everything and start fresh
docker compose -f docker-compose.test.yml down -v --rmi all
docker compose -f docker-compose.test.yml build test
docker compose -f docker-compose.test.yml up -d db
sleep 5
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          chmod +x run_tests_docker.sh
          ./run_tests_docker.sh all
```

### GitLab CI Example
```yaml
test:
  script:
    - chmod +x run_tests_docker.sh
    - ./run_tests_docker.sh all
```

## Performance Tips

1. **Use `--keepdb`** for Django tests to reuse database
2. **Build once** and reuse images
3. **Run tests in parallel** (separate services)
4. **Cache volumes** for test database

## Expected Output

```
==========================================
Docker Test Runner - Normalization Tests
==========================================
Docker version: Docker version 28.3.0
Docker Compose version: v2.37.3

Building test image...
Running: Migration Readiness Check
----------------------------------------
✅ Migration Readiness Check PASSED

Running: Consistency Check
----------------------------------------
✅ Consistency Check PASSED

Running: Normalization Tests
----------------------------------------
✅ Normalization Tests PASSED

Running: Django Unit Tests
----------------------------------------
✅ Django Unit Tests PASSED

==========================================
TEST SUMMARY
==========================================
✅ ALL TESTS PASSED!
```

## Next Steps

After tests pass:
1. Review test output
2. Fix any issues
3. Run migrations on development
4. Deploy to staging
5. Run tests in staging environment

