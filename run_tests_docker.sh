#!/bin/bash
# Docker-based test runner for normalization tests
# Usage: ./run_tests_docker.sh [test_type]
# test_type: all, normalization, consistency, migration, django-tests

set -e

TEST_TYPE=${1:-all}

echo "=========================================="
echo "Docker Test Runner - Normalization Tests"
echo "=========================================="
echo "Docker version: $(docker --version)"
echo "Docker Compose version: $(docker compose version)"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run a test service
run_test_service() {
    local service=$1
    local description=$2
    
    echo -e "${YELLOW}Running: ${description}${NC}"
    echo "----------------------------------------"
    
    if docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from $service $service; then
        echo -e "${GREEN}✅ ${description} PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ ${description} FAILED${NC}"
        return 1
    fi
}

# Function to cleanup
cleanup() {
    echo ""
    echo "Cleaning up..."
    docker compose -f docker-compose.test.yml down -v 2>/dev/null || true
}

# Trap cleanup on exit
trap cleanup EXIT

# Build test image first
echo "Building test image..."
docker compose -f docker-compose.test.yml build test

case $TEST_TYPE in
    all)
        echo "Running ALL tests..."
        echo ""
        
        # 1. Check migration readiness
        run_test_service "check_migration" "Migration Readiness Check"
        MIGRATION_CHECK=$?
        
        if [ $MIGRATION_CHECK -ne 0 ]; then
            echo -e "${RED}Migration check failed. Fix issues before running other tests.${NC}"
            exit 1
        fi
        
        # 2. Run migrations (using host database)
        echo ""
        echo -e "${YELLOW}Running migrations on host database...${NC}"
        docker compose -f docker-compose.test.yml run --rm test python manage.py makemigrations --check --dry-run || true
        docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
        
        # 3. Consistency check
        run_test_service "test_consistency" "Consistency Check"
        CONSISTENCY_CHECK=$?
        
        # 4. Normalization tests
        run_test_service "test_normalization" "Normalization Tests"
        NORMALIZATION_CHECK=$?
        
        # 5. Workflow tests
        run_test_service "test_workflow" "Organization Workflow Tests"
        WORKFLOW_CHECK=$?
        
        # 6. Django tests (if any)
        run_test_service "test" "Django Unit Tests"
        DJANGO_CHECK=$?
        
        # Summary
        echo ""
        echo "=========================================="
        echo "TEST SUMMARY"
        echo "=========================================="
        
        if [ $MIGRATION_CHECK -eq 0 ] && [ $CONSISTENCY_CHECK -eq 0 ] && [ $NORMALIZATION_CHECK -eq 0 ] && [ $WORKFLOW_CHECK -eq 0 ] && [ $DJANGO_CHECK -eq 0 ]; then
            echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
            exit 0
        else
            echo -e "${RED}❌ SOME TESTS FAILED${NC}"
            [ $MIGRATION_CHECK -ne 0 ] && echo "  - Migration check failed"
            [ $CONSISTENCY_CHECK -ne 0 ] && echo "  - Consistency check failed"
            [ $NORMALIZATION_CHECK -ne 0 ] && echo "  - Normalization tests failed"
            [ $WORKFLOW_CHECK -ne 0 ] && echo "  - Workflow tests failed"
            [ $DJANGO_CHECK -ne 0 ] && echo "  - Django tests failed"
            exit 1
        fi
        ;;
    
    migration)
        run_test_service "check_migration" "Migration Readiness Check"
        exit $?
        ;;
    
    consistency)
        run_test_service "test_consistency" "Consistency Check"
        exit $?
        ;;
    
    normalization)
        # Run migrations first (using host database)
        echo "Running migrations on host database..."
        docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
        
        run_test_service "test_normalization" "Normalization Tests"
        exit $?
        ;;
    
    workflow)
        # Run migrations first (using host database)
        echo "Running migrations on host database..."
        docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
        
        run_test_service "test_workflow" "Organization Workflow Tests"
        exit $?
        ;;
    
    django-tests)
        # Run migrations first (using host database)
        echo "Running migrations on host database..."
        docker compose -f docker-compose.test.yml run --rm test python manage.py migrate
        
        run_test_service "test" "Django Unit Tests"
        exit $?
        ;;
    
    *)
        echo "Usage: $0 [all|migration|consistency|normalization|workflow|django-tests]"
        exit 1
        ;;
esac

