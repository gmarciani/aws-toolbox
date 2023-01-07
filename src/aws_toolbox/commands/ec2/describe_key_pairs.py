import json
import re

import boto3
import click

from aws_toolbox.commands.base_commands import match_resources
from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


@click.command(help="Describe Key Pairs.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--name",
    required=True,
    help="Regex pattern for EC2 Key Pair name.",
)
@click.option(
    "--fields",
    required=False,
    default="KeyName,KeyType",
    show_default=True,
    type=str,
    help="Comma separated list of fields.",
)
@click.pass_context
def describe_key_pairs(ctx, region, name, fields):
    log.info(f"Describing EC2 KeyPairs with filters: region={region}, name={name}, fields={fields}")

    regions_to_target = get_regions(region_name_regex=region)

    conditions = {"KeyName": re.compile(str(name))}

    fields_to_show = fields.split(",")

    result = {region: [] for region in regions_to_target}

    for region in regions_to_target:
        log.info(
            f"Describing EC2 KeyPairs in region {region}, with conditions {','.join(['{}={}'.format(k,v) for k,v in conditions.items()])}"
        )

        client = boto3.client("ec2", region_name=region)
        describe_results = client.describe_key_pairs()

        resources_to_describe = match_resources(describe_results["KeyPairs"], conditions)

        log.info(f"{region}: found {len(resources_to_describe)} KeyPairs")

        for resource_to_describe in resources_to_describe:
            result[region].append({field: resource_to_describe.get(field, None) for field in fields_to_show})

    print(json.dumps(result, indent=4))
