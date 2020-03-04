#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Utility functions
"""
import functools
import glob
import os.path
import os

import flask
import werkzeug.utils

from ..lib import finder, configparsers, utils
from ..globals import NODE_ANY, CONFIG_TYPES


def uploaddir():
    """
    :return: absolute path to the upload dir
    """
    return os.getenv("NOF_UPLOADDIR",
                     flask.current_app.config["UPLOADED_FILES_DEST"])


def list_filenames(pattern=None):
    """
    :param pattern: Filename pattern [*.yml]
    :return: A list of graph (YAML) data files.
    """
    if pattern is None:
        pattern = "*.yml"

    files = glob.glob(os.path.join(uploaddir(), pattern))
    return sorted(os.path.basename(f) for f in files)


def upload_filepath(filename, subdir=None):
    """
    :param filename: Uploaded file path
    :param subdir: Sub dir to save file
    """
    filename = werkzeug.utils.secure_filename(filename)

    if subdir is None:
        return os.path.join(uploaddir(), filename)

    return os.path.join(uploaddir(), subdir, filename)


@functools.lru_cache(maxsize=None)
def processed_filename(filename, prefix=None):
    """
    :param filename: Processed file path
    """
    if prefix is None:
        prefix = ''

    basename = os.path.splitext(werkzeug.utils.secure_filename(filename))[0]
    return "{}{}.json".format(prefix, basename)


def processed_filepath(filename, prefix=None):
    """
    :param filename: Processed file path
    """
    return os.path.join(uploaddir(), processed_filename(filename, prefix))


def generate_node_link_data_from_graph_data(filename):
    """
    :param filename: Original YAML file name
    """
    filepath = upload_filepath(filename)
    outpath = processed_filepath(filename)
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
    filepath = upload_filepath(filename)
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


def parse_config_and_dump_json_file(filename, ctype=None):
    """
    Parse fortios 'show full-configuration' output and dump parsed results as
    JSON file.
    """
    if ctype is None:
        ctype = CONFIG_TYPES[0]  # default

    filepath = upload_filepath(filename, ctype)
    utils.ensure_dir_exists(filepath)

    parse_fn = configparsers.PARSERS[ctype]
    outpath = processed_filepath(filename, prefix=ctype + '_')
    utils.ensure_dir_exists(outpath)

    return parse_fn(filepath, outpath)

# vim:sw=4:ts=4:et:
