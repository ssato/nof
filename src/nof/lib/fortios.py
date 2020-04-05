#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Parse fortios configuration

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import collections.abc
import ipaddress
import itertools
import logging
import os.path
import re

import anyconfig

from .utils import ensure_dir_exists


CNF_GRPS = dict(firewall=("vdom", "system interface",
                          "firewall service category",
                          "firewall service group",
                          "firewall service custom",
                          "firewall addrgrp",
                          "firewall address",
                          "firewall policy"),
                log="log *",
                report="report *",
                router="router *",
                system="system *",
                user="user *")

LOG = logging.getLogger(__name__)

NET_MAX_PREFIX = 24


def make_group_configs(cnfs, group=None):
    """
    :param cnfs: {"configs": [<a mapping object holds configurations>]}
    :param group: Group name of configurations

    :return: Re-structured mapping object having sub group configurations
    :raises: IOError, OSError, TypeError, AttributeError
    """
    fwcs = dict()
    cnf_names = CNF_GRPS.get(group, [])  # (name_0, ..) or glob pattern

    if cnf_names:
        fwcs = dict((c["config"].lower(), c) for c in cnfs.get("configs", [])
                    if (c.get("config", '').startswith(cnf_names.replace('*',
                                                                         ''))
                        if '*' in cnf_names else c.get("config") in cnf_names))
    return fwcs


def list_configs_from_config_data(cnf, filepath=None):
    """
    :param cnf: Config data loaded or parsed log.
    :raises: ValueError, TypeError
    """
    if not cnf:
        raise ValueError("No expected data was found in {}".format(filepath))

    if not isinstance(cnf, collections.abc.Mapping):
        raise TypeError("Invalid typed data was found in {}".format(filepath))

    if "configs" not in cnf:
        raise ValueError("Configs were not found in {}".format(filepath))

    return cnf["configs"]


def resolve_config_name(cnfs, name):
    """
    :param cnfs: A list of fortios config objects
    :param name: Name of the configuration

    :return: A list of strings represent configs
    """
    found = [c["config"] for c in cnfs if re.match(name, c.get("config", ""))]

    if found:
        return found

    return []


def config_by_name(fwcnfs, name, regexp=False, only_first=True):
    """
    .. note::
       Even if there are more than one matched results were found, it returns
       the first one only.

    :param fwcnfs: A list of fortios config objects
    :param name: Name of the configuration
    :param regexp: Use regular expression in name
    :param only_first: Return the first item in the result only

    :return: A list of config edits or None
    """
    if regexp:
        res = [c for c in fwcnfs if re.match(name, c.get("config", ""))]
    else:
        res = [c for c in fwcnfs if c.get("config") == name]

    if res:
        # It should have an item only in most cases.
        return res[0] if only_first else res

    return None


def edits_by_name(fwcnfs, name, regexp=False):
    """
    :param fwcnfs: A list of fortios config objects
    :param name: Name of the configuration has edits
    :param regexp: Use regular expression in name

    :return: A list of config edits or None
    """
    cnf = config_by_name(fwcnfs, name, regexp=regexp)
    if cnf:
        return cnf.get("edits", None)

    return None


def hostname_from_configs(fwcnfs):
    """
    Detect hostname of the fortigate node from its '[system ]global'
    configuration.

    :param fwcnfs: A list of fortios config objects
    :raises:
        ValueError if given data does not contain global configuration to find
        hostname
    :return: hostname str or None (if hostname was not found)
    """
    gcnf = config_by_name(fwcnfs, ".*global", regexp=True)

    if not gcnf:  # I assume that it shsould not happen.
        raise ValueError("No global configs were found. Is it correct data?")

    return gcnf.get("hostname", '').lower() or None


def parse_show_config(filepath):
    """
    Parse 'show full-configuration output and returns a list of parsed configs.

    :param filepath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs

    :return:
        A list of configs (mapping objects) or [] (no data or something went
        wrong)
    :raises: IOError, OSError
    """
    for enc in ("utf-8", "shift-jis"):
        try:
            with open(filepath, encoding=enc) as inp:
                return anyconfig.load(inp, ac_parser="fortios")
        except UnicodeDecodeError:
            pass  # Try the next encoding...

    return None


def group_config_path(filepath, group):
    """
    Compute the path of the group config file.

    :param filepath: (JSON) file path contains parsed results
    """
    return os.path.join(os.path.dirname(filepath), group + ".json")


def parse_show_config_and_dump(inpath, outpath):
    """
    Similiar to the above :func:`parse_show_config` but save results as JSON
    file (path: `outpath`).

    :param inpath:
        a str or :class:`pathlib.Path` object represents file path contains
        'show full-configuration` or any other 'show ...' outputs
    :param outpath: (JSON) file path to save parsed results

    :return: A mapping object contains parsed results
    :raises: IOError, OSError
    """
    data = parse_show_config(inpath)

    ensure_dir_exists(outpath)
    anyconfig.dump(data, outpath)

    for grp in CNF_GRPS:
        g_outpath = group_config_path(outpath, grp)
        ensure_dir_exists(g_outpath)

        g_cnfs = make_group_configs(data, grp)
        if g_cnfs:
            anyconfig.dump(g_cnfs, g_outpath)

    return data


def assert_group(group):
    """
    :param group: Group name of configurations
    :raises: ValueError
    """
    if group not in CNF_GRPS:
        raise ValueError("Given {} is not valid group. Try other one from"
                         " {}".format(group, ", ".join(CNF_GRPS.keys())))
    return True


def load_configs(filepath, group=None):
    """
    :param filepath: (JSON) file path contains parsed results
    :raises: ValueError, TypeError
    """
    if group is not None:
        assert_group(group)
        filepath = group_config_path(filepath, group)

    try:
        cnf = anyconfig.load(filepath)
        return list_configs_from_config_data(cnf, filepath)

    except (IOError, OSError, ValueError) as exc:
        raise ValueError("{!r}: Something goes wrong with {}. "
                         "Ignore it.".format(exc, filepath))


def network_prefix(net_addr):
    """
    :param net_addr: IPv*Network object

    >>> net = ipaddress.ip_network("192.168.122.0/24")
    >>> network_prefix(net)
    24
    """
    return int(net_addr.compressed.split('/')[-1])


def summarize_networks(*net_addrs, prefix=None):
    """
    Degenerate and summarize given network addresses. For example,

    >>> net1 = ipaddress.ip_network("192.168.122.0/25")
    >>> net2 = ipaddress.ip_network("192.168.122.128/25")
    >>> net3 = ipaddress.ip_network("10.1.0.0/16")
    >>> summarize_networks(net1, net2)
    IPv4Network('192.168.122.0/24')
    >>> summarize_networks(net1, net2, mask=16)
    IPv4Network('192.168.0.0/16')
    >>> summarize_networks(net1, net3)
    >>> summarize_networks(net1, net3, prefix=1)
    """
    if prefix is None:
        prefix_len = min(network_prefix(n) for n in net_addrs)

        # try to find the smallest network.
        for diff in range(prefix_len):
            cnet = net_addrs[0].supernet(prefixlen_diff=diff)
            if all(n.supernet(prefixlen_diff=diff) == cnet for n in net_addrs):
                return cnet
    else:
        cnet = net_addrs[0].supernet(new_prefix=prefix)
        if all(n.supernet(new_prefix=prefix) == cnet for n in net_addrs):
            return cnet

    return None


def interface_ip_addrs_from_configs(fwcnfs):
    """
    :param fwcnfs: A list of fortios config objects
    :return: A list of interface IP addresses (IPv*Address objects)
    """
    for iface in edits_by_name(fwcnfs, "system interface"):
        if "ip" not in iface:
            continue  # IP address is not assigned to this interface.

        ip_netmask = iface["ip"]
        try:
            # Which is better? ipaddress.ip_address can validate the ip but ...
            # ipaddress.ip_interface("{}/{}".format(*ip_netmask))
            yield ipaddress.ip_address(ip_netmask[0])
        except ValueError:  # Invalid IP address, etc.
            LOG.warning("Found invalid IP address/mask: %s/%s", *ip_netmask)


def firewall_networks_from_configs(fwcnfs, max_prefix=NET_MAX_PREFIX):
    """
    :param fwcnfs: A list of fortios config objects
    :param max_prefix: Max prefix for networks

    :return: A list of network addresses (IPv*Network objects)
    """
    for edit in edits_by_name(fwcnfs, "firewall address"):
        if "subnet" not in edit:
            continue  # It is not subnet and may be iprange, etc.

        subnet = edit["subnet"]  # (network_or_host_ip_addr, netmask)
        try:
            maybe_net = ipaddress.ip_network("{}/{}".format(*subnet))
            if maybe_net.num_addresses > 1:  # It's network.
                # Replace it with its supernet (larger network segment).
                if network_prefix(maybe_net) > max_prefix:
                    maybe_net = maybe_net.supernet(new_prefix=max_prefix)

                yield maybe_net
        except ValueError:  # Invalid IP address, etc.
            LOG.warning("Found invalid address/mask: %s/%s", *subnet)


def parse_config_files(config_files, max_prefix=NET_MAX_PREFIX):
    """
    Load network related data from parsed fortigate config files.

    :param config_files: A list of fortios' config files parsed
    :param max_prefix: Max prefix for networks
    """
    cntr = itertools.count()
    net_seen = set()      # {IP*Network}
    net_id_seen = dict()  # {IP*Network: int}

    for cpath in config_files:
        try:
            fwcnfs = load_configs(cpath)
        except (ValueError, TypeError) as exc:
            LOG.warning(str(exc))
            continue

        node_id = next(cntr)

        try:
            name = hostname_from_configs(fwcnfs)
        except ValueError as exc:
            LOG.warning("%r: %s", exc, cpath)
            continue

        # interfaces
        addrs = list(interface_ip_addrs_from_configs(fwcnfs))
        if addrs:
            # firewall node
            yield dict(id=node_id, name=name, type="firewall",
                       addrs=[str(a) for a in addrs])

        # firewall address
        for net in firewall_networks_from_configs(fwcnfs, max_prefix):
            # network nodes
            if net in net_seen:
                net_id = net_id_seen[net]
            else:
                net_id = next(cntr)

                net_seen.add(net)
                net_id_seen[net] = net_id

                yield dict(id=net_id, name=str(net), type="network",
                           addrs=[str(net)])

            # firewall <-> network link
            yield [node_id, net_id]


def make_networks_from_config_files(config_files, max_prefix=NET_MAX_PREFIX):
    """
    Load network related data from parsed fortigate config files.

    :param config_files: A list of fortios' config files parsed
    :param max_prefix: Max prefix for networks

    :return: A mapping object, {nodes: [node], edges: [edge]}
    """
    nodes_and_edges = list(parse_config_files(config_files, max_prefix))
    nodes = [x for x in nodes_and_edges
             if isinstance(x, collections.abc.Mapping)]
    edges = [x for x in nodes_and_edges
             if isinstance(x, collections.abc.Sequence)]

    return dict(nodes=nodes, edges=edges)


def dump_networks_from_config_files(config_files, output=None,
                                    max_prefix=NET_MAX_PREFIX):
    """
    Load network related data from parsed fortigate config files.

    :param config_files: A list of fortios' config files parsed
    :param output: Output file path
    :param max_prefix: Max prefix for networks
    """
    nodes_links = make_networks_from_config_files(config_files,
                                                  max_prefix=max_prefix)

    if output is None:
        output = os.path.join(os.path.dirname(config_files[0]), "output.yml")

    anyconfig.dump(nodes_links, output)

# vim:sw=4:ts=4:et:
