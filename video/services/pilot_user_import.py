import csv
import io

from video.pilot_user_forms import PilotUserProvisioningForm

PILOT_USER_CSV_MAX_ROWS = 200
PILOT_USER_CSV_REQUIRED_HEADERS = {"username", "email"}
PILOT_USER_CSV_ALLOWED_HEADERS = {
    "username",
    "email",
    "first_name",
    "last_name",
}


class PilotUserCsvValidationError(ValueError):
    def __init__(self, messages):
        self.messages = list(messages)
        super().__init__("; ".join(self.messages))


def validate_pilot_user_csv(uploaded_file):
    try:
        text = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise PilotUserCsvValidationError(
            ["The CSV must be valid UTF-8 text."]
        ) from error

    try:
        reader = csv.DictReader(io.StringIO(text), strict=True)
    except csv.Error as error:
        raise PilotUserCsvValidationError(
            [f"The CSV could not be parsed: {error}"]
        ) from error

    if reader.fieldnames is None:
        raise PilotUserCsvValidationError(
            ["The CSV must include a header row."]
        )

    headers = [str(header or "").strip().lower() for header in reader.fieldnames]
    if len(headers) != len(set(headers)):
        raise PilotUserCsvValidationError(
            ["The CSV header row contains duplicate column names."]
        )

    missing = sorted(PILOT_USER_CSV_REQUIRED_HEADERS - set(headers))
    unexpected = sorted(set(headers) - PILOT_USER_CSV_ALLOWED_HEADERS)
    header_errors = []
    if missing:
        header_errors.append(
            "Missing required CSV header(s): " + ", ".join(missing) + "."
        )
    if unexpected:
        header_errors.append(
            "Unexpected CSV header(s): "
            + ", ".join(unexpected)
            + ". Allowed headers are username, email, first_name, last_name."
        )
    if header_errors:
        raise PilotUserCsvValidationError(header_errors)

    rows = []
    errors = []
    seen_usernames = set()
    seen_emails = set()
    nonblank_row_count = 0

    try:
        parsed_rows = list(reader)
    except csv.Error as error:
        raise PilotUserCsvValidationError(
            [f"The CSV could not be parsed: {error}"]
        ) from error

    for line_number, raw_row in enumerate(parsed_rows, start=2):
        if None in raw_row:
            errors.append(
                f"Row {line_number}: contains more values than the CSV header declares."
            )
            continue

        row = {
            header: str(raw_row.get(original_header) or "").strip()
            for header, original_header in zip(headers, reader.fieldnames)
        }

        if not any(row.get(header, "") for header in PILOT_USER_CSV_ALLOWED_HEADERS):
            continue

        nonblank_row_count += 1
        if nonblank_row_count > PILOT_USER_CSV_MAX_ROWS:
            errors.append(
                f"Row {line_number}: the CSV may contain at most {PILOT_USER_CSV_MAX_ROWS} non-blank users."
            )
            continue

        form = PilotUserProvisioningForm(row)
        if not form.is_valid():
            for field_name, field_errors in form.errors.items():
                for field_error in field_errors:
                    errors.append(
                        f"Row {line_number} {field_name}: {field_error}"
                    )
            continue

        cleaned = form.cleaned_data
        username_key = cleaned["username"].casefold()
        email_key = cleaned["email"].casefold()

        if username_key in seen_usernames:
            errors.append(
                f"Row {line_number} username: duplicate username within this CSV."
            )
        if email_key in seen_emails:
            errors.append(
                f"Row {line_number} email: duplicate email address within this CSV."
            )
        if username_key in seen_usernames or email_key in seen_emails:
            continue

        seen_usernames.add(username_key)
        seen_emails.add(email_key)
        rows.append(cleaned)

    if not rows and not errors:
        errors.append("The CSV does not contain any non-blank user rows.")

    if errors:
        raise PilotUserCsvValidationError(errors)

    return rows
