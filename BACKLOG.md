# Prioritized backlog

| Priority | Item | Why it matters | Status |
| --- | --- | --- | --- |
| P0 | Keep CI/build/deployment green | Broken software blocks every user and pilot | Ongoing |
| P0 | Align local Docker full-suite execution with CI parallelism | Shorten development feedback loops and avoid unnecessary serial test time | Implemented in PR #288; host Docker daemon blocked full local run |
| P0 | Keep Mad Mallard repository standards current | Makes development/review/release behavior repeatable | Ongoing |
| P0 | SMB pilot deployment preflight | Reduce setup mistakes and customer-demo risk | Delivered in PR #286 |
| P1 | Choose and add an explicit open-source license | Public source without a license does not grant normal reuse rights; license choice requires owner authorization | Owner decision required |
| P1 | Validate SMB buyer/problem interviews | Avoid building commercialization features without demand evidence | Planned |
| P1 | Branded portal/demo gaps identified by pilot audit | Strengthen value versus generic public video hosting | White-label homepage messaging delivered in PR #301 |
| P1 | Privacy/access workflow gaps identified by pilot audit | SMB training/client content often needs controlled access | Private portal + registration control delivered; branded sign-in and anonymous navigation delivered in PR #303 |
| P0 | Closed-pilot operator account provisioning workflow | Reduce admin/support friction when public registration is disabled | Delivered in PR #290 |
| P0 | Existing pilot user setup-link recovery | Let staff recover onboarding/reset without Django admin or public signup | Delivered in PR #291 |
| P0 | Bulk pilot user CSV import | Reduce repetitive onboarding work for multi-user SMB pilots | Delivered in PR #292 |
| P1 | Pilot user directory search/filter/pagination | Keep larger closed-pilot cohorts manageable after bulk import | Delivered in PR #294 |
| P1 | Pilot onboarding status visibility | Identify never-signed-in users who still need setup help | Delivered in PR #295 |
| P1 | Pilot user access-state controls | Suspend/reactivate ordinary pilot users without leaving the directory | Delivered in PR #296 |
| P1 | Filtered pilot user directory CSV export | Give operators a portable cohort/status record without sensitive setup tokens | Delivered in PR #297 |
| P1 | Optional pilot-user setup email delivery | Reduce manual setup-link delivery while keeping providers optional | Delivered in PR #293 |
| P1 | Customer-facing deployment/runbook hardening | Reduce setup/support cost for pilots | Preflight delivered; continue as deployment needs emerge |
| P0 | Accessibility regression checks for key workflows | Reduces product and customer risk | Delivered in PR #287 |
| P2 | Category detail filtering/pagination | Useful scale improvement but lower commercial urgency | Delivered in PR #299 |
| P2 | Additional discovery/recommendation ranking | Useful engagement work after pilot requirements are clearer | Delivered in PR #300 |
| P1 | Editorial visual refresh | Improve viewing hierarchy, mobile navigation and customer demo quality | Delivered in PR #304; manual visual QA pending |
| P2 | Watch-next topic relevance | Improve related-video discovery across channels | Delivered in PR #305 |
| P1 | Creator workspace refresh | Reduce creator navigation and library scanning friction | Awaiting CI and visual QA |

## Prioritization rules

P0 defects and broken CI/build/deployment take precedence. Otherwise prioritize work that improves a credible SMB demo, reduces customer setup/support cost, or validates willingness to pay. Do not report market validation until actual customer evidence exists.
