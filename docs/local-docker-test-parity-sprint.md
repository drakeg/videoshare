# Local Docker Test Parity Sprint

## Goal

Align the local Docker full-suite runner with the same four-process Django test execution used in CI, while keeping the process count configurable for constrained developer machines.

## Scope

- Add `DJANGO_TEST_PROCESSES` with a default of 4 to the Docker test service.
- Run `docker/test.sh` with Django's `--parallel` option.
- Use the same environment variable in GitHub Actions so local/CI test-process configuration stays aligned.
- Document the default and the one-off override for lower-resource systems.
- Add regression tests that keep Compose, the Docker test script, CI, and `.env.example` synchronized.
- Run the full local Docker suite after the change and record the result.

## Rationale

The 900+ test suite was observed running serially in Docker even though CI already uses four processes. This unnecessarily lengthens the local Build → Test → Fix loop and conflicts with the project's rapid-development standard.

## Acceptance criteria

1. `docker compose run --rm test` defaults to four Django test processes.
2. `DJANGO_TEST_PROCESSES=1 docker compose run --rm test` can force serial execution.
3. GitHub Actions uses the same configuration variable.
4. The configuration is documented in `.env.example` and README.
5. Regression tests fail if Docker/CI execution drifts back to mismatched process settings.
6. The full local Docker suite passes with the new default.
7. No application behavior, schema, dependency, payment, or infrastructure resource changes are introduced.

## Verification

    docker compose config --quiet
    docker compose run --rm --entrypoint python test manage.py test video.test_local_docker_runtime
    docker compose run --rm test

## Out of scope

- Changing application query/runtime concurrency
- Changing database technology
- Adding test sharding services
- Paid CI acceleration

## Delivered

- Added `DJANGO_TEST_PROCESSES` with a default of 4 to the Docker test service.
- Updated `docker/test.sh` to run Django tests with configurable `--parallel`.
- Updated GitHub Actions to use the same `DJANGO_TEST_PROCESSES` variable.
- Documented the default and a one-off `DJANGO_TEST_PROCESSES=1` override.
- Added runtime regression coverage that keeps Compose, the test script, CI, `.env.example`, and README aligned.

## Verification results

- `git diff --check` passed locally.
- `sh -n docker/test.sh` passed locally.
- `docker compose config --quiet` passed locally.
- Compose interpolation verified `DJANGO_TEST_PROCESSES=4` by default and `=1` with an override.
- A shell-level execution check verified `docker/test.sh` emits `python manage.py test --parallel 4` by default and `--parallel 1` when overridden.
- GitHub Actions Django checks run #652 passed configuration and migration-drift checks and all 953 tests with one expected skip using the shared process-count variable.
- Repository standards workflow run #14 passed.
- Actual one-off Docker test containers repeatedly stalled in the host Docker daemon before test output. Two stranded ephemeral `videoshare-test-run-*` containers (one Dead, one Created) were identified and removed without touching named volumes or application data; the daemon still stalled afterward. No full local Docker-suite pass is claimed for this sprint.

The repository runner behavior is validated, but a Docker Desktop/daemon restart may be needed on the development host before local container execution is reliable again. Restarting Docker was not performed because it could interrupt unrelated running containers.
