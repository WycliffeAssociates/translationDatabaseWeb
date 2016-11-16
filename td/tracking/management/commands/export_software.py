import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Software


class Command(BaseCommand):
    help = "Export Outputs information"

    def handle(self, *args, **options):
        file_name = "Software.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["name"])

            for s in Software.objects.all():
                if s.name.lower() != "other":
                    writer.writerow([s.name])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
