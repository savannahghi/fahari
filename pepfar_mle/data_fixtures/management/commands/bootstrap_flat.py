import glob
import os

from django.core.management import BaseCommand

from .bootstrap_flat import process_json
from .common import process_json_files


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument("data_file", nargs="+", type=str)
        parser.add_argument(
            "--strict_mode", nargs="?", type=bool, const=True, default=False
        )

    def handle(self, *args, **options):
        strict_mode = options["strict_mode"]
        for suggestion in options["data_file"]:
            if os.path.exists(suggestion) and os.path.isfile(suggestion):
                process_json_files([suggestion], process_json, strict_mode=strict_mode)
            else:
                process_json_files(
                    sorted(glob.glob(suggestion)), process_json, strict_mode=strict_mode
                )

        self.stdout.write("Done loading")
