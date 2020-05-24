#
# -*- coding: utf-8 -*-
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""REST APIs for networks app. version 1.x
"""
import os.path

import anyconfig
import flask

from ..globals import FT_NETWORKS
from .. import libs, utils
from .common import API_PREFIX


API = flask.Blueprint("api", __name__, url_prefix=API_PREFIX)

# url paths :
UP_GET_PATH = "/<path:filename>"
BY_ADDR_PATH = os.path.join(UP_GET_PATH, "by_addr/<string:ipa>")
BY_PATH_PATH = os.path.join(UP_GET_PATH,
                            "by_path/<string:src_ip>/<string:dst_ip>")


def _get_networks(filename):
    """
    Download a networks JSON data file.

    :param filename: a str gives a name of the networks JSON data file
    """
    filename = utils.uploaded_filename(filename)
    ftype = FT_NETWORKS

    return flask.send_from_directory(utils.uploaddir(ftype), filename)


def _upload_networks(filename):
    """
    Upload a networks (nodes and links) data in JSON format.

    :param filename: a str gives a name of the networks JSON data file
    """
    url_prefix = UP_GET_PATH
    payload = flask.request.get_data()

    content = payload.decode("utf-8")
    ftype = FT_NETWORKS
    fpath = utils.uploaded_filepath(filename, ftype, content=content)
    try:
        utils.ensure_dir_exists(fpath)

        # It does not look work...
        # net_data = anyconfig.loads(content, ac_parser="json")
        # anyconfig.dump(net_data, fpath)
        open(fpath, 'wb').write(payload)
        net_data = anyconfig.load(fpath, ac_parser="json")

    except (IOError, OSError, ValueError, RuntimeError) as exc:
        flask.abort(400,
                    dict(code="Invalid data",
                         message="Uploaded data was invalid "
                                 "or something goes wrong. "
                                 "exc={!r} content="
                                 "{!r}".format(exc, content)))

    filename = utils.uploaded_filename(filename, content=content)

    resp = flask.jsonify(net_data)
    resp.headers["Location"] = os.path.join(url_prefix, filename)

    return resp, 201


@API.route(UP_GET_PATH, methods=["GET", "POST"])
def get_or_upload_networks(filename):
    """
    Get or upload a networks JSON data.

    :param filename: a str gives a name of the networks JSON data file
    """
    if flask.request.method == "POST":
        return _upload_networks(filename)

    return _get_networks(filename)


@API.route(BY_ADDR_PATH, methods=['GET'])
def find_networks_by_addr(filename, ipa):
    """
    Return a list of JSON objects represents nodes.

    :param filename: a str gives a name of the networks JSON data file
    :param ipa: a str gives an IP address
    """
    res = libs.find_networks_by_ipaddr(filename, ipa)
    return flask.jsonify(res)


@API.route(BY_PATH_PATH, methods=['GET'])
def find_networks_by_path(filename, src_ip, dst_ip, node_type=False):
    """
    Return a list of nodes in the found link paths.

    :param filename: a str gives a name of the networks JSON data file
    """
    # raise ValueError("filename='{}', src_ip={}, "
    #                  "dst_ip={}".format(filename, src_ip, dst_ip))
    paths = libs.find_network_paths(filename, src_ip, dst_ip,
                                    node_type=node_type)
    return flask.jsonify(paths)

# vim:sw=4:ts=4:et:
