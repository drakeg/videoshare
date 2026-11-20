# Accessibility Regression Gate Sprint

## Goal

Add a zero-cost rendered-HTML accessibility regression gate for the highest-value viewer, authentication, creator, and private-pilot workflows.

## Scope

- Add a small standard-library HTML accessibility auditor used by tests only.
- Validate rendered documents for:
  - non-empty `<html lang>`;
  - non-empty page title;
  - working skip link to `#main-content`;
  - unique element IDs;
  - valid `aria-labelledby` references;
  - `alt` attributes on images;
  - accessible names for links and buttons;
  - accessible labels/names for non-hidden inputs, selects, and textareas.
- Run the auditor against core anonymous viewer pages.
- Run it against login/registration flows.
- Run it against authenticated creator pages, including upload.
- Verify the private-portal anonymous path still lands on an accessible login page.
- Fix any concrete markup regressions discovered by the gate.
- Keep the checks inside the existing Django CI; add no browser runtime, npm stack, paid scanner, or application dependency.

## Commercial rationale

Accessibility defects create customer risk and support friction, especially for SMB portals used for training or internal content. A deterministic baseline gate catches common structural regressions on every PR without adding infrastructure cost.

## Acceptance criteria

1. The auditor identifies unlabeled form controls and unnamed interactive elements.
2. Missing image alt attributes are detected.
3. Duplicate IDs and broken `aria-labelledby` references are detected.
4. The shared shell is checked for language, title, skip link, and main-content target.
5. Core viewer/auth pages pass the gate.
6. An authenticated creator upload workflow passes the gate.
7. The private-portal login experience passes the gate.
8. Tests prove the auditor catches representative bad markup.
9. No runtime dependency, schema migration, paid service, or AWS resource is introduced.

## Verification

    python manage.py test video.test_accessibility_regression
    python manage.py test --parallel 4
    docker compose config --quiet

## Boundaries

This is a regression baseline, not a claim of WCAG conformance and not a replacement for periodic browser/assistive-technology testing.
