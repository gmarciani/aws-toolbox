import re
from datetime import datetime

import boto3
import click

from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


@click.group(help="EC2 commands")
@click.pass_context
def ec2(ctx):
    pass


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

    region_pattern = re.compile(region)

    ec2_client = boto3.client("ec2")
    regions = ec2_client.describe_regions()

    regions_to_target = [
        region["RegionName"] for region in regions["Regions"] if re.match(region_pattern, region["RegionName"])
    ]

    owners = owners.split(",")

    ami_name_pattern = re.compile(name)

    filters = [{"Name": "is-public", "Values": ["false"]}]

    creation_date_limit = datetime.strptime(before, "%Y-%m-%dT%H:%M:%S.%f%z")

    for region in regions_to_target:
        log.info(
            f"Deleting AMIs in region {region}, name pattern {name}, owners {owners}, creation date limit {creation_date_limit}"
        )

        ec2_client = boto3.client("ec2", region_name=region)
        amis = ec2_client.describe_images(Owners=owners, Filters=filters, IncludeDeprecated=True)

        ami_filter = (
            lambda ami: re.match(ami_name_pattern, ami["Name"])
            and datetime.strptime(ami["CreationDate"], "%Y-%m-%dT%H:%M:%S.%f%z") <= creation_date_limit
        )
        amis_to_delete = list(filter(ami_filter, amis["Images"]))

        if len(amis_to_delete) == 0:
            log.info(f"No AMI to delete in region {region}")
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


@click.command(help="Delete Snapshots.")
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
@click.option(
    "--dryrun/--no-dryrun", default=False, show_default=True, type=bool, help="Activate/Deactivate dryrun mode."
)
@click.pass_context
def delete_snapshot(ctx, region, description, owners, dryrun):
    log.info(
        f"Deleting Snapshots with region pattern {region}, description pattern {description}, owners {owners}, dryrun {dryrun}"
    )

    region_pattern = re.compile(region)

    ec2_client = boto3.client("ec2")
    regions = ec2_client.describe_regions()

    regions_to_target = [
        region["RegionName"] for region in regions["Regions"] if re.match(region_pattern, region["RegionName"])
    ]

    owners = owners.split(",")

    snapshot_description_pattern = re.compile(description)

    for region in regions_to_target:
        log.info(f"Deleting Snapshots in region {region}, description pattern {description}, owners {owners}")

        ec2_client = boto3.client("ec2", region_name=region)
        snapshots = ec2_client.describe_snapshots(OwnerIds=owners)

        snapshots_to_delete = list(
            filter(
                lambda snapshot: re.match(snapshot_description_pattern, snapshot["Description"]), snapshots["Snapshots"]
            )
        )

        if len(snapshots_to_delete) == 0:
            log.info(f"No Snapshot to delete in region {region}")
            continue

        for snapshot_to_delete in snapshots_to_delete:
            snapshot_id = snapshot_to_delete["SnapshotId"]
            snapshot_owner = snapshot_to_delete["OwnerId"]
            snapshot_description = snapshot_to_delete["Description"]
            log.info(
                f"Deleting Snapshot {snapshot_id} owned by {snapshot_owner} in region {region} ({snapshot_description})"
            )
            try:
                ec2_client.delete_snapshot(SnapshotId=snapshot_id, DryRun=dryrun)
            except Exception as e:
                log.error(f"Cannot delete Snapshot {snapshot_id}: {e}")


ec2.add_command(delete_ami)
ec2.add_command(delete_snapshot)
