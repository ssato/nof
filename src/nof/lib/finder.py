#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
r"""Network objects finding APIs.

.. versionadded:: 0.1.0

   - initial checkin
"""
from __future__ import absolute_import

import ipaddress
import operator

import anyconfig
import networkx
import networkx.readwrite.json_graph


NOF_DATA_DIR = "/var/lib/nof"

NODE_TYPES = (NODE_ANY, NODE_NET, NODE_ROUTER, NODE_FIREWALL, NODE_SWITCH,
              NODE_HOST) \
           = ("any", "network", "firewall", "router", "switch", "host")


def is_net_node(node):
    """
    :return: True if given `node` is network node else False
    """
    return node.get("type", None) == NODE_NET


def _to_ip_or_net_node_itr(node):
    """
    :param node: A dict should have 'addr' key and any IP address value
    :yield: (key, <ip_or_net_address_object> or original val)
    """
    for key, val in node.items():
        if key == "addr":
            if is_net_node(node):
                yield (key, ipaddress.ip_network(val))
            else:
                yield (key, ipaddress.ip_address(val))
        else:
            yield (key, val)


def to_ip_or_net_nodes(nodes):
    """
    :param nodes:
        A list of dicts should have 'addr' key and represents some network
        objects like network, host, switch, router and firewall
    :return: [{'addr': <ip_or_net_address_object>, ...}]
    """
    return [dict(_to_ip_or_net_node_itr(n)) for n in nodes]


def _to_ext_native_node_dicts_itr(nodes):
    """
    :param nodes: [{'addr': <ip_or_net_address_object>, ...}]
    :yield: <a_node_dict_only_having_native_values>
    """
    for node in nodes:
        node["addr"] = str(node["addr"])
        node["type_id"] = NODE_TYPES.index(node["type"])
        node["class"] = "node {0[type]}".format(node)
        node["label"] = "{0[name]}: {0[addr]}".format(node)

        yield node


def to_ext_native_dicts(nodes):
    """
    :param nodes: [{'addr': <ip_or_net_address_object>, ...}]
    :return: [{'addr': ip_addr_string, ...}]
    """
    return list(_to_ext_native_node_dicts_itr(nodes))


def list_nodes_from_graph(graph):
    """
    :param graph: A networkx.Graph object
    :return: [{'addr': <ip_or_net_address_object>, ...}]
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
    nodes = to_ip_or_net_nodes(data["nodes"])
    edges = data["edges"]

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


def _find_network_nodes_by_addr_itr(nodes, addr):
    """
    :param nodes: {'addr': <ip_or_net_address_object>, 'type': ..., ...}
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
        if not is_net_node(node):
            continue

        net = node["addr"]
        # FIXME
        # assert isinstance(net, net_types), (
        #    "node: {!r}, node['addr']: {!r}".format(node, net))
        if not isinstance(net, net_types):
            net = ipaddress.ip_network(net)

        if addr in net:
            yield node


def find_network_nodes_by_addr(nodes, addr):
    """
    :param nodes: {'addr': <ip_or_net_address_object>, 'type': ..., ...}
    :param addr:
        An instance of :class:`ipaddress.IPv4Address` or
        :class:`ipaddress.IPv6Address` or str represents an ip address

    :return:
        [] or a list of network nodes sorted by its 'size' in reversed order

    .. note:: 10.0.0.0/8 < 10.1.1.0/24 in ipaddress
    """
    return sorted(_find_network_nodes_by_addr_itr(nodes, addr),
                  key=operator.itemgetter("addr"),
                  reverse=True)


def find_network_node_by_addr(nodes, addr):
    """
    :param nodes: a mapping object has key, addr
    :param addr: ipaddress.ip_address object or a string represents IP address
    :return: A (smallest) network or None

    .. seealso:: `find_network_nodes_by_addr`
    """
    nets = find_network_nodes_by_addr(nodes, addr)
    return nets[0] if nets else None


def find_networks_by_addr(graph, ip):
    """
    :param graph: networkx.Graph object to find paths from
    :param ip: ipaddress.ip_address object or a string represents IP address

    :return: A list of network nodes should contain the given `ip`
    :raises: ValueError if given ip is not an IP address string
    """
    nodes = list_nodes_from_graph(graph)
    nets = find_network_nodes_by_addr(nodes, ip)
    return to_ext_native_dicts(nets)


def find_network_by_addr(graph, ip):
    """
    :param graph: networkx.Graph object to find paths from
    :param ip: ipaddress.ip_address object or a string represents IP address

    :return: A smallest network node should contain the given `ip` or None
    :raises: ValueError if given ip is not an IP address string
    """
    nets = find_networks_by_addr(graph, ip)
    if nets:
        return nets[0]

    return None


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

    src_net = find_network_node_by_addr(nodes, src_ip)
    dst_net = find_network_node_by_addr(nodes, dst_ip)

    if not node_type:
        node_type = NODE_ANY

    if src_net and dst_net:
        if src_net == dst_net:
            if node_type in (NODE_ANY, NODE_NET):
                return [to_ext_native_dicts([src_net])]

            return []

        nss = networkx.all_shortest_paths(graph, src_net["id"], dst_net["id"],
                                          **nx_opts)
        res = [[src_net] + [n for n in nodes if n["id"] in ns] + [dst_net]
               for ns in nss]

        if node_type != NODE_ANY:
            res = [[n for n in ns if n["type"] == node_type] for ns in res]

        return [to_ext_native_dicts(ns) for ns in res]

    return []

# vim:sw=4:ts=4:et:
