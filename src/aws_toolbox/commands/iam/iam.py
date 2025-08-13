import click

from aws_toolbox.commands.iam.delete_roles import delete_roles


@click.group(help="IAM commands")
@click.pass_context
def iam(ctx):
    pass


# Stacks
iam.add_command(delete_roles)
