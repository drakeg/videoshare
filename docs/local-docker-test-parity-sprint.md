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
