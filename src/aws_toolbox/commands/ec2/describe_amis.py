import json
import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils, time

log = logutils.get_logger(__name__)


@click.command(help="Describe AMIs.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--name",
    required=True,
    help="Regex pattern for AMI name.",
)
@click.option(
    "--owners",
    required=True,
    help="Comma separated list of owners.",
)
@click.option(
    "--before",
    required=True,
    help="Date time string, e.g. 2022-03-21T13:34:12.000Z",
)
@click.option(
    "--fields",
    required=False,
    default="Name",
    show_default=True,
    type=str,
    help="Comma separated list of fields.",
)
@click.pass_context
def describe_amis(ctx, region, name, owners, before, fields):
    log.info(
        f"Describing AMIs with region pattern {region}, name pattern {name}, owners {owners}, before {before}, fields {fields}"
    )

    regions_to_target = get_regions(region_name_regex=region)

    ami_name_pattern = re.compile(name)

    owners = owners.split(",")

    filters = [{"Name": "is-public", "Values": ["false"]}]

    creation_date_limit = time.parse(before)

    fields_to_show = fields.split(",")

    result = {region: [] for region in regions_to_target}

    for region in regions_to_target:
        log.info(
            f"Describing AMIs in region {region}, name pattern {name}, owners {owners}, creation date limit {creation_date_limit}"
        )

        ec2_client = boto3.client("ec2", region_name=region)
        amis = ec2_client.describe_images(Owners=owners, Filters=filters, IncludeDeprecated=True)

        resource_filter = (
            lambda ami: re.match(ami_name_pattern, ami["Name"])
            and time.parse(ami["CreationDate"]) <= creation_date_limit
        )
        resources_to_describe = list(filter(resource_filter, amis["Images"]))

        log.info(f"{region}: found {len(resources_to_describe)} AMIs")

        for resource_to_describe in resources_to_describe:
            result[region].append({field: resource_to_describe.get(field, None) for field in fields_to_show})

        print(json.dumps(result, indent=4))
