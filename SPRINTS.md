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

## Current sprint — SMB pilot deployment preflight

**Goal:** Add a deterministic, read-only preflight command for public and private SMB pilot deployments.

**Deliverables**
- [ ] Reusable PASS/WARN/FAIL preflight service
- [ ] `manage.py pilot_check` command with public/private profiles
- [ ] Optional deployment-hardening checks
- [ ] Focused regression tests
- [ ] README/deployment documentation
- [ ] Full CI verification and reviewable PR

**Acceptance:** operators receive actionable failures/warnings for branding, access policy, hosts, secrets, debug mode, HTTPS redirect, and secure cookies without the command mutating state.

## Next sprint — SMB pilot operations

**Goal:** Continue reducing pilot setup/support friction based on the next highest-value non-blocked backlog item after preflight is validated.

No live payment activation or paid infrastructure is required.
