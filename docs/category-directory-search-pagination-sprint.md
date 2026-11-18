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
