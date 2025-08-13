import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils, time


log = logutils.get_logger(__name__)


@click.command(help="Delete roles.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--name",
    required=True,
    help="Regex pattern for role name.",
)
@click.option(
    "--before",
    required=True,
    help="Date time string, e.g. 2022-03-21T13:34:12.000Z",
)
@click.option(
    "--dryrun/--no-dryrun",
    default=False,
    show_default=True,
    type=bool,
    help="Activate/Deactivate dryrun mode.",
)
@click.pass_context
def delete_roles(ctx, region, name, before, dryrun):
    log.info(f"Deleting roles with region pattern {region}, name pattern {name}, before {before}, dryrun {dryrun}")

    regions_to_target = get_regions(region_name_regex=region)

    resource_name_pattern = re.compile(name)

    creation_date_limit = time.parse(before)

    for region in regions_to_target:
        log.info(f"Deleting roles in region {region}, name pattern {name}, creation date limit {creation_date_limit}")

        client = boto3.client("iam", region_name=region)
        paginator = client.get_paginator("list_roles")
        resources = []
        for page in paginator.paginate():
            resources.extend(page.get("Roles", []))

        resources_filter = (
            lambda role: re.match(resource_name_pattern, role["RoleName"]) and role["CreateDate"] <= creation_date_limit
        )
        resources_to_delete = list(filter(resources_filter, resources))

        n_resources_to_delete = len(resources_to_delete)
        log.info(f"Found {n_resources_to_delete} roles to delete in region {region}")

        if n_resources_to_delete == 0:
            continue

        for resource_to_delete in resources_to_delete:
            resource_name = resource_to_delete["RoleName"]
            resource_creation_time = resource_to_delete["CreateDate"]

            resource_description = (
                f"Role {resource_name} in region {region} with creation time {resource_creation_time}"
            )

            if dryrun:
                log.info(f"[DRYRUN] {resource_description} would be deleted")
                continue

            log.info(f"Deleting {resource_description}")

            try:
                # Detach managed policies
                attached_policies = client.list_attached_role_policies(RoleName=resource_name)["AttachedPolicies"]
                for policy in attached_policies:
                    client.detach_role_policy(RoleName=resource_name, PolicyArn=policy["PolicyArn"])

                # Delete inline policies
                inline_policies = client.list_role_policies(RoleName=resource_name)["PolicyNames"]
                for policy_name in inline_policies:
                    client.delete_role_policy(RoleName=resource_name, PolicyName=policy_name)

                client.delete_role(RoleName=resource_name)
            except Exception as e:
                log.error(f"Cannot delete role {resource_name}: {e}")
