import calendar
import codecs
import csv
import re

from datetime import datetime
from django.core.management.base import BaseCommand

from td.models import Country
from td.tracking.models import Charter, Event
from td.tracking.tasks import export_event_data


class Command(BaseCommand):
    help = "Export events information"

    def handle(self, *args, **options):
        file_name = "Events.csv"

        with open(file_name, "wb") as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file)

            writer.writerow([
                "charter",
                "event_name",
                "number",
                "location",
                "country",
                "start_date",
                "end_date",
                "lead_dept",
                "contact_person",
                "charter_partner",
                "partner",
                "lead_facilitator",
                "co_lead_facilitator",
                "comment",
                "current_check_level",
                "target_check_level",
            ])

            name_delimiter = re.compile(r'/|,\s')
            location_delimiter = re.compile(r',*\s')

            events = export_event_data()

            for event in events:
                # Only one person could be the contact person
                contact_name = name_delimiter.split(event.get("contact_person"))[0]
                full_name = contact_name if \
                    len(contact_name.split(" ")) > 1 else contact_name + " Unknown"

                # Try to find country from location
                locations = location_delimiter.split(event.get("location", ""))
                for location in locations:
                    location = location.title()
                    country = location if Country.objects.filter(name=location).exists() else ""

                # Construct event name
                time = datetime.strptime(event.get("start_date"), "%Y-%m-%d")
                event_name = " ".join([country or "Unknown", calendar.month_name[time.month], str(time.year)])

                # Identify lead and co-lead facilitators
                leads = [f.get("name") for f in event.get("facilitators") if f.get("is_lead", False)]
                lead_facilitator = leads[0] if len(leads) > 0 else ""
                co_lead_facilitator = leads[1] if len(leads) > 1 else ""

                print "processing event", event.get("name")

                writer.writerow([
                    event.get("charter", {}).get("name", ""),
                    event.get("name", "").encode("utf-8"),
                    event.get("number", ""),
                    event.get("location", "").encode("utf-8"),
                    country or "",
                    event.get("start_date"),
                    event.get("end_date"),
                    event.get("lead_dept").get("name", "").encode("utf-8"),
                    full_name,
                    event.get("charter_partner"),
                    event.get("partner", {}).get("name", "").encode("utf-8"),
                    lead_facilitator.encode("utf-8"),
                    co_lead_facilitator.encode("utf-8"),
                    event.get("comment", "").encode("utf-8"),
                    event.get("current_check_level", ""),
                    event.get("target_check_level", ""),
                ])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
