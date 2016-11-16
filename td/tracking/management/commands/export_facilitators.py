import codecs
import csv

import re

from django.core.management.base import BaseCommand

from td.tracking.tasks import export_facilitator_data


class Command(BaseCommand):
    help = "Export event's facilitators"

    def handle(self, *args, **options):
        file_name = "Event_Facilitators.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)
            file_name = "Event_Facilitators.xlsx"

            writer.writerow([
                "first_name",
                "last_name"
            ])

            facilitators = export_facilitator_data()

            names = [f.get("name", "") for f in facilitators]
            # names2 = []

            # pattern = re.compile(r'/|,\s')

            # for name in list(set(names)):
            #     sub_names = pattern.split(name)
            #     for sub_name in sub_names:
            #         names2.append(sub_name)

            # for name in names2:
            for name in names:
                name_parts = name.split(" ")
                first_name = name_parts[0] or "Unknown"
                last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
                writer.writerow([
                    first_name.encode("utf-8"),
                    last_name.encode("utf-8"),
                ])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
