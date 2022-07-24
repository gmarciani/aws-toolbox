import re

import boto3
import click

from aws_toolbox.commands.regions import get_regions
from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


@click.command(help="Delete Secrets.")
@click.option(
    "--region",
    required=True,
    help="Region name.",
)
@click.option(
    "--name",
    required=True,
    help="Regex pattern for Secret name.",
)
@click.option(
    "--dryrun/--no-dryrun", default=False, show_default=True, type=bool, help="Activate/Deactivate dryrun mode."
)
@click.pass_context
def list_secrets(ctx, region, name, dryrun):
    log.info(f"Listing Secrets with region pattern {region}, with name pattern {name}, dryrun {dryrun}")

    regions_to_target = get_regions(region_name_regex=region)

    secret_name_pattern = re.compile(name)

    for region in regions_to_target:
        log.info(f"Listing Secrets in region {region}, name pattern {name}")

        secretsmanager_client = boto3.client("secretsmanager", region_name=region)
        secrets = secretsmanager_client.list_secrets()["SecretList"]

        secrets_filter = lambda secret: re.match(secret_name_pattern, secret.get("Name", None))
        secrets_to_list = list(filter(secrets_filter, secrets))

        if len(secrets_to_list) == 0:
            log.info(f"No Secrets to list in region {region}")
            continue

        if dryrun:
            log.info(
                f"The following secrets would have been listed in region {region}, but dryrun mode is enabled: {', '.join(map(lambda s: s.get('Name', None), secrets_to_list))}"
            )
            continue

        for secret_to_list in secrets_to_list:
            secret_name_name = secret_to_list.get("Name", None)
            creation_date = secret_to_list.get("CreatedDate", None)
            last_access_date = secret_to_list.get("LastAccessedDate", None)
            log.info(
                f"Existing Secret {secret_name_name} in region {region}, created on {creation_date} and last accessed on {last_access_date}"
            )
