import codecs
import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Charter


class Command(BaseCommand):
    help = "Export charter's contact person"

    def handle(self, *args, **options):
        file_name = "Charter_ContactPerson.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)
            file_name = "Charter_ContactPerson.xlsx"

            writer.writerow([
                "first_name",
                "last_name"
            ])

            names = [charter.contact_person for charter in Charter.objects.all()]
            names2 = []

            for name in list(set(names)):
                if "/" in name:
                    sub_names = name.split("/")
                    for sub_name in sub_names:
                        names2.append(sub_name)
                elif ", " in name:
                    sub_names = name.split(", ")
                    for sub_name in sub_names:
                        names2.append(sub_name)
                else:
                    names2.append(name)

            for name in names2:
                name_parts = name.split(" ")
                first_name = name_parts[0] or "Unknown"
                last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"
                writer.writerow([first_name, last_name])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
