# Closed Pilot User Provisioning

Use the staff-only **Pilot Users** page when a private deployment has public registration disabled and an operator needs to add viewers manually.

## Open the workflow

1. Sign in with a staff account.
2. Open **Site admin**.
3. Select **Pilot users**.
4. Enter the user's username, email address, and optional first/last name.
5. Select **Create pilot user**.

The workflow creates an active **ordinary user only**. It cannot create staff or superuser accounts.

## Password setup

After account creation, the page displays a password-setup URL.

- No temporary plaintext password is displayed or emailed.
- The account receives a random internal password value that the operator never needs to know.
- Share the setup URL through an approved channel.
- Treat the URL as sensitive until the user sets a password.
- Once the user sets a password, the old reset token becomes invalid.

The user follows the link, chooses a password, and then signs in normally.

## Existing users and forgotten passwords

The normal **Lost password?** link on the login page now uses the branded password-reset flow.

Pilot-user setup/reset email delivery is optional and disabled by default. Manual setup/reset URLs always remain available.

To enable staff-triggered delivery, configure the deployment's Django email backend and set:

```text
DJANGO_PILOT_USER_SETUP_EMAIL_ENABLED=true
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DJANGO_DEFAULT_FROM_EMAIL=noreply@example.com
```

Use the SMTP/backend-specific host, port, credentials, and TLS/SSL settings already supported by the project. The built-in console backend is useful for local testing but does not deliver mail externally; `pilot_check` warns if pilot-user email is enabled with console/locmem/dummy backends.

When enabled:

- the provisioning form offers **Email the password-setup link** for a new individual account;
- eligible existing users show **Email reset link** alongside **Generate reset link**;
- the manual signed URL is still shown after the action whether email succeeds or fails;
- backend delivery failures do not roll back account creation or change an existing user's password;
- email subject/body use `DJANGO_SITE_NAME` and `DJANGO_DEFAULT_FROM_EMAIL`.

Bulk CSV imports intentionally continue to download setup links without automatically sending email so a provider outage cannot create ambiguous partial delivery across a cohort.

## Duplicate protection

The provisioning form rejects duplicate usernames and duplicate email addresses case-insensitively. A failed submission does not create a partial account.

## Security boundaries

- Only staff can access the Pilot Users page.
- Pilot Users creates only non-staff, non-superuser accounts.
- Elevated account creation remains in Django admin.
- Public registration stays controlled by `DJANGO_ALLOW_PUBLIC_REGISTRATION`.
- Private portal access stays controlled by `DJANGO_PRIVATE_PORTAL`.
- Account suspension/reactivation remains in the existing Site Administration moderation workflow.


## Bulk CSV import

For a multi-user pilot, use the **Import users from CSV** form on the Pilot Users page.

Required headers:

```text
username,email
```

Optional headers:

```text
first_name,last_name
```

Example:

```csv
username,email,first_name,last_name
alice,alice@example.com,Alice,Example
bob,bob@example.com,Bob,Example
```

Limits and safety rules:

- UTF-8 CSV only
- maximum 100 KB
- maximum 200 non-blank user rows
- only `username`, `email`, `first_name`, and `last_name` headers are accepted
- usernames and emails must be unique case-insensitively within the file and against existing accounts
- the complete file is validated before any user is created
- if any row is invalid, **zero users are created**
- successful imports create ordinary active users only

On success, the browser downloads `pilot-user-setup-links.csv` containing each new username, email address, and signed password-setup URL. The download contains no temporary plaintext passwords. Treat the setup-link CSV as sensitive until users have completed password setup.
