import csv

from django.core.management.base import BaseCommand

from td.tracking.models import TranslationMethod


class Command(BaseCommand):
    help = "Export TranslationMethod information"

    def handle(self, *args, **options):
        file_name = "TranslationMethods.csv"

        with open(file_name, "wb") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["name"])

            for t in TranslationMethod.objects.all():
                if t.name.lower() != "other":
                    writer.writerow([t.name])

        self.stdout.write(self.style.SUCCESS("Output is saved as " + file_name))
