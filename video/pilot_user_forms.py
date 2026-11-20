from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

PILOT_USER_CSV_MAX_BYTES = 100 * 1024


class PilotUserCsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label="Pilot users CSV",
        help_text="UTF-8 CSV up to 100 KB. Required headers: username,email. Optional: first_name,last_name.",
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data["csv_file"]
        if csv_file.size > PILOT_USER_CSV_MAX_BYTES:
            raise forms.ValidationError("CSV files must be 100 KB or smaller.")
        return csv_file


class PilotUserProvisioningForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "A user with that username already exists.",
                code="unique",
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "A user with that email address already exists.",
                code="unique",
            )
        return email
