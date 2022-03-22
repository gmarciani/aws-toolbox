import click

from aws_toolbox.commands.s3.delete_bucket import delete_bucket


@click.group(help="S3 commands")
@click.pass_context
def s3(ctx):
    pass


# Buckets
s3.add_command(delete_bucket)
