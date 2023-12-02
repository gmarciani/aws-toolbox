import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils, time
from aws_toolbox.utils.time import CLOUDFORMATION_STACK_FORMAT

log = logutils.get_logger(__name__)


@click.command(help="Delete Stacks.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--name",
    required=True,
    help="Regex pattern for Stack name.",
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
def delete_stacks(ctx, region, name, before, dryrun):
    log.info(
        f"Deleting Stacks with region pattern {region}, name pattern {name}, before {before}, dryrun {dryrun}"
    )

    regions_to_target = get_regions(region_name_regex=region)

    resource_name_pattern = re.compile(name)

    creation_date_limit = time.parse(before)

    for region in regions_to_target:
        log.info(
            f"Deleting Stacks in region {region}, name pattern {name}, creation date limit {creation_date_limit}"
        )

        client = boto3.client("cloudformation", region_name=region)
        resources = (client.list_stacks().get("StackSummaries", []) +
                     client.list_stacks(StackStatusFilter=["DELETE_FAILED"]).get("StackSummaries", []))

        resources_filter = (
            lambda stack: re.match(resource_name_pattern, stack["StackName"])
            and stack["StackStatus"] != "DELETE_COMPLETE"
            and time.parse(str(stack["CreationTime"]), CLOUDFORMATION_STACK_FORMAT) <= creation_date_limit
        )
        resources_to_delete = list(filter(resources_filter, resources))

        n_resources_to_delete = len(resources_to_delete)
        log.info(f"Found {n_resources_to_delete} Stacks to delete in region {region}")

        if n_resources_to_delete == 0:
            continue

        for resource_to_delete in resources_to_delete:
            resource_name = resource_to_delete["StackName"]
            resource_creation_time = resource_to_delete["CreationTime"]
            resource_status = resource_to_delete["StackStatus"]

            resources_to_retain = []
            if resource_status == "DELETE_FAILED":
                resources_to_retain = re.findall(r"\[(\w+)\]", resource_to_delete["StackStatusReason"])

            resource_description = f"Stack {resource_name} in region {region} with creation time {resource_creation_time}, status {resource_status} and resources to retain {resources_to_retain}"

            if dryrun:
                log.info(f"[DRYRUN] {resource_description} would be deleted")
                continue

            log.info(f"Deleting {resource_description}")

            try:
                client.delete_stack(StackName=resource_name, RetainResources=resources_to_retain)
            except Exception as e:
                log.error(f"Cannot delete Stack {resource_name}: {e}")
