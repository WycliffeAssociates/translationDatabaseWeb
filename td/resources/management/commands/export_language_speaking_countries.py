import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Language


class Command(BaseCommand):
    help = "Export many-to-many relationships between language and countries"

    def handle(self, *args, **options):
        languages = Language.objects.all()
        file_name = "languages_speaking_countries.csv"

        with open(file_name, "wb") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            for l in languages:
                speaking_countries = l.cc_all
                for c in speaking_countries:
                    writer.writerow([l.lc, c])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
