import codecs
import csv

import re

from django.core.management.base import BaseCommand

from td.tracking.models import Event


class Command(BaseCommand):
    help = "Export event's contact person"

    def handle(self, *args, **options):
        file_name = "Event_ContactPerson.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            writer.writerow([
                "first_name",
                "last_name"
            ])

            names = [event.contact_person for event in Event.objects.all()]
            names2 = []

            pattern = re.compile(r'/|,\s')

            for name in list(set(names)):
                sub_names = pattern.split(name)
                for sub_name in sub_names:
                    names2.append(sub_name)

            for name in names2:
                name_parts = name.split(" ")
                first_name = name_parts[0] or "Unknown"
                last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
                writer.writerow([first_name.encode("utf-8"), last_name.encode("utf-8")])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
