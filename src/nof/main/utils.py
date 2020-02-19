#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
"""Utility functions
"""
import functools
import glob
import os.path
import os

import flask
import werkzeug.utils

from ..lib import finder
from ..globals import NODE_ANY


def uploaddir():
    """
    :return: absolute path to the upload dir
    """
    return os.getenv("NOF_UPLOADDIR",
                     flask.current_app.config["UPLOADED_FILES_DEST"])


def list_graph_filenames():
    """
    :return: A list of graph (YAML) data files.
    """
    files = glob.glob(os.path.join(uploaddir(), "*.yml"))
    return sorted(os.path.basename(f) for f in files)


def graph_path(filename):
    """
    :param filename: Original YAML file name
    """
    filename = werkzeug.utils.secure_filename(filename)
    return os.path.join(uploaddir(), filename)


@functools.lru_cache(maxsize=None)
def node_link_filename(filename):
    """
    :param filename: Original YAML file name
    """
    basename = os.path.splitext(werkzeug.utils.secure_filename(filename))[0]
    return "{}.json".format(basename)


def node_link_path(filename):
    """
    :param filename: Original YAML file name
    """
    return os.path.join(uploaddir(), node_link_filename(filename))


def generate_node_link_data_from_graph_data(filename):
    """
    :param filename: Original YAML file name
    """
    filepath = graph_path(filename)
    outpath = node_link_path(filename)
    msg = "filepath: {}, outpath: {}".format(filepath, outpath)

    try:
        graph = finder.load(filepath, ac_parser="yaml")
        finder.save_as_node_link(graph, outpath)
    except (IOError, OSError, RuntimeError):
        raise IOError(msg)

    except (ValueError, KeyError):
        raise ValueError(msg)


def _load_graph_by_filename(filename):
    """Load graph data by filename
    """
    filepath = graph_path(filename)
    return finder.load(filepath, ac_parser="yaml")


def find_networks_from_graph(filename, ip):
    """
    :param filename: Original YAML file name
    :param ip: A string represents an IP address

    :return: A list of networks
    :raises: ValueError if given `ip` is not an IP address string
    """
    graph = _load_graph_by_filename(filename)
    networks = finder.find_networks_by_addr(graph, ip)

    return networks


def find_paths_from_graph(filename, src_ip, dst_ip, node_type=None):
    """
    :param filename: Original YAML file name
    :param src_ip: A string represents source IP address
    :param dst_ip: A string represents destination IP address

    :return: A list of lists of nodes in the found paths
    :raises: ValueError if given src and/or dst is not an IP address string
    """
    if node_type is None:
        node_type = NODE_ANY

    graph = _load_graph_by_filename(filename)

    return finder.find_paths(graph, src_ip, dst_ip, node_type=node_type)

# vim:sw=4:ts=4:et:
