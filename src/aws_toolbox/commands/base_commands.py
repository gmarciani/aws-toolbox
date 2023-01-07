import re

from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


def match_resources(resources: list, conditions: dict):
    log.info(f"Matching the following resources with conditions {conditions}: {resources}")
    return list(
        filter(
            lambda resource: all(re.match(regex, resource.get(field, None)) for field, regex in conditions.items()),
            resources,
        )
    )
