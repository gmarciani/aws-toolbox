from datetime import datetime


DEFAULT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"
CLOUDFORMATION_STACK_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"


def parse(datetime_string: str, datetime_format: str = DEFAULT_FORMAT):
    return datetime.strptime(datetime_string, datetime_format)
