#!/usr/bin/env python

import click

from aws_toolbox.commands.cloudformation import cloudformation
from aws_toolbox.commands.ec2 import ec2
from aws_toolbox.commands.s3 import s3
from aws_toolbox.commands.secretsmanager import secretsmanager
from aws_toolbox.config.metadata import NAME, VERSION
from aws_toolbox.utils import guiutils, logutils

log = logutils.get_logger(__name__)


@click.group(invoke_without_command=True, context_settings=dict(max_content_width=120))
@click.option("--debug/--no-debug", default=False, show_default=True, type=bool, help="Activate/Deactivate debug mode.")
@click.pass_context
@click.version_option(version=VERSION)
def main(ctx, debug):
    print(guiutils.get_splash(NAME))
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
    else:
        ctx.ensure_object(dict)
        ctx.obj["DEBUG"] = debug
        logutils.set_level("DEBUG" if debug else "INFO")


main.add_command(ec2.ec2)
main.add_command(s3.s3)
main.add_command(secretsmanager.secretsmanager)
main.add_command(cloudformation.cloudformation)


if __name__ == "__main__":
    main(obj={})
