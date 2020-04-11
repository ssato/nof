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
import datetime
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

CNF_NAMES = (".*global",
             "system.*",
             "firewall service category",
             "firewall service group",
             "firewall service custom",
             "firewall addrgrp",
             "firewall address",
             "firewall policy")

METADATA_FILENAME = "metadata.json"

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


def configs_by_name_0(cnfs, name, regexp=False):
    """
    :param cnfs: A list of fortios config objects, [{"config": ...}]
    :param name: Name of the configuration
    :param regexp: Use regular expression in name

    :return: A list of config edits or [] (not found)
    """
    if regexp:
        res = [c for c in cnfs if re.match(name, c.get("config", ""))]
    else:
        res = [c for c in cnfs if c.get("config") == name]

    return res


def vdom_names_itr(cnfs):
    """
    :param cnfs: A list of fortios config objects, [{"config": ...}]
    :param list_names: List vdoms with names

    :return: True if vdoms are found in given configurations
    """
    for vcnf in configs_by_name_0(cnfs, "vdom"):
        if "edits" in vcnf:
            if all(e for e in vcnf["edits"] if "configs" not in e):
                for vdom in vcnf["edits"]:
                    yield vdom["edit"]  # It's the vdom name.


def has_vdom(cnfs):
    """
    :param cnfs: A list of fortios config objects, [{"config": ...}]
    :return: True if vdoms are found in given configurations
    """
    return bool(configs_by_name_0(cnfs, "vdom"))


def configs_by_name(fwcnfs, name, regexp=False, vdom=None):
    """
    Structure of fwcnfs:

    [{"config": "vdom",   # VDom list
      "edits": [
        {"edit": "root"},
        ...
      ]},
     {"config": "global",  # Global configurations
      "configs": [
        {"config": "system global", ... },
        ...
      ]},
     {"comments": [ ... ]},  # Comments
     {"config": "vdom",  # Configurations in each VDoms
      "edits": [         # especially 'root' vdom.
        {"edit": "root",
         "configs": [
            {"config": "system settings", ...},
            ...
        ]}
      ]}
    ]

    or

    [{"config": ...}]

    :param fwcnfs: A list of fortios config objects
    :param name: Name of the configuration
    :param regexp: Use regular expression in name
    :param vdom: vdom to search configurations from [root]

    :return: A list of configs or []
    """
    # Handle some special cases first.
    if name in ("vdom", "global"):
        return configs_by_name_0(fwcnfs, name, regexp=False)

    if not has_vdom(fwcnfs):
        return configs_by_name_0(fwcnfs, name, regexp=regexp)

    # Items other than "vdom" need search from the children.
    gcnfs = configs_by_name_0(fwcnfs, "global", regexp=False)
    if gcnfs:
        gcnfs = gcnfs[0].get("configs", [])  # len(gcnfs) should be 1

    # exclude config contains vdom list
    vcnfs = [c for c in configs_by_name_0(fwcnfs, "vdom", regexp=False)
             if "edits" in c and any(e for e in c["edits"] if "configs" in e)]

    # {"config": "vdom", "edits": [{"edit": "root", "configs": [...]}]}
    if vcnfs:
        vedits = vcnfs[0]["edits"]  # len(vcnfs) should be 1.
        if vdom:
            ccnfs = (e["configs"] for e in vedits
                     if "configs" in e and e.get("edit") == vdom)
        else:
            ccnfs = (e["configs"] for e in vedits if "configs" in e)

        ccnfs = itertools.chain.from_iterable(ccnfs)
        cnfs = itertools.chain(gcnfs, ccnfs)

        return configs_by_name_0(cnfs, name, regexp=regexp)

    return configs_by_name_0(gcnfs, name, regexp=regexp)


def config_by_name(fwcnfs, name, regexp=False):
    """
    .. note::
       Even if there are more than one matched results were found, it returns
       the first item only.

    :param fwcnfs: A list of fortios config objects
    :param name: Name of the configuration
    :param regexp: Use regular expression in name

    :return: A list of config having edits or None
    """
    cnfs = configs_by_name(fwcnfs, name, regexp=regexp)
    if cnfs:
        # It should have an item only in most cases.
        return cnfs[0]

    return None


def edits_by_name(fwcnfs, name, regexp=False):
    """
    :param fwcnfs: A list of fortios config objects
    :param name: Name of the configuration has edits
    :param regexp: Use regular expression in name

    :return: A list of config edits or []
    """
    cnf = config_by_name(fwcnfs, name, regexp=regexp)
    if cnf:
        return cnf.get("edits", [])

    return []


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


def config_filename(name, ext="json"):
    """
    >>> config_filename("system global")
    'system_global.json'
    >>> config_filename('system replacemsg webproxy "deny"')
    'system_replacemsg_webproxy_deny.json'
    """
    cname = re.sub(r"[\"']", '', re.sub("[- ]+", '_', name))
    return "{}.{}".format(cname, ext)


def timestamp():
    """Generate timestamp string.
    """
    return datetime.datetime.now().strftime("%F %T")


def parse_show_config_and_dump(inpath, outpath, cnames=CNF_NAMES):
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

    cnfs = list_configs_from_config_data(data, filepath=inpath)
    try:
        hostname = hostname_from_configs(cnfs)
    except ValueError as exc:
        LOG.warning("%r: %s", exc, inpath)
        hostname = False

    if hostname:  # It should have this in most cases.
        outdir = os.path.join(os.path.dirname(outpath), hostname)

        vdoms = list(vdom_names_itr(cnfs)) or ["root"]
        anyconfig.dump(dict(timestamp=timestamp(), hostname=hostname,
                            vdoms=vdoms, origina_data=inpath),
                       os.path.join(outdir, METADATA_FILENAME))

        for name in cnames:
            cnf = edits_by_name(cnfs, name)
            if cnf is None:  # It should have edits but configs.
                cnf = config_by_name(cnfs, name)

            if cnf:
                opath = os.path.join(outdir, config_filename(name))
                anyconfig.dump(cnf, opath)

        for grp in CNF_GRPS:
            g_outpath = os.path.join(outdir, grp + ".json")
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
    >>> summarize_networks(net1, net2, prefix=16)
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
    edits = edits_by_name(fwcnfs, "firewall address")
    if not edits:
        raise ValueError(hostname_from_configs(fwcnfs))

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


def collect_net_info_from_files(config_files, max_prefix=NET_MAX_PREFIX):
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
    nodes_and_edges = list(collect_net_info_from_files(config_files,
                                                       max_prefix))
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
