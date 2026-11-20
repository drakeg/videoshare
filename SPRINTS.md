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

## Current sprint — Local Docker test parity

**Goal:** Align the local Docker full-suite runner with CI's parallel test execution after the serial runner was observed to be unnecessarily slow.

**Deliverables**
- [ ] Configurable `DJANGO_TEST_PROCESSES` with default 4
- [ ] Docker test runner uses Django `--parallel`
- [ ] GitHub Actions uses the same process-count variable
- [ ] Runtime regression coverage and documentation
- [ ] Full local Docker verification

No live payment activation or paid infrastructure is required.
