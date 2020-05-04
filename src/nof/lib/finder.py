#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Network objects finding APIs.

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import functools
import ipaddress

import anyconfig
import networkx
import networkx.readwrite.json_graph


# Network node is an object have some attributes.
# - id: int, Unique node ID
# - type: str, see the definition of NODE_TYPES
# - addr_type: net or ipset
# - addrs: A list of str represents any IP address or network
# - description: str, some descriptions about the node (option)
# - notes: str, some notes about the node (option)
NODE_TYPES = (NODE_ANY, NODE_NET, NODE_IPSET, NODE_HOST,
              NODE_ROUTER, NODE_SWITCH, NODE_FIREWALL) \
           = ("any", "network", "ipset", "host",
              "router", "switch", "firewall")


def is_net_node(node):
    """
    :return: True if given `node` is network node else False
    """
    return node.get("type", None) == NODE_NET


def _to_net_node_itr(node):
    """
    :param node:
        A mapping object represents a network node should have 'addrs' key and
        any IP address value.

    :yield: (key, [<ip_or_net_address_object>] or original val)
    """
    for key, val in node.items():
        if key == "addrs":
            if is_net_node(node):
                yield (key, [ipaddress.ip_network(i) for i in val])
            else:
                yield (key,
                       [ipaddress.ip_interface(i).ip for i in val])
        else:
            yield (key, val)


def _to_net_node_dicts_itr(nodes):
    """
    :param nodes:
        A list of mapping objects should have 'addrs' key and represents some
        network objects like network, host, switch, router and firewall

    :yield: A mapping object rerepsesnts that network node
    """
    for idx, node in enumerate(nodes):
        ndic = dict(_to_net_node_itr(node))

        if "id" not in ndic:
            ndic["id"] = idx

        yield ndic


def to_net_nodes(nodes):
    """
    :param nodes:
        A list of mapping objects should have 'addrs' key and represents some
        network objects like network, host, switch, router and firewall
    :return: [{'addrs': [<ip_or_net_address_object>], ...}]
    """
    return list(_to_net_node_dicts_itr(nodes))


def _to_ext_native_node_dicts_itr(nodes):
    """
    :param nodes: [{'addrs': <ip_or_net_address_object>, ...}]
    :yield: <a_node_dict_only_having_native_values>
    """
    for node in nodes:
        ndic = dict(**node)

        ndic["addrs"] = [str(i) for i in node["addrs"]]
        ndic["type_id"] = NODE_TYPES.index(node["type"])
        ndic["class"] = "node {0[type]}".format(node)
        ndic["label"] = "{0[name]} ({0[type]})".format(node)

        yield ndic


def to_ext_native_dicts(nodes):
    """
    :param nodes: [{'addrs': <ip_or_net_address_object>, ...}]
    :return: [{'addrs': [ip_addr_string], ...}]
    """
    return list(_to_ext_native_node_dicts_itr(nodes))


def list_nodes_from_graph(graph):
    """
    :param graph: A networkx.Graph object
    :return: [{'addrs': [<ip_or_net_address_object>], ...}]
    """
    return [graph.nodes[idx] for idx in graph.nodes]


def load(graph_filepath, **ac_args):
    """
    :param graph_filepath:
        File path of network graph data ({'nodes': ..., 'edges': ...})
    :param ac_args: keyword arguments given to anyconfig.load

    :return: An instance of networkx.Graph
    """
    data = anyconfig.load(graph_filepath, **ac_args)
    nodes = to_net_nodes(data["nodes"])

    if data["links"] and "edges" in data["links"][0]:
        edges = data["edges"]
    else:
        edges = [(l["source"], l["target"]) for l in data["links"]]

    graph = networkx.Graph()
    graph.add_nodes_from((n["id"], n) for n in nodes)
    graph.add_edges_from(edges)

    return graph


def to_node_link_data(graph):
    """Transform graph to JSON serializable data.

    :param graph: networkx.Graph object to find paths from
    """
    res = networkx.readwrite.json_graph.node_link_data(graph)

    # .. note:: Needed to make it serializable to JSON data
    res["nodes"] = to_ext_native_dicts(res["nodes"])

    return res


def save_as_node_link(graph, outpath, **json_dump_opts):
    """Convert graph data to node-link data used in D3.js and save it.

    :param graph: networkx.Graph object to find paths from
    :param outpath: Output file path
    """
    json_data = to_node_link_data(graph)
    anyconfig.dump(json_data, outpath, ac_parser="json", **json_dump_opts)


def _find_network_or_ipset_nodes_by_addr_itr(nodes, addr):
    """
    :param nodes: {'addrs': [<ip_or_net_address_object>], 'type': ..., ...}
    :param addr:
        An instance of :class:`ipaddress.IPv4Address` or
        :class:`ipaddress.IPv6Address`, or str represents an ip address

    .. note:: 10.0.0.0/8 < 10.1.1.0/24 in ipaddress
    """
    addr_types = (ipaddress.IPv4Address, ipaddress.IPv6Address)
    net_types = (ipaddress.IPv4Network, ipaddress.IPv6Network)

    if not isinstance(addr, addr_types):
        addr = ipaddress.ip_address(addr)

    for node in nodes:
        ntype = node["type"]

        if ntype == NODE_NET:
            for net in node["addrs"]:
                if not isinstance(net, net_types):
                    net = ipaddress.ip_network(net)

                if addr in net:
                    yield node

        elif ntype == NODE_IPSET:
            for ip in node["addrs"]:
                if not isinstance(net, addr_types):
                    ip = ipaddress.ip_address(ip)

                if ip == addr:
                    yield node


def cmp_network_or_ipset_nodes(lhs, rhs):
    """
    rules:
      - NODE_IPSET >> NODE_NET
      - NODE_IPSET: Smaller number of IPs is "bigger"
      - NODE_NET: Smaller segment is "bigger", e.g. 192.168.1.0/24 >>
        192.168.0.0/16

    :param lhs: {'addr': <ip_or_net_address_object>, 'type': ..., ...}
    :param rhs: likewise
    """
    (lhs_t, rhs_t) = (lhs["type"], rhs["type"])

    if lhs_t == rhs_t:
        if lhs["addrs"] == rhs["addrs"]:
            return 0

        if lhs_t == NODE_IPSET:
            # Less IPs is "bigger".
            return len(rhs["addrs"]) - len(lhs["addrs"])

        # e.g. IPv4Network("192.168.0.0/16") < IPv4Network("192.168.1.0/24")
        return -1 if lhs["addrs"][0] < rhs["addrs"][0] else 1

    # NODE_NET < NODE_IPSET
    return -1 if lhs_t == NODE_NET else 1


def find_network_or_ipset_nodes_by_addr(nodes, addr):
    """
    :param nodes: {'addr': <ip_or_net_address_object>, 'type': ..., ...}
    :param addr:
        An instance of :class:`ipaddress.IPv4Address` or
        :class:`ipaddress.IPv6Address` or str represents an ip address

    :return:
        [] or a list of network nodes sorted by its 'size' in reversed order

    .. note:: 10.0.0.0/8 < 10.1.1.0/24 in ipaddress
    """
    return sorted(_find_network_or_ipset_nodes_by_addr_itr(nodes, addr),
                  key=functools.cmp_to_key(cmp_network_or_ipset_nodes),
                  reverse=True)


def find_network_or_ipset_node_by_addr(nodes, addr):
    """
    :param nodes: a mapping object has key, addr
    :param addr: ipaddress.ip_address object or a string represents IP address
    :return: A (smallest) network or None

    .. seealso:: `find_network_nodes_by_addr`
    """
    nets = find_network_or_ipset_nodes_by_addr(nodes, addr)
    return nets[0] if nets else None


def find_networks_or_ipsets_by_addr(graph, ip):
    """
    :param graph: networkx.Graph object to find paths from
    :param ip: ipaddress.ip_address object or a string represents IP address

    :return: A list of network nodes should contain the given `ip`
    :raises: ValueError if given ip is not an IP address string
    """
    nodes = list_nodes_from_graph(graph)
    nets = find_network_or_ipset_nodes_by_addr(nodes, ip)
    return to_ext_native_dicts(nets)


def find_network_or_ipset_by_addr(graph, ip):
    """
    :param graph: networkx.Graph object to find paths from
    :param ip: ipaddress.ip_address object or a string represents IP address

    :return: A smallest network node should contain the given `ip` or None
    :raises: ValueError if given ip is not an IP address string
    """
    nets = find_networks_or_ipsets_by_addr(graph, ip)
    if nets:
        return nets[0]

    return None


def select_unique_paths_itr(paths):
    """
    :param paths: A list of lists of nodes in the found paths
    :return: A generator yields a filtered a list of nodes in the paths
    """
    seen = set()
    for path in paths:  # path :: [{id: ..., } (node), ...]
        path_by_node_ids = tuple(n["id"] for n in path)
        if path_by_node_ids not in seen:
            seen.add(path_by_node_ids)
            yield path


def find_paths(graph, src, dst, node_type=False, **nx_opts):
    """
    :param graph: networkx.Graph object to find paths from
    :param src: ipaddress.ip_address object or a string represents IP address
    :param dst: ipaddress.ip_address object or a string represents IP address
    :param node_type: Node type to filter results if given
    :param nx_opts:
        Keyword options given to networkx.all_shortest_paths() such as method,
        and weight

    :return: A list of lists of nodes in the found paths
    :raises: ValueError if given src and/or dst is not an IP address string
    """
    nodes = list_nodes_from_graph(graph)

    # raises: ValueError
    src_ip = ipaddress.ip_address(src)
    dst_ip = ipaddress.ip_address(dst)

    src_net = find_network_or_ipset_node_by_addr(nodes, src_ip)
    dst_net = find_network_or_ipset_node_by_addr(nodes, dst_ip)

    if src_net and dst_net:
        if src_net == dst_net:
            if not node_type or (node_type and node_type != NODE_ANY and
                                 src_net["type"] == node_type):
                return [to_ext_native_dicts([src_net])]

            return []

        nss = networkx.all_shortest_paths(graph, src_net["id"], dst_net["id"],
                                          **nx_opts)
        res = [[n for n in nodes if n["id"] in ns] for ns in nss]

        if node_type and node_type != NODE_ANY:
            # Those paths might be degenerated and need to remove duplicates.
            pitr = ([n for n in ns if n["type"] == node_type] for ns in res)
            res = list(select_unique_paths_itr(pitr))

        res = [[src_net] + ns + [dst_net] for ns in res]

        return [to_ext_native_dicts(ns) for ns in res]

    return []

# vim:sw=4:ts=4:et:
