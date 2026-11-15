# Channel Directory Sorting Sprint

## Goal

Let viewers choose how the Channels directory is ordered while preserving the search, pagination, moderation visibility, and statistics delivered in the previous sprint.

## Scope

- Keep **Most subscribers** as the default ordering.
- Add **Most public videos** and **Name A-Z** sort choices.
- Validate the requested sort server-side and fall back to the default for unknown values.
- Apply sorting after the existing availability/search filters and count annotations, but before pagination.
- Preserve both search and sort in pagination links.
- Keep search/sort submission page-reset behavior.
- Preserve suspended-channel visibility boundaries and existing channel statistics.

## Acceptance criteria

1. The default directory ordering remains subscriber count descending, then name, then primary key.
2. Viewers can sort by public-video count descending or channel name ascending.
3. Unknown sort values safely fall back to the default.
4. Search combines with every supported sort option.
5. Pagination preserves the active search and sort.
6. Existing moderation visibility and count annotations remain unchanged.
7. No schema, migration, dependency, worker, queue, AWS resource, paid service, or live-payment change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_channel_directory
    python manage.py test --parallel 4
    docker compose config --quiet
    docker compose run --build --rm test

## Out of scope

- Fuzzy/full-text search
- Search ranking changes
- Category/tag filters
- Recommendation ranking
- Background indexing

## Delivered

- Most subscribers remains the default ordering.
- Added Most public videos and Name A-Z ordering.
- Unknown sort values safely fall back to the default.
- Search and sort are applied before pagination and preserved in pager links.
- Existing moderation visibility and annotated subscriber/public-video counts are unchanged.
- Added regression coverage for all sort choices, fallback behavior, and pager state.

## Verification

GitHub Actions Django checks run #611 passed:

- Django configuration checks passed.
- Migration drift check passed.
- All 899 tests passed with one expected skip.
- Local source compilation with `python3 -m compileall -q video` passed.
- Docker verification was attempted locally, but the host Docker daemon was occupied by another Compose operation and did not progress to Django output during this sprint.
