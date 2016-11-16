import json
from openpyxl import Workbook

from django.core.management.base import BaseCommand

from td.tracking.models import Language


class Command(BaseCommand):
    help = "Export custom languages information to an excel file."

    def handle(self, *args, **options):
        languages = Language.objects.all()
        file_name = "languages.xlsx"
        wb = Workbook()
        ws = wb.active

        ws.append([
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
            ws.append([
                l.id,
                l.code,
                l.iso_639_3,
                l.name,
                l.anglicized_name,
                ",".join(l.alt_name_all),
                l.get_direction_display(),
                l.country.code if l.country else "",
                l.wa_region.slug if l.wa_region else "",
                ",".join(l.cc_all),
                l.gateway_language.code if l.gateway_language else "",
                l.gateway_flag,
                l.native_speakers if l.native_speakers >= 0 else 0
            ])

        wb.save(file_name)

        self.stdout.write(self.style.NOTICE("Output is saved as " + file_name))
