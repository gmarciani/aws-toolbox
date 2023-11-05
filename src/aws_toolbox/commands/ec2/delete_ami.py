import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils, time

log = logutils.get_logger(__name__)


@click.command(help="Delete AMIs.")
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
    "--dryrun/--no-dryrun", default=False, show_default=True, type=bool, help="Activate/Deactivate dryrun mode."
)
@click.pass_context
def delete_ami(ctx, region, name, owners, before, dryrun):
    log.info(
        f"Deleting AMIs with region pattern {region}, name pattern {name}, owners {owners}, before {before}, dryrun {dryrun}"
    )

    regions_to_target = get_regions(region_name_regex=region)

    ami_name_pattern = re.compile(name)

    owners = owners.split(",")

    filters = [{"Name": "is-public", "Values": ["false"]}]

    creation_date_limit = time.parse(before)

    for region in regions_to_target:
        log.info(
            f"Deleting AMIs in region {region}, name pattern {name}, owners {owners}, creation date limit {creation_date_limit}"
        )

        ec2_client = boto3.client("ec2", region_name=region)
        amis = ec2_client.describe_images(Owners=owners, Filters=filters, IncludeDeprecated=True)

        ami_filter = (
            lambda ami: re.match(ami_name_pattern, ami["Name"])
            and time.parse(ami["CreationDate"]) <= creation_date_limit
        )
        amis_to_delete = list(filter(ami_filter, amis["Images"]))

        n_amis_to_delete = len(amis_to_delete)
        log.info(f"Found {n_amis_to_delete} AMIs to delete in region {region}")

        if n_amis_to_delete == 0:
            continue

        for ami_to_delete in amis_to_delete:
            ami_id = ami_to_delete["ImageId"]
            ami_name = ami_to_delete["Name"]
            owner = ami_to_delete["OwnerId"]
            public = ami_to_delete["Public"]
            creation_date = ami_to_delete["CreationDate"]
            log.info(
                f"Deleting AMI {ami_id} {'public' if public else 'private'} owned by {owner} in region {region} with creation date {creation_date} ({ami_name})"
            )
            try:
                ec2_client.deregister_image(ImageId=ami_id, DryRun=dryrun)
            except Exception as e:
                log.error(f"Cannot delete AMI {ami_id} ({ami_name}): {e}")
