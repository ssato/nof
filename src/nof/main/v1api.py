#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""REST APIs. version 1.x
"""
import anyconfig
import flask
import werkzeug.utils

from .globals import API
from . import utils
from ..lib import finder


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
        anyconfig.dump(yml_data, utils.graph_path(filename))
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
    filepath = utils.graph_path(filename)
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
    filename = utils.node_link_filename(filename)
    return flask.send_from_directory(utils.uploaddir(), filename)


@API.route("/networks/by_addr/<path:filename>/<string:ip>", methods=['GET'])
def find_networks_by_addr(filename, ip):
    """
    Return a list of JSON objects represents nodes.

    :param ip: IP address
    """
    graph = _load_graph_by_filename(filename)
    networks = finder.find_networks_by_addr(graph, ip)

    return flask.jsonify(networks)


@API.route("/node_link_paths/<path:filename>/<string:src_ip>/<string:dst_ip>",
           methods=['GET'])
def find_node_link_paths(filename, src_ip, dst_ip):
    """
    Return a list of nodes in the found link paths.

    :param filename: graph (YAML) data filename
    """
    paths = utils.find_paths_from_graph(filename, src_ip, dst_ip)
    return flask.jsonify(paths)

# vim:sw=4:ts=4:et:
