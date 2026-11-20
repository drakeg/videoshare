# Prioritized backlog

| Priority | Item | Why it matters | Status |
| --- | --- | --- | --- |
| P0 | Keep CI/build/deployment green | Broken software blocks every user and pilot | Ongoing |
| P0 | Align local Docker full-suite execution with CI parallelism | Shorten development feedback loops and avoid unnecessary serial test time | Implemented in PR #288; host Docker daemon blocked full local run |
| P0 | Keep Mad Mallard repository standards current | Makes development/review/release behavior repeatable | Ongoing |
| P0 | SMB pilot deployment preflight | Reduce setup mistakes and customer-demo risk | Delivered in PR #286 |
| P1 | Choose and add an explicit open-source license | Public source without a license does not grant normal reuse rights; license choice requires owner authorization | Owner decision required |
| P1 | Validate SMB buyer/problem interviews | Avoid building commercialization features without demand evidence | Planned |
| P1 | Branded portal/demo gaps identified by pilot audit | Strengthen value versus generic public video hosting | Initial branding control delivered; further discovery required |
| P1 | Privacy/access workflow gaps identified by pilot audit | SMB training/client content often needs controlled access | Private portal + registration control delivered; further discovery required |
| P0 | Closed-pilot operator account provisioning workflow | Reduce admin/support friction when public registration is disabled | Delivered in PR #290 |
| P0 | Existing pilot user setup-link recovery | Let staff recover onboarding/reset without Django admin or public signup | Delivered in PR #291 |
| P0 | Bulk pilot user CSV import | Reduce repetitive onboarding work for multi-user SMB pilots | Delivered in PR #292 |
| P1 | Pilot user directory search/filter/pagination | Keep larger closed-pilot cohorts manageable after bulk import | Next |
| P1 | Optional pilot-user setup email delivery | Reduce manual setup-link delivery while keeping providers optional | Delivered in PR #293 |
| P1 | Customer-facing deployment/runbook hardening | Reduce setup/support cost for pilots | Preflight delivered; continue as deployment needs emerge |
| P0 | Accessibility regression checks for key workflows | Reduces product and customer risk | Delivered in PR #287 |
| P2 | Category detail filtering/pagination | Useful scale improvement but lower commercial urgency | Backlog |
| P2 | Additional discovery/recommendation ranking | Useful engagement work after pilot requirements are clearer | Backlog |

## Prioritization rules

P0 defects and broken CI/build/deployment take precedence. Otherwise prioritize work that improves a credible SMB demo, reduces customer setup/support cost, or validates willingness to pay. Do not report market validation until actual customer evidence exists.
