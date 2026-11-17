# Channel Content Sorting Sprint

## Goal

Let viewers order a channel's visible standard videos and Shorts while preserving channel search, visibility boundaries, and independent pagination.

## Scope

- Keep **Newest** as the default ordering.
- Add **Oldest** and **Most viewed** sort choices.
- Validate requested sort values server-side with safe fallback to Newest.
- Apply the selected sort consistently to both standard videos and Shorts.
- Preserve the active search and sort in both pager link sets.
- Reset both pagers when search or sort is submitted.
- Keep existing page sizes and visibility behavior unchanged.

## Acceptance criteria

1. Newest remains the default and uses publication date descending with primary key descending as a deterministic tie-break.
2. Oldest orders by publication date ascending with primary key ascending.
3. Most viewed orders by views descending, then publication date descending, then primary key descending.
4. Unknown sort values safely fall back to Newest.
5. Search combines correctly with every sort choice.
6. Both standard-video and Shorts pagination preserve the active search and sort plus the other section's page.
7. Submitting the form resets both pagers.
8. Existing visibility rules, page sizes, and content separation remain unchanged.
9. No schema, migration, dependency, worker, queue, AWS resource, paid service, or live-payment change is introduced.

## Verification

    python manage.py check
    python manage.py makemigrations --check --dry-run
    python manage.py test video.test_channel_content_pagination
    python manage.py test --parallel 4
    docker compose config --quiet
    docker compose run --build --rm test

## Out of scope

- Separate sort choices for videos and Shorts
- Relevance ranking
- Trending/time-decay scoring
- Date filters
- Background indexing
- Recommendation changes
