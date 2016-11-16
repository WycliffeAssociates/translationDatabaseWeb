import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Hardware


class Command(BaseCommand):
    help = "Export Outputs information"

    def handle(self, *args, **options):
        file_name = "Hardware.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["name"])
            for h in Hardware.objects.all():
                if h.name.lower() != "other":
                    writer.writerow([h.name])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
