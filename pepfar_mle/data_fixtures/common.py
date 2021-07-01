import logging
import os

try:
    import ujson as json
except ImportError:
    import json

from django.db import transaction
from six import string_types

LOGGER = logging.getLogger(__name__)


class DataAlreadyExistsException(Exception):
    pass


@transaction.atomic
def process_json_files(filenames, processor, *args, **kwargs):
    """The entry point - loops through data files and loads each in

    It takes an iterable of file names
    """
    assert isinstance(filenames, list)

    for filename in filenames:
        assert isinstance(filename, string_types)
        assert os.path.isfile(filename)

        LOGGER.info("processing {}".format(filename))
        with open(filename) as f:
            model_specs = json.load(f)
            assert isinstance(model_specs, list)
            try:
                processor(model_specs, *args, **kwargs)
            except Exception as ex:  # Broad catch to allow debug messages
                # The str() calls respond to some Python 3 weirdness
                LOGGER.debug("{} when processing {}".format(str(ex), str(filename)))
                raise  # Abort early on failure, sort the failure out
