import csv

from django.core.management.base import BaseCommand

from td.gl_tracking.models import Partner


class Command(BaseCommand):
    help = "Export Partner's contact info"

    def handle(self, *args, **options):
        file_name = "Partner_ContactPerson.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow([
                "organization",
                "name",
                "phone",
                "email",
                "notes"
            ])

            for p in Partner.objects.all():
                if p.contact_name:
                    writer.writerow([
                        p.name.encode("utf-8"),
                        p.contact_name,
                        p.contact_email,
                        p.contact_phone,
                        p.notes
                    ])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
