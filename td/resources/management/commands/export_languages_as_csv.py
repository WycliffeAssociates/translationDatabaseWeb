import csv
from openpyxl import Workbook

from django.core.management.base import BaseCommand

from td.tracking.models import Language


class Command(BaseCommand):
    help = "Export custom languages information to a CSV file."

    def handle(self, *args, **options):
        languages = Language.objects.all()
        file_name = "languages.csv"

        with open(file_name, "wb") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                "id",
                "code",
                "iso_639_3",
                "name",
                "anglicized_name",
                "alternate_names",
                "direction",
                "home_country",
                "region",
                "speaking_countries",
                "gateway_language",
                "gateway_flag",
                "native_speakers"
            ])
            for l in languages:
                writer.writerow([
                    l.id,
                    l.code,
                    l.iso_639_3,
                    l.name.encode("utf-8"),
                    l.anglicized_name.encode("utf-8"),
                    # ",".join(l.alt_name_all).encode("utf-8"),
                    l.alt_names.encode("utf-8"),
                    l.get_direction_display(),
                    l.country.code if l.country else "",
                    l.wa_region.slug if l.wa_region else "",
                    ",".join(l.cc_all).encode("utf-8"),
                    l.gateway_language.code if l.gateway_language else "",
                    l.gateway_flag,
                    l.native_speakers if l.native_speakers >= 0 else 0
                ])

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
