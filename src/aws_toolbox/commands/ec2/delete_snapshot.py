import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


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

    regions_to_target = get_regions(region_name_regex=region)

    snapshot_description_pattern = re.compile(description)

    owners = owners.split(",")

    for region in regions_to_target:
        log.info(f"Deleting Snapshots in region {region}, description pattern {description}, owners {owners}")

        ec2_client = boto3.client("ec2", region_name=region)
        snapshots = ec2_client.describe_snapshots(OwnerIds=owners)

        snapshots_to_delete = list(
            filter(
                lambda snapshot: re.match(snapshot_description_pattern, snapshot["Description"]), snapshots["Snapshots"]
            )
        )

        n_snapshots_to_delete = len(snapshots_to_delete)
        log.info(f"Found {n_snapshots_to_delete} snapshots to delete in region {region}")

        if n_snapshots_to_delete == 0:
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
