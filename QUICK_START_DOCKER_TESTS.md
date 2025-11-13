# Quick Start - Docker Testing

## Prerequisites ✅
- Docker 2+ installed
- Docker Compose v2.37.3+ (verified)

## One Command to Run All Tests

```bash
./run_tests_docker.sh all
```

## Or Use Make

```bash
make test              # Run all tests
make test-migration    # Check migration readiness
make test-consistency  # Consistency checks
make test-normalization # Normalization tests
make test-django       # Django unit tests
make clean             # Clean up
```

## What Gets Tested

1. **Migration Readiness** - Verifies models are ready for migration
2. **Consistency Checks** - Python syntax, imports, query patterns
3. **Normalization Tests** - All 8 model property tests
4. **Django Tests** - Unit tests (if any)

## Expected Output

```
==========================================
Docker Test Runner - Normalization Tests
==========================================
✅ Migration Readiness Check PASSED
✅ Consistency Check PASSED
✅ Normalization Tests PASSED
✅ Django Unit Tests PASSED

✅ ALL TESTS PASSED!
```

## Troubleshooting

### First Time Setup
```bash
# Build test image
docker compose -f docker-compose.test.yml build test

# Start database
docker compose -f docker-compose.test.yml up -d db

# Wait for DB, then run migrations
sleep 5
docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
```

### Clean Everything
```bash
make clean
# or
docker compose -f docker-compose.test.yml down -v --rmi all
```

### View Logs
```bash
docker compose -f docker-compose.test.yml logs test_normalization
docker compose -f docker-compose.test.yml logs db
```

## Files Created

- `docker-compose.test.yml` - Test services configuration
- `Dockerfile.test` - Test container image
- `run_tests_docker.sh` - Test runner script
- `Makefile` - Convenience commands
- `.dockerignore` - Build optimization

## Next Steps

After tests pass:
1. Review test output
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`
4. Test in development
5. Deploy

