#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""REST APIs. version 1.x
"""
import os.path
import flask

from ..lib import fortios
from ..main import utils
from .globals import API_PREFIX


API = flask.Blueprint("fortios_api", __name__, url_prefix=API_PREFIX)

_PREFIX = "fortios_"


@API.route("/<string:group>/<path:filename>", methods=["GET"])
def get_group_config_file(group, filename):
    """
    Get group configuration file

    :param group: Configuration group name, see ..lib.fortios.CONFIG_GROUPS
    :param filename: Original configuration filename uploaded
    """
    try:
        fortios.assert_group(group)
    except ValueError as exc:
        return flask.jsonify(dict(error=dict(type="InvalidGroup",
                                             message=str(exc)))), 400

    filepath = utils.processed_filepath(filename, prefix=_PREFIX)
    g_path = fortios.group_config_path(filepath, group)

    return flask.send_from_directory(os.path.dirname(g_path),
                                     os.path.basename(g_path))

# vim:sw=4:ts=4:et:
