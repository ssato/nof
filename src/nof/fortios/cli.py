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
@click.argument("inpaths", type=click.Path(exists=True), nargs=-1)
@click.option("-O", "--outdir", type=click.Path(), help="Output dir")
def parse(inpaths, outdir=None):
    """
    Parse inputs (fortios 'show' or 'show full-configuration' outputs) and dump
    parsed results under dir, `outdir`.

    :param inpaths: Input file paths
    :param outdir: Output directory
    """
    for ipath in inpaths:
        if not outdir:
            outdir = os.path.dirname(ipath)

        (bname, ext) = os.path.splitext(os.path.basename(ipath))
        if ext == ".json":
            LOG.warning("Input and output look same: %s, skip it", ipath)
            continue

        opath = os.path.join(outdir, bname + ".json")
        fortios.parse_show_config_and_dump(ipath, opath)


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
    fortios.dump_networks_from_config_files(config_files, output,
                                            max_prefix=prefix)

# vim:sw=4:ts=4:et:
