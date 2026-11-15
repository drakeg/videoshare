# Channel Content Search Sprint

## Goal

Let viewers quickly find a creator's visible uploads from the channel page without changing visibility, ranking, or pagination boundaries.

## Scope

- Add one bounded search field to the channel page.
- Match visible standard videos and Shorts by title, description, category, structured tag, or hashtag.
- Trim surrounding whitespace and cap the query at 120 characters.
- Apply the existing channel/video visibility rules before search.
- Apply search before the existing independent standard-video and Shorts pagination.
- Preserve the active query in both pager link sets.
- Reset both pagers when a new search is submitted.
- Keep newest-first ordering and current page sizes unchanged.
- Provide a useful no-results state when a search matches neither section.

## Acceptance criteria

1. Search is limited to content already visible to the current viewer.
2. Search matches title, description, category, tag, and hashtag case-insensitively.
3. Search filters both standard videos and Shorts before pagination.
4. Blank or whitespace-only search behaves as unfiltered.
5. Search input is normalized and capped at 120 characters.
6. Both pager sets preserve the active query and the other section's current page.
7. Submitting a new search resets both pagers.
8. Existing newest-first ordering and page sizes remain unchanged.
9. No schema, migration, dependency, worker, queue, AWS resource, paid service, or live-payment change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_channel_content_pagination
    python manage.py test --parallel 4
    docker compose config --quiet
    docker compose run --build --rm test

## Out of scope

- Search relevance ranking
- Fuzzy or full-text search
- Per-section independent search terms
- Sorting controls
- Date filters
- Background indexing
- Recommendation changes
