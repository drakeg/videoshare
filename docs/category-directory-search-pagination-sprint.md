# Category Directory Search and Pagination Sprint

## Goal

Make the public Categories directory easier to browse as it grows without changing category creation or category/video visibility behavior.

## Scope

- Add bounded search across category name and description.
- Add validated A–Z and Z–A sorting.
- Paginate the directory at 24 categories per page.
- Preserve search and sort state across pagination.
- Reset pagination when search or sort is submitted.
- Keep category creation controls and category detail behavior unchanged.

## Acceptance criteria

1. Blank search returns the full directory.
2. Search matches category name and description case-insensitively.
3. Search input is trimmed and capped at 120 characters.
4. A–Z is the default sort.
5. Z–A reverses name ordering.
6. Invalid sort values safely fall back to A–Z.
7. Pagination is 24 categories per page.
8. Pager links preserve active search and sort state.
9. The form does not preserve a stale page number when a new search/sort is submitted.
10. No schema, migration, dependency, worker, queue, AWS resource, paid service, or live-payment change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_category_directory
    python manage.py test --parallel 4
    docker compose config --quiet

## Out of scope

- Category popularity ranking
- Viewer-specific visible-video counts
- Category recommendations
- Fuzzy/full-text search
- Category detail pagination or filtering

## Delivered

- Added bounded category search across name and description.
- Search input is trimmed and capped at 120 characters.
- Added validated Name A–Z and Name Z–A ordering with safe fallback to A–Z.
- Paginated the Categories directory at 24 categories per page.
- Pager links preserve active search and sort state.
- New search/sort submissions do not preserve stale page numbers.
- Category creation and category detail behavior are unchanged.

## Verification results

- `python3 -m compileall -q video` passed locally.
- `docker compose config --quiet` passed locally.
- Focused Docker regression suite: 9/9 tests passed in 0.240s.
- GitHub Actions Django checks run #620 passed configuration and migration-drift checks and all 917 tests with one expected skip.
