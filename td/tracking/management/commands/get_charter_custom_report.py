import json
from openpyxl import Workbook

from django.core.management.base import BaseCommand

from td.tracking.models import Charter


class Command(BaseCommand):
    help = "Export custom charter information with for reporting"

    def handle(self, *args, **options):

        file_name = "charters.xlsx"
        wb = Workbook()
        ws = wb.active

        # Write headers
        ws.append([
            "id",
            "code",
            "name",
            "english name",
            "first event's start date",
            "start_date",
            "end date",
            "new start",
            "lead dept",
            "partner",
            "contact person",
            "country",
            "wa region",
            "gateway flag",
            "direction",
            "alternate names",
            "created at",
            "created by",
            "modified at",
            "modified by"
        ])

        # Write entries
        for c in Charter.objects.all():
            first_event = c.event_set.first()
            ws.append([
                c.id,
                c.language.lc,
                c.language.ln,
                c.language.ang,
                first_event.start_date if first_event else "",
                c.start_date,
                c.end_date,
                c.new_start,
                str(c.lead_dept),
                str(c.partner),
                c.contact_person,
                str(c.language.country),
                str(c.language.wa_region),
                c.language.gateway_flag,
                c.language.direction,
                c.language.alt_names,
                c.created_at,
                c.created_by,
                c.modified_at,
                c.modified_by,
            ])

        wb.save(file_name)

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
