#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""REST APIs. version 1.x
"""
import os.path

import anyconfig
import flask
import werkzeug.utils

from .globals import API_PREFIX
from . import utils
from ..lib import finder


API = flask.Blueprint("api", __name__, url_prefix=API_PREFIX)


def _get_graph(filename):
    """
    Download a YAML graph data.

    :param filename: graph (YAML) data filename
    """
    filename = werkzeug.utils.secure_filename(filename)
    return flask.send_from_directory(utils.uploaddir(), filename)


def _upload_graph(filename):
    """
    Upload a YAML graph data.

    :param filename: graph (YAML) data filename
    """
    payload = flask.request.get_data()
    try:
        yml_data = anyconfig.loads(payload.decode("utf-8"), ac_parser="yaml")
        anyconfig.dump(yml_data, utils.upload_filepath(filename))
        utils.generate_node_link_data_from_graph_data(filename)
    except (IOError, OSError, ValueError, RuntimeError):
        flask.abort(400, dict(code="Invalid data",
                              message="Uploaded data was invalid "
                                      "or something goes wrong."))

    resp = flask.jsonify(yml_data)
    resp.headers["Location"] = "/api/v1/graph/<path:filename>"

    return resp, 201


def _load_graph_by_filename(filename):
    """
    Load graph (YAML) data found by given filename.
    """
    filepath = utils.upload_filepath(filename)
    return finder.load(filepath, ac_parser="yaml")


@API.route("/graph/<path:filename>", methods=["GET", "POST"])
def get_or_upload_graph(filename):
    """
    Get or upload a YAML graph data.

    :param filename: graph (YAML) data filename
    """
    if flask.request.method == "POST":
        return _upload_graph(filename)

    return _get_graph(filename)


@API.route("/node_link/<path:filename>", methods=['GET'])
def get_node_link(filename):
    """
    Return a JSON node link data converted from YAML graph data.

    :param filename: graph (YAML) data filename
    """
    filename = utils.processed_filename(filename)
    return flask.send_from_directory(utils.uploaddir(), filename)


@API.route("/networks/by_addr/<path:filename>/<string:ip>", methods=['GET'])
def find_networks_by_addr(filename, ip):
    """
    Return a list of JSON objects represents nodes.

    :param ip: IP address
    """
    graph = _load_graph_by_filename(filename)
    res = finder.find_networks_or_ipsets_by_addr(graph, ip)

    return flask.jsonify(res)


@API.route("/node_link_paths/<path:filename>/<string:src_ip>/<string:dst_ip>",
           methods=['GET'])
def find_node_link_paths(filename, src_ip, dst_ip):
    """
    Return a list of nodes in the found link paths.

    :param filename: graph (YAML) data filename
    """
    paths = utils.find_paths_from_graph(filename, src_ip, dst_ip)
    return flask.jsonify(paths)


@API.route("/config/<string:ctype>/<path:filename>", methods=["GET"])
def get_config(ctype, filename):
    """
    Get config parsed.

    :param filename: Parsed configuration file
    """
    if not utils.is_valid_config_type(ctype):
        flask.abort(400, dict(code="Invalid Configuration type",
                              message="Given configuration type "
                                      "was invalid"))

    filepath = utils.processed_filepath(filename, ctype)
    udir = os.path.dirname(filepath)

    return flask.send_from_directory(udir, filename)

# vim:sw=4:ts=4:et:
