# Makefile for Docker-based testing
.PHONY: help test test-all test-migration test-consistency test-normalization test-django clean build

help:
	@echo "Docker Testing Commands:"
	@echo "  make test              - Run all tests"
	@echo "  make test-migration    - Check migration readiness"
	@echo "  make test-consistency  - Run consistency checks"
	@echo "  make test-normalization - Run normalization tests"
	@echo "  make test-django       - Run Django unit tests"
	@echo "  make build             - Build test image"
	@echo "  make clean             - Clean up test containers and volumes"

build:
	docker compose -f docker-compose.test.yml build test

test: test-all

test-all:
	@./run_tests_docker.sh all

test-migration:
	@./run_tests_docker.sh migration

test-consistency:
	@./run_tests_docker.sh consistency

test-normalization:
	@./run_tests_docker.sh normalization

test-workflow:
	@./run_tests_docker.sh workflow

test-django:
	@./run_tests_docker.sh django-tests

clean:
	docker compose -f docker-compose.test.yml down -v
	docker compose -f docker-compose.test.yml down --rmi all 2>/dev/null || true

shell:
	docker compose -f docker-compose.test.yml run --rm test bash

migrate:
	docker compose -f docker-compose.test.yml up -d db
	sleep 5
	docker compose -f docker-compose.test.yml run --rm test python manage.py migrate

