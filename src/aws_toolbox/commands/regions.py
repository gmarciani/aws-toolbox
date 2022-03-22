import re

import boto3


def get_regions(region_name_regex=None):
    region_name_pattern = re.compile(region_name_regex if region_name_regex is not None else ".*")
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    regions = ec2_client.describe_regions()

    return [
        region["RegionName"] for region in regions["Regions"] if re.match(region_name_pattern, region["RegionName"])
    ]
