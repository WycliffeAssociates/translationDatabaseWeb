import codecs
import csv
import re

from django.core.management.base import BaseCommand

from td.tracking.models import Charter
from td.tracking.tasks import export_charter_data


class Command(BaseCommand):
    help = "Export charters information"

    def handle(self, *args, **options):
        file_name = "Charters.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            writer.writerow([
                "name",
                "language_code",
                "new_start",
                "start_date",
                "end_date",
                "accounting_number",
                "lead_dept_name",
                "contact_person",
                "partner_name",
            ])

            pattern = re.compile(r'/|,\s')

            for c in export_charter_data():
                # Only export the first contact name if there are multiples
                contact_name = pattern.split(c.get("contact_person"))[0]
                # Add "Unknown" as last name if contact name only has one word
                full_name = contact_name if len(contact_name.split(" ")) > 1 else contact_name + " Unknown"
                writer.writerow([
                    c.get("name"),
                    c.get("language_code"),
                    c.get("new_start"),
                    c.get("start_date"),
                    c.get("end_date"),
                    c.get("accounting_number"),
                    c.get("lead_dept_name"),
                    full_name,
                    c.get("partner_name"),
                ])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
