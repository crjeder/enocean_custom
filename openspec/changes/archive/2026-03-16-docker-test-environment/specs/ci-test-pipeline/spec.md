## ADDED Requirements

### Requirement: GitHub Actions workflow for integration tests
The system SHALL provide `.github/workflows/integration-tests.yml` that builds the Docker test environment and runs the full integration test suite on every push and pull request to `main`.

#### Scenario: Workflow triggers on push to main
- **WHEN** a commit is pushed to the `main` branch
- **THEN** the `integration-tests` GitHub Actions job is triggered automatically

#### Scenario: Workflow triggers on pull request
- **WHEN** a pull request targeting `main` is opened or updated
- **THEN** the `integration-tests` GitHub Actions job is triggered automatically

### Requirement: CI job passes on green test suite
The CI job SHALL exit with code 0 (success) if and only if all integration tests pass.

#### Scenario: All tests pass → CI green
- **WHEN** the test suite runs and all test cases pass
- **THEN** the GitHub Actions job reports a success status

#### Scenario: Any test fails → CI red
- **WHEN** at least one test case fails
- **THEN** the GitHub Actions job reports a failure status and the PR cannot be merged if branch protection is enabled

### Requirement: Docker layer caching in CI
The CI job SHALL cache Docker image layers between runs to reduce build time.

#### Scenario: Cached layers are reused
- **WHEN** the workflow runs a second time with no changes to `Dockerfile` or `docker-compose.test.yml`
- **THEN** Docker build completes faster than the first run due to layer cache hits

### Requirement: Test results are published as CI artifacts
The CI job SHALL upload the pytest XML report as a GitHub Actions artifact so test results are inspectable without reading raw logs.

#### Scenario: XML report is available after run
- **WHEN** the CI job completes (pass or fail)
- **THEN** a `test-results.xml` artifact is available for download in the GitHub Actions run summary

### Requirement: Local one-command test execution
The system SHALL provide a `Makefile` (or shell script) target `make test-integration` that builds and runs the full Docker test environment locally.

#### Scenario: Developer runs tests locally
- **WHEN** a developer with Docker installed runs `make test-integration` from the repository root
- **THEN** the Docker environment is built, tests execute, and a pass/fail result is printed to stdout
