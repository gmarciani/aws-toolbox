import click

from aws_toolbox.commands.ec2.delete_ami import delete_ami
from aws_toolbox.commands.ec2.delete_snapshot import delete_snapshot
from aws_toolbox.commands.ec2.describe_ami import describe_ami
from aws_toolbox.commands.ec2.describe_snapshot import describe_snapshot


@click.group(help="EC2 commands")
@click.pass_context
def ec2(ctx):
    pass


# AMI
ec2.add_command(delete_ami)
ec2.add_command(describe_ami)

# Snapshots
ec2.add_command(delete_snapshot)
ec2.add_command(describe_snapshot)
