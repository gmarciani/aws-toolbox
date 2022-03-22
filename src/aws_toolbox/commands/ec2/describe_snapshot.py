import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


@click.command(help="Describe Snapshots.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--description",
    required=True,
    help="Regex pattern for Snapshot description.",
)
@click.option(
    "--owners",
    required=True,
    help="Comma separated list of owners.",
)
@click.pass_context
def describe_snapshot(ctx, region, description, owners):
    log.info(f"Describing Snapshots with region pattern {region}, description pattern {description}, owners {owners}")

    regions_to_target = get_regions(region_name_regex=region)

    snapshot_description_pattern = re.compile(description)

    owners = owners.split(",")

    for region in regions_to_target:
        log.info(f"Describing Snapshots in region {region}, description pattern {description}, owners {owners}")

        ec2_client = boto3.client("ec2", region_name=region)
        snapshots = ec2_client.describe_snapshots(OwnerIds=owners)

        snapshots_to_describe = list(
            filter(
                lambda snapshot: re.match(snapshot_description_pattern, snapshot["Description"]), snapshots["Snapshots"]
            )
        )

        log.info(f"{region}: found {len(snapshots_to_describe)} Snapshots")
