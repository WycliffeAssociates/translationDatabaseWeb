import json
from openpyxl import Workbook

from django.core.management.base import BaseCommand

from td.tracking.models import Charter, Event


class Command(BaseCommand):
    help = "Export custom event information with for reporting"

    def handle(self, *args, **options):

        file_name = "events.xlsx"
        wb = Workbook()
        ws = wb.active

        # Write headers
        ws.append([
            "id",
            "charter__language__code",
            "charter__language__name",
            "charter__language__anglicized_name",
            "location",
            "start_date",
            "end date",
            "lead dept",
            "partner",
            "contact person",
            "current_check_level",
            "target_check_level",
            "comment",
            "created at",
            "created by",
            "modified at",
            "modified by"
        ])

        # Write entries
        for e in Event.objects.all():
            ws.append([
                e.id,
                e.charter.language.lc,
                e.charter.language.ln,
                e.charter.language.ang,
                e.location,
                e.start_date,
                e.end_date,
                str(e.lead_dept),
                str(e.partner),
                e.contact_person,
                e.current_check_level,
                e.target_check_level,
                e.comment,
                e.created_at,
                e.created_by,
                e.modified_at,
                e.modified_by,
            ])

        wb.save(file_name)

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
