# White-label homepage branding sprint

## Goal

Let an SMB pilot present customer-specific messaging without modifying application code or templates.

## Delivered

- Environment-driven site tagline.
- Environment-driven homepage headline and supporting copy.
- Shared branding context across templates.
- Customer tagline exposed as the page meta description.
- Pilot preflight warning when homepage messaging remains on the VideoShare defaults.
- Regression coverage for rendered branding and preflight behavior.

## Configuration

```text
DJANGO_SITE_NAME=Acme Training TV
DJANGO_SITE_TAGLINE=Training that travels with your team.
DJANGO_HOME_HEADLINE=Everything your crew needs to learn.
DJANGO_HOME_SUBTITLE=Private, branded video training for field teams and managers.
```

## Acceptance criteria

- Branding changes require environment configuration only.
- Empty environment values fall back to safe defaults.
- Customer-facing homepage copy is available through the shared context processor.
- The pilot preflight identifies incomplete default branding.
- No schema, migration, external service, paid infrastructure, or live-payment change is introduced.
