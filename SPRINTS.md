# Sprint plan

## Product direction

VideoShare is being developed as an open-source, self-hostable video platform with a commercialization hypothesis around SMBs and creator-led businesses that need a branded, controllable video hub without building their own platform.

Completed historical sprint detail remains in `docs/roadmap.md`. This file is the concise current plan.

## Recently completed

- Repository standards adoption (#281)
- Private portal mode (#283)
- Category directory search/pagination (#279)
- SMB pilot configuration: branding + registration control (#285)
- Stripe 17.1 runtime update (#280)

## Completed sprint — SMB pilot deployment preflight

**Delivered:** read-only PASS/WARN/FAIL preflight service and `manage.py pilot_check` with public/private profiles, deployment hardening, focused regression coverage, and operator documentation.

**Verification:** focused Docker 11/11; GitHub Actions run #648 passed all 945 tests with one expected skip; real local public preflight reported 4 PASS / 2 WARN / 0 FAIL.

## Completed sprint — Accessibility regression gate

**Delivered:** rendered-HTML structural accessibility auditing, critical design-token contrast checks, core viewer/auth/creator/private-pilot coverage, and two contrast fixes.

**Verification:** focused Docker 7/7; GitHub Actions run #650 passed all 952 tests with one expected skip; repository standards passed.

## Completed sprint — Local Docker test parity

**Delivered:** configurable `DJANGO_TEST_PROCESSES`, matching Docker/CI parallel execution, regression coverage, and developer documentation.

**Verification:** GitHub Actions run #652 passed all 953 tests with one expected skip; Compose and shell-runner behavior verified locally. Full local container execution remains blocked by the host Docker daemon and is not claimed as passed.

## Completed sprint — Closed pilot user provisioning

**Delivered:** staff-only Pilot Users page, ordinary-user provisioning, secure password-setup links, branded password recovery, accessibility coverage, and operator documentation.

**Verification:** focused Docker 15/15; GitHub Actions run #660 passed all 961 tests with one expected skip; repository standards passed.

## Completed sprint — Existing pilot user reset links

**Delivered:** staff-only reset/setup-link generation for active ordinary users, eligibility enforcement, branded output, and password/account-state safety coverage.

**Verification:** focused Docker 14/14; GitHub Actions run #662 passed all 968 tests with one expected skip; repository standards passed.

## Completed sprint — Bulk pilot user CSV import

**Delivered:** staff-only bounded CSV import, complete pre-validation, atomic ordinary-user creation, duplicate/collision safeguards, and downloadable setup-link CSV output.

**Verification:** focused Docker 10/10; GitHub Actions run #664 passed all 978 tests with one expected skip; repository standards passed.

## Next sprint — Pilot user onboarding delivery

**Goal:** Reduce manual link-delivery friction while keeping email/invitation delivery opt-in and provider-agnostic.

No live payment activation or paid infrastructure is required.
