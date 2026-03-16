# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2023-03-16

### Added

- Docker-based integration test environment (`docker-compose.test.yml`) that runs a clean Home Assistant instance with `enocean_custom` mounted and a virtual serial EnOcean dongle via `socat`
- Integration test suite (`tests/integration/`) covering cover position state, binary sensor state, service-call serial output, and UTE teach-in auto-response
- GitHub Actions workflow (`.github/workflows/integration-tests.yml`) that runs the full integration test suite on every push and pull request to `main`, with Docker layer caching and JUnit XML artifact upload
- `scripts/test-integration.sh` — one-command local test runner for the Docker suite
- `scripts/test-unit.sh` — convenience script for the existing enocean library unit tests
- `docs/testing.md` — developer guide for running both test suites

