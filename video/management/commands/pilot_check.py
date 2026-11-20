from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from video.services.pilot_preflight import run_pilot_preflight


class Command(BaseCommand):
    help = "Run a read-only SMB pilot configuration/deployment preflight."

    def add_arguments(self, parser):
        parser.add_argument(
            "--profile",
            choices=("public", "private"),
            default="public",
            help="Access profile to validate (default: public).",
        )
        parser.add_argument(
            "--deployment",
            action="store_true",
            help="Also require production-style debug/HTTPS/cookie hardening.",
        )

    def handle(self, *args, **options):
        profile = options["profile"]
        deployment = options["deployment"]
        results = run_pilot_preflight(
            settings,
            profile=profile,
            deployment=deployment,
        )

        self.stdout.write(
            f"Pilot preflight: profile={profile} deployment={'yes' if deployment else 'no'}"
        )
        counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
        for result in results:
            counts[result.status] += 1
            line = f"[{result.status}] {result.code}: {result.message}"
            if result.status == "PASS":
                self.stdout.write(self.style.SUCCESS(line))
            elif result.status == "WARN":
                self.stdout.write(self.style.WARNING(line))
            else:
                self.stdout.write(self.style.ERROR(line))
            self.stdout.write(f"  -> {result.guidance}")

        self.stdout.write(
            f"Summary: {counts['PASS']} passed, {counts['WARN']} warning(s), {counts['FAIL']} failure(s)."
        )
        if counts["FAIL"]:
            raise CommandError(
                "Pilot preflight failed. Resolve the FAIL items above and run the command again."
            )

        if counts["WARN"]:
            self.stdout.write(
                self.style.WARNING(
                    "Pilot preflight completed with warnings; review them before the customer demo."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("Pilot preflight passed with no warnings."))
