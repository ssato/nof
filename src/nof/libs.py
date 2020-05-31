#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
"""Libs to wrap external library functions.
"""
import os.path

import anyconfig
import flask
import fortios_xutils

from . import utils
from .globals import FT_NETWORKS, FT_FORTI_SHOW_CONFIG


FORTI_FILENAMES = (
    FORTI_CNF_ALL,
    FORTI_CNF_META,
    FORTI_FIREWALL_POLICIES
) = (
    # .. seealso:: `fortios_xutils.parser`
    "all.json",
    "metadata.json",

    # .. seealso:: `fortios_xutils.firewall`
    # "firewall_policy_table.data.pickle.gz"
    "firewall_policy_table.json"
)


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


def parse_fortigate_config_and_save_files(filepath):
    """
    Parse fortigate's "show *configuration" output and save its result as a
    series of JSON and database files under `datadir`.

    :param filepath:
       Path to the fortigate's "show *configuration" output uploaded

    :return: (hostname, a_mapping_object_holding_configs)
    :raises: ValueError
    """
    odir = os.path.dirname(filepath)

    # FIXME: Quick and dirty hack.
    if "config system global" not in open(filepath).read():
        raise ValueError("Not a fortigate's show *configuration output? "
                         "{}".format(filepath))

    res = fortios_xutils.parse_and_save_show_configs([filepath], outdir=odir)

    # res: (path of all.json, a_mapping_object_holding_configs)
    if not res or not res[0][-1]:
        raise ValueError("Looks invalid data: {}".format(filepath))

    (apath, cnf) = res[0]

    fwp = fortios_xutils.make_and_save_firewall_policy_table(
        apath,
        os.path.join(os.path.dirname(apath), FORTI_FIREWALL_POLICIES)
    )
    if fwp.empty:
        raise ValueError("Failed to generate firewall policies database: "
                         "{}".format(filepath))

    hostname = os.path.basename(os.path.split(apath)[0])

    return (hostname, cnf)


def load_firewall_policy_table(hostname, datadir=None):
    """
    :param hostname: Hostname
    :param datadir: Path to the top dir for data files

    :return:
        A :class:`pandas.DataFrame` object gives firewall policy table data
    """
    udir = utils.uploaddir(FT_FORTI_SHOW_CONFIG, datadir=datadir)
    fpath = os.path.join(udir, hostname, FORTI_FIREWALL_POLICIES)

    return fortios_xutils.load_firewall_policy_table(fpath)


def search_firewall_policy_by_addr(tbl_rdf, ipa):
    """
    :param tbl_rdf: A :class:`pandas.DataFrame` object to search
    :param ipa: A str gives an ip address to find nodes

    :return: A list of mappping objects contains results
    """
    return fortios_xutils.search_firewall_policy_table_by_addr(ipa, tbl_rdf)

# vim:sw=4:ts=4:et:
