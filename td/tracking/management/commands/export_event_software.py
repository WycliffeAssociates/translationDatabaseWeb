import codecs
import csv

from django.core.management.base import BaseCommand

from td.tracking.tasks import export_event_data


class Command(BaseCommand):
    help = "Export Event Software information"

    def handle(self, *args, **options):
        file_name = "Event_Software.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            for e in export_event_data():
                software = e.get("software", [])
                for s in software:
                    writer.writerow([e.get("name"), s.get("name")])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
