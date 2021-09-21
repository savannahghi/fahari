from ..constants import IMAGE_TYPES


def unique_list(list_object):
    """Return a list that contains only unique items."""
    seen = set()
    new_list = []
    for each in list_object:
        if each in seen:
            continue
        new_list.append(each)
        seen.add(each)

    return new_list


def get_directory(instance, filename):
    """Determine the upload_to path for every model inheriting Attachment."""
    org = instance.organisation.organisation_name
    app = instance._meta.app_label  # noqa
    return "{}/{}/{}/{}".format(org, app, instance.__class__.__name__.lower(), filename)


def is_image_type(file_type):
    """Check if file is an image."""
    return file_type in IMAGE_TYPES
