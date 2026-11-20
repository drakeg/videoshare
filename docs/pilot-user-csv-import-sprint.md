# Bulk Pilot User CSV Import Sprint

## Goal

Reduce onboarding time for multi-user SMB pilots by importing multiple ordinary users from a validated CSV while keeping public registration closed.

## Scope

- Add a staff-only CSV upload action to Pilot Users.
- Require UTF-8 CSV with headers: `username,email`; allow optional `first_name,last_name`.
- Bound uploads to 100 KB and 200 non-blank data rows.
- Validate the entire file before creating any users.
- Reject missing headers, malformed UTF-8/CSV, blank required fields, invalid emails, duplicates within the file, and username/email collisions with existing accounts.
- Create all users atomically only when every row is valid.
- Create only active, non-staff, non-superuser accounts through the existing provisioning service.
- On success, return a downloadable CSV containing username, email, and password-setup URL for operator delivery.
- Never include temporary plaintext passwords.
- Add focused security, validation, rollback, and success-output tests.

## Commercial rationale

Small and medium business pilots often begin with a cohort rather than one viewer. Repeating single-user provisioning manually adds setup/support time and makes larger trials unnecessarily expensive to operate.

## Acceptance criteria

1. Only staff can import users.
2. GET is not accepted by the import endpoint.
3. Required headers are enforced; optional names are supported.
4. Uploads over 100 KB or more than 200 rows are rejected.
5. Any invalid row or duplicate causes zero users to be created.
6. Duplicate username/email checks are case-insensitive both within the CSV and against the database.
7. Successful imports create only active ordinary users.
8. Successful response is a CSV attachment with setup URLs and no plaintext passwords.
9. Each returned setup URL reaches the branded password setup flow.
10. No migration, runtime dependency, paid service, live-payment, or AWS resource change is introduced.

## Verification

    python manage.py test video.test_pilot_user_csv_import
    python manage.py test --parallel 4
    docker compose config --quiet

## Delivered

- Added a staff-only CSV import form to Pilot Users.
- Added UTF-8/header/size/row-count validation with a 100 KB / 200-user limit.
- Rejects missing or unexpected headers, malformed UTF-8/CSV, extra row values, invalid fields, duplicates within the file, and case-insensitive collisions with existing users.
- Validates the complete file before any account creation.
- Creates all users atomically through the existing ordinary-user provisioning service only after validation succeeds.
- Successful imports download `pilot-user-setup-links.csv` containing username, email, and signed setup URL only.
- Added operator documentation and 10 focused rollback/security/output tests.

## Verification results

- Focused Docker CSV-import suite passed 10/10 in 3.694s.
- `python3 -m compileall -q video` passed locally.
- `git diff --check` passed locally.
- `docker compose config --quiet` passed locally.
- GitHub Actions Django checks run #664 passed configuration and migration-drift checks and all 978 tests with one expected skip.
- Repository standards workflow run #26 passed.
