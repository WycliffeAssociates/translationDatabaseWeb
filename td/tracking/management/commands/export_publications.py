import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Publication


class Command(BaseCommand):
    help = "Export Publication information"

    def handle(self, *args, **options):
        file_name = "Publications.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["name"])
            for p in Publication.objects.all():
                if p.name.lower() != "other":
                    writer.writerow([p.name])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
