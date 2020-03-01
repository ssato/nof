#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""REST APIs. version 1.x
"""
import flask

from .globals import API
from ..lib import fortios
from ..main import utils


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
    res = fortios.load_configs(filepath, group)

    return flask.jsonify(res)

# vim:sw=4:ts=4:et:
