import click

from aws_toolbox.commands.cloudformation.delete_stacks import delete_stacks


@click.group(help="CloudFormation commands")
@click.pass_context
def cloudformation(ctx):
    pass


# Stacks
cloudformation.add_command(delete_stacks)