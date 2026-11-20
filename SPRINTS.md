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

## Current sprint — Accessibility regression gate

**Goal:** Add automated rendered-HTML accessibility regression checks for the highest-value viewer/auth/creator/private-pilot workflows without introducing a paid scanner or new runtime dependency.

**Deliverables**
- [ ] Standard-library HTML accessibility auditor
- [ ] Core viewer/auth page regression coverage
- [ ] Creator upload regression coverage
- [ ] Private-portal login regression coverage
- [ ] Fix concrete markup defects found by the gate
- [ ] Full CI verification and reviewable PR

No live payment activation or paid infrastructure is required.
