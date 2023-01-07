import click

from aws_toolbox.commands.ec2.delete_ami import delete_ami
from aws_toolbox.commands.ec2.delete_snapshot import delete_snapshot
from aws_toolbox.commands.ec2.describe_amis import describe_amis
from aws_toolbox.commands.ec2.describe_key_pairs import describe_key_pairs
from aws_toolbox.commands.ec2.describe_snapshot import describe_snapshot


@click.group(help="EC2 commands")
@click.pass_context
def ec2(ctx):
    pass


# AMI
ec2.add_command(delete_ami)
ec2.add_command(describe_amis)

# Snapshots
ec2.add_command(delete_snapshot)
ec2.add_command(describe_snapshot)

# Key Pairs
ec2.add_command(describe_key_pairs)
