#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Libs to wrap external library functions.
"""
import flask
import fortios_xutils

from . import utils
from .globals import FT_NETWORKS


def sendfile_from_upload_dir(filename, file_type, datadir=None):
    """
    Load and send file from upload dir.

    :param filename: The name of the file to send
    :param file_type: type of file uploaded
    :param datadir: Path to the top dir for data files
    """
    fname = utils.uploaded_filepath(filename, file_type)
    udir = utils.uploaddir(file_type, datadir=datadir)

    return flask.send_from_directory(udir, fname)


def load_networks(filename, datadir=None):
    """
    Load network graph data from network JSON or YAML file.

    :param filename: The name of the file contains network graph data
    :param datadir: Path to the top dir for data files
    """
    fpath = utils.uploaded_filepath(filename, FT_NETWORKS, datadir=datadir)

    return fortios_xutils.load_network_graph(fpath)


def find_networks_by_ipaddr(filename, ipa, datadir=None):
    """
    Load network graph data from network JSON or YAML file.

    :param filename: File name
    :param ipa: A str gives an ip address
    :param datadir: Path to the top dir for data files

    :return: [] or a list of network nodes sorted by its prefix
    """
    fpath = utils.uploaded_filepath(filename, FT_NETWORKS, datadir=datadir)

    return fortios_xutils.find_network_nodes_by_ip(fpath, ipa)


def find_network_paths(filename, src, dst, node_type=False, datadir=None):
    """
    Load network graph data from network JSON or YAML file.

    :param filename: File name
    :param src: A str gives a source ip address
    :param dst: A str gives a destination ip address
    :param node_type: Node type to filter results if given
    :param datadir: Path to the top dir for data files

    :return: An iterable object to yield nodes in the found paths
    """
    fpath = utils.uploaded_filepath(filename, FT_NETWORKS, datadir=datadir)
    opts = dict(node_type=node_type)

    return fortios_xutils.find_network_paths(fpath, src, dst, **opts)

# vim:sw=4:ts=4:et:
