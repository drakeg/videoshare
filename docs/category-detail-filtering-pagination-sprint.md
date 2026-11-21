# Category detail filtering and pagination sprint

## Goal

Make category detail pages usable as their video collections grow without changing the platform's centralized visibility rules.

## Delivered

- In-category search across title, description, creator username, and channel name.
- Sort options for newest, most viewed, and most liked videos.
- Upload-date filters for today, week, month, year, or any time.
- Pagination at 24 videos per page.
- Filter-preserving pagination links.
- Regression coverage for category scoping, filtering, sorting, pagination, and private-video exclusion.

## Acceptance criteria

- Category pages never expose videos hidden by `Video.objects.visible_to(user)`.
- Search input is trimmed and capped at 120 characters.
- Invalid sort/upload values fall back safely.
- Page navigation preserves active filters.
- CI and repository standards checks pass before merge.
