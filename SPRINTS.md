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

## Completed sprint — Optional pilot-user setup email

**Delivered:** disabled-by-default provider-agnostic setup/reset email delivery for individual pilot users, manual-link fallback, preflight warnings, and operator documentation.

**Verification:** focused Docker email/preflight 23/23; accessibility 8/8; GitHub Actions run #666 passed all 990 tests with one expected skip; repository standards passed.

## Completed sprint — Pilot user directory management

**Delivered:** bounded username/email/name search, account-state filtering, 50-user pagination, and preserved directory state.

**Verification:** GitHub Actions run #669 passed all 999 tests with one expected skip; repository standards passed.

## Completed sprint — Pilot onboarding status visibility

**Delivered:** last-successful-sign-in display, explicit Never signed in state, composable onboarding filtering, and preserved directory state.

**Verification:** GitHub Actions run #671 passed all 1004 tests with one expected skip; repository standards passed.

## Completed sprint — Pilot user access-state controls

**Delivered:** audited in-directory suspend/reactivate controls for ordinary pilot users with required reasons and safe return-state preservation.

**Verification:** GitHub Actions run #674 passed all 1012 tests with one expected skip; repository standards passed.

## Next sprint — Filtered pilot user directory export

**Goal:** Let staff download the currently filtered pilot-user directory for operator records without exporting passwords or setup/reset tokens.

No live payment activation or paid infrastructure is required.
