import csv

from django.core.management.base import BaseCommand

from td.gl_tracking.models import Partner


class Command(BaseCommand):
    help = "Export Partner's organizational info"

    def handle(self, *args, **options):
        file_name = "Partner_Organization.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow([
                "name",
                "address",
                "city",
                "province",
                "country",
                "start_date",
                "end_date",
                "is_active"
            ])

            for p in Partner.objects.all():
                writer.writerow([
                    p.name.encode("utf-8"),
                    p.address,
                    p.city,
                    p.province,
                    p.country.name.encode("utf-8"),
                    p.partner_start,
                    p.partner_end,
                    p.is_active
                ])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
