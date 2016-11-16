import csv
import re

from django.core.management.base import BaseCommand

from td.tracking.models import Charter, Event, Output


class Command(BaseCommand):
    help = "Export Outputs information"

    def handle(self, *args, **options):
        file_name = "Outputs.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["name"])

            for o in Output.objects.all():
                if o.name.lower() != "other":
                    writer.writerow([o.name])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
