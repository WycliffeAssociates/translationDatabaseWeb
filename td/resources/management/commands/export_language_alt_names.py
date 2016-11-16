import codecs
import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Language


class Command(BaseCommand):
    help = "Export many-to-many relationships for Language and LangAltName"

    def handle(self, *args, **options):
        languages = Language.objects.all()
        file_name = "Languages_AltLangNames.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            for l in languages:
                for n in l.alt_name_all:
                    writer.writerow([l.lc, n])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
