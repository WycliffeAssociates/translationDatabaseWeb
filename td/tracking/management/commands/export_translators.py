import codecs
import csv

from django.core.management.base import BaseCommand

from td.tracking.tasks import export_translator_data


class Command(BaseCommand):
    help = "Export Translator information"

    def handle(self, *args, **options):
        file_name = "Translators.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            writer.writerow([
                "name",
                "statement_of_faith",
                "translation_guidelines",
                "cc_by_sa",
            ])

            for t in export_translator_data():
                writer.writerow(
                    [t.get("name").encode("utf-8")] +
                    [t.get("docs_signed")] * 3
                )

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
