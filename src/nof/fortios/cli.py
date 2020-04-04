#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""fortios related custom CLI commands.
"""
import logging
import os.path
import os

import click
import flask.cli

from ..lib import fortios


# >= 1.1.x: https://flask.palletsprojects.com/en/1.1.x/cli/
# https://flask.palletsprojects.com/en/1.0.x/cli/#custom-commands
# CLI_ = flask.Blueprint("fortios_cli", __name__, cli_group="fortios")
CLI = flask.cli.AppGroup("fortios")

LOG = logging.getLogger(__name__)


@CLI.command("parse", with_appcontext=False)
@click.argument("config_path", type=click.Path(exists=True))
@click.argument("output", type=click.Path())
def parse(config_path, output):
    """
    Parse input (fortios 'show' or 'show full-configuration' outputs) and dump
    parsed results into output dir.

    :param input: Input file path
    :param output: Output file path
    """
    outdir = os.path.dirname(output)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    fortios.parse_show_config_and_dump(config_path, output)


@CLI.command("gen_network", with_appcontext=False)
@click.argument("config_files", type=click.Path(exists=True), nargs=-1)
@click.option("-p", "--prefix", type=int,
              help="Max network prefix to summarize")
@click.option("-o", "--output", type=click.Path())
def generate_network_yml(config_files, output=None,
                         prefix=fortios.NET_MAX_PREFIX):
    """
    Generate network YAML file to find paths later, from parsed fortigate
    config files.
    """
    fortios.make_and_save_network_graph_from_configs(config_files, output,
                                                     max_prefix=prefix)

# vim:sw=4:ts=4:et:
