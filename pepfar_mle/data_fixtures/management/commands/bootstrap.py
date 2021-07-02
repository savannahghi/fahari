import glob
import os

from django.core.management import BaseCommand

from .bootstrap import process_json
from .common import process_json_files


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("data_file", nargs="+", type=str)

    def handle(self, *args, **options):
        for suggestion in options["data_file"]:
            if os.path.exists(suggestion) and os.path.isfile(suggestion):
                process_json_files([suggestion], process_json)
            else:
                process_json_files(sorted(glob.glob(suggestion)), process_json)

        self.stdout.write("Done loading")
