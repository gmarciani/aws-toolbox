import click

from aws_toolbox.commands.secretsmanager.delete_secrets import delete_secrets
from aws_toolbox.commands.secretsmanager.list_secrets import list_secrets


@click.group(help="Secrets Manager commands")
@click.pass_context
def secretsmanager(ctx):
    pass


secretsmanager.add_command(delete_secrets)
secretsmanager.add_command(list_secrets)
