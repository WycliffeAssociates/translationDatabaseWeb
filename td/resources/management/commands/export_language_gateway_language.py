import csv

from django.core.management.base import BaseCommand

from td.tracking.models import Language


class Command(BaseCommand):
    help = "Export many-to-many relationships between language and itself (Gateway Language)"

    def handle(self, *args, **options):
        languages = Language.objects.all()
        file_name = "languages_gateway_language.csv"

        with open(file_name, "wb") as csvfile:
            writer = csv.writer(csvfile)
            for l in languages:
                if l.gateway_language is not None:
                    writer.writerow([l.lc, l.gateway_language.lc])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
