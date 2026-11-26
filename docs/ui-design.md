# Interface and Design System

## Delivered behavior

The application's prototype styling is replaced by an original, cohesive video-platform interface that is polished on desktop and mobile without reproducing another platform's branding or page layouts.

## Visual direction

- Warm off-white surfaces, deep ink text, and a coral-to-violet accent palette
- A compact sticky header, centered search, and responsive navigation drawer
- Rounded media cards with strong thumbnail treatment and restrained motion
- Clear page hierarchy, readable content widths, and consistent spacing
- Shared treatments for forms, tables, metrics, alerts, comments, and empty states
- Responsive layouts that remain useful from narrow phones through wide desktops

The design may use familiar video-product interaction patterns, but its name, colors, typography, shapes, and composition remain specific to VideoShare.

## Scope and acceptance criteria

- Refresh the global shell, navigation, search, and signed-in creator links.
- Establish reusable CSS tokens and components without adding a front-end build system.
- Refresh discovery cards, video playback/detail, channel/profile, playlists, history, notifications, search, forms, and creator management surfaces.
- Preserve route names, form actions, CSRF behavior, authorization boundaries, and existing test-visible copy.
- Provide visible keyboard focus, sufficient contrast, semantic landmarks, and reduced-motion support.
- Avoid paid services, new AWS resources, JavaScript frameworks, and externally hosted design assets.

## Local test plan

With Docker:

```bash
docker compose up --build --detach
docker compose ps
docker compose run --rm test
```

Without Docker:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Visual verification covers the homepage and video detail at desktop and mobile widths, plus keyboard navigation and empty states. Terraform is unaffected.

## Verification

- Django system checks passed.
- Migration-drift checks reported no changes.
- All 189 tests passed, including three focused interface-shell tests.
- Compose configuration, Docker shell scripts, and Python compilation validated.
- The homepage was inspected at 1440 × 900 and 390 × 844 with no horizontal overflow or browser errors.
- Video detail was inspected at desktop and phone widths; playback, creator information, and comments reflowed without overflow.
- The local Docker engine remained inaccessible from this workspace, so `docker compose run --rm test` remains the documented local handoff check.

## Out of scope

- Copying third-party branding, icons, or pixel-level layouts
- Recommendation, playback, upload, or permission changes
- Native mobile applications
- A front-end framework, asset pipeline, or third-party design service
- User-selectable themes in this first design-system pass


## Automated accessibility regression baseline

The Django test suite now audits rendered HTML for common structural regressions across core viewer, authentication, creator-upload, and private-portal login workflows. The standard-library auditor checks document language/title, skip-link/main targeting, unique IDs, `aria-labelledby` references, image `alt` attributes, interactive accessible names, and form-control labels.

Critical design-system color pairs are also checked with the WCAG contrast-ratio formula. The first run found and fixed two defects: the coral `--accent-deep` token was below 4.5:1 on the canvas, and the small side-navigation section label used a low-contrast hardcoded gray. The corrected values are regression-tested.

Run the focused gate with:

```bash
docker compose run --rm --entrypoint python test manage.py test video.test_accessibility_regression
```

This automated baseline is intentionally scoped. Passing it does not claim WCAG conformance and does not replace periodic keyboard, browser, screen-reader, zoom/reflow, or other assistive-technology testing.


## Editorial refresh

See `docs/editorial-visual-refresh.md` for the new visual direction and outstanding verification. Historical verification above applies to the earlier design, not the refresh.
