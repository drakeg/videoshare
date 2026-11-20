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

For password-reset email delivery, configure the deployment's Django email backend. Closed-pilot provisioning itself does not automatically send email in this sprint; the operator receives the setup URL directly.

## Duplicate protection

The provisioning form rejects duplicate usernames and duplicate email addresses case-insensitively. A failed submission does not create a partial account.

## Security boundaries

- Only staff can access the Pilot Users page.
- Pilot Users creates only non-staff, non-superuser accounts.
- Elevated account creation remains in Django admin.
- Public registration stays controlled by `DJANGO_ALLOW_PUBLIC_REGISTRATION`.
- Private portal access stays controlled by `DJANGO_PRIVATE_PORTAL`.
- Account suspension/reactivation remains in the existing Site Administration moderation workflow.
