import codecs
import csv
import re

from django.core.management.base import BaseCommand

from td.tracking.tasks import export_material_data


class Command(BaseCommand):
    help = "Export Material information"

    def handle(self, *args, **options):
        file_name = "Materials.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            writer.writerow(["name", "licensed"])

            pattern = re.compile(r'[;,] ')
            temp = []

            # Split multiple entries in one line into different lines
            for m in export_material_data():
                entries = pattern.split(m.get("name"))
                for entry in entries:
                    temp.append((entry, m.get("licensed")))

            for entry, licensed in list(set(temp)):
                writer.writerow([entry, licensed])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
