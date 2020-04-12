#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""REST APIs. version 1.x
"""
import os.path
import flask

from . import globals as G, utils


API = flask.Blueprint("fortios_api", __name__, url_prefix=G.API_PREFIX)


@API.route("/<string:hostname>", methods=["GET"])
def get_host_configs(hostname):
    """
    Get host's config filenames

    :param hostname: Hostname to get config file
    """
    return flask.jsonify(utils.list_host_configs(hostname))


@API.route("/", methods=["GET"])
def index():
    """
    Get hosts with group config filenames
    """
    hosts = [dict(hostname=h, filenames=utils.list_host_configs(h))
             for h in utils.list_hostnames()]

    return flask.jsonify(hosts)


@API.route("/<string:hostname>/<path:filename>", methods=["GET"])
def get_host_config(hostname, filename):
    """
    Get host's configuration file

    :param hostname: Hostname to get config file
    :param filename: Original configuration filename uploaded
    """
    filepath = utils.get_group_config_path(hostname, filename)
    (hdir, filename) = os.path.split(filepath)

    try:
        return flask.send_from_directory(hdir, filename)
    except ValueError as exc:
        return flask.jsonify(dict(error=dict(type="InvalidOrMissing",
                                             message=str(exc)))), 400

# vim:sw=4:ts=4:et:
