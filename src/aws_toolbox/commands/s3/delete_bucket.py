import re
import time

import boto3
import click
from botocore.exceptions import ClientError

from aws_toolbox.utils import logutils

log = logutils.get_logger(__name__)


@click.command(help="Delete Buckets.")
@click.option(
    "--name",
    required=True,
    help="Regex pattern for Bucket name.",
)
@click.option(
    "--dryrun/--no-dryrun", default=False, show_default=True, type=bool, help="Activate/Deactivate dryrun mode."
)
@click.pass_context
def delete_bucket(ctx, name, dryrun):
    log.info(f"Deleting Buckets with name pattern {name}, dryrun {dryrun}")

    bucket_name_pattern = re.compile(name)

    s3_client = boto3.client("s3")
    buckets = s3_client.list_buckets()

    buckets_filter = lambda bucket: re.match(bucket_name_pattern, bucket["Name"])
    buckets_to_delete = list(filter(buckets_filter, buckets["Buckets"]))

    if len(buckets_to_delete) == 0:
        log.info(f"No Bucket to delete")
        return

    if dryrun:
        log.info(
            f"The following {len(buckets_to_delete)} buckets would be deleted, but dryrun mode is enabled and nothing will be done: {', '.join(map(lambda b: b['Name'], buckets_to_delete))}"
        )
        return

    for bucket_to_delete in buckets_to_delete:
        bucket_name = bucket_to_delete["Name"]
        creation_date = bucket_to_delete["CreationDate"]
        log.info(f"Emptying Bucket {bucket_name} with creation date {creation_date}")

        try:
            object_versions = s3_client.list_object_versions(Bucket=bucket_name).get("Versions", [])
            objects_to_delete = [{"Key": obj["Key"], "VersionId": obj["VersionId"]} for obj in object_versions]
            if objects_to_delete:
                s3_client.delete_objects(Bucket=bucket_name, Delete={"Objects": objects_to_delete, "Quiet": False})
        except Exception as e:
            log.error(f"Cannot empty Bucket {bucket_name}: {e}")

        log.info(f"Deleting Bucket {bucket_name} with creation date {creation_date}")

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                s3_client.delete_bucket(Bucket=bucket_name)
                log.info(f"Bucket {bucket_name} deleted")
            except ClientError as e:
                if e.response["Error"]["Code"] == "BucketNotEmpty":
                    log.error(f"Cannot delete Bucket {bucket_name} (attempt {attempt}/{max_attempts}): {e}")
                    time.sleep(1)
            except Exception as e:
                log.error(f"Cannot delete Bucket {bucket_name} (attempt {attempt}/{max_attempts}): {e}")
                break
