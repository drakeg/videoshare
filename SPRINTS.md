# Sprint plan

## Product direction

VideoShare is being developed as an open-source, self-hostable video platform with a commercialization hypothesis around SMBs and creator-led businesses that need a branded, controllable video hub without building their own platform.

Completed historical sprint detail remains in `docs/roadmap.md`. This file is the concise current plan.

## Recently completed

- Channel directory search, pagination, and sorting
- Channel content search and sorting
- Local Docker/LAN reliability
- Creator video/trash search and pagination
- Category directory search/pagination is implemented in PR #279 and remains pending merge/review

## Current sprint — Repository standards adoption

**Goal:** Bring the repository into compliance with the Mad Mallard Development Standards without altering completed application behavior.

**Deliverables**
- [x] Required governance/development documents
- [x] Verified README badge block and badge maintenance tooling
- [x] Standards validation workflow
- [x] Dependency security workflow
- [x] SMB commercialization hypothesis and validation plan
- [ ] PR review/merge

**Acceptance:** standards audit/check passes, badge generation is idempotent, security/standards workflows are dynamic and read-only, existing Django/Terraform CI remains green.

## Next sprint — SMB pilot readiness

**Goal:** Improve the fastest credible path from a working demo to an SMB pilot.

Planned discovery/implementation order:
1. Audit existing branding, sharing, privacy, team, analytics, and onboarding flows against the pilot use case.
2. Choose the smallest missing user-visible capability that materially improves an SMB demo.
3. Implement, deploy locally, test real workflows, fix defects, and update pilot documentation.

No live payment activation or paid infrastructure is required for this sprint.
