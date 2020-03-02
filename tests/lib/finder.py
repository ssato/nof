#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import itertools
import os.path
import random
import unittest

import nof.lib.finder as TT
import nof.globals as G

from .. import common as C


NG_IPS = ["127.0.0.1", "192.168.3.7", "224.0.0.1"]


class Node_link_TestCase(unittest.TestCase):

    def _is_node_link(self, node_link):
        self.assertTrue(node_link)

        for key in ("nodes", "links"):
            self.assertTrue(key in node_link)

        links = node_link["links"]
        if links:
            for key in ("source", "target"):
                self.assertTrue(all(key in l for l in links))


class TT_10_Simple_Function_TestCases(Node_link_TestCase):

    def test_10_is_net_node(self):
        self.assertFalse(TT.is_net_node(dict()))
        self.assertFalse(TT.is_net_node(dict(type=None)))
        self.assertFalse(TT.is_net_node(dict(type=True)))

        self.assertTrue(TT.is_net_node(dict(type=TT.NODE_NET)))

    def test_20_load(self):
        for inp in C.ok_yml_files():
            graph = TT.load(inp)
            self.assertTrue(graph)
            self.assertTrue(isinstance(graph, TT.networkx.Graph))

    def test_30_to_node_link_data(self):
        for inp in C.ok_yml_files():
            graph = TT.load(inp)
            node_link = TT.to_node_link_data(graph)
            self._is_node_link(node_link)


class TT_20_Simple_Function_TestCases(Node_link_TestCase):

    def setUp(self):
        self.workdir = C.setup_workdir()

    def teardown(self):
        C.prune_workdir(self.workdir)

    def test_10_save_as_node_link(self):
        for inp in C.ok_yml_files():
            graph = TT.load(inp)
            outpath = os.path.join(self.workdir, "out.json")
            TT.save_as_node_link(graph, outpath)
            node_link = TT.anyconfig.load(outpath)

            self.assertTrue(os.path.exists(outpath))
            self._is_node_link(node_link)


class TT_30_find_network_nodes_by_addr_TestCases(unittest.TestCase):

    # .. seealso:: tests/res/*.yml
    ok_ips = ["10.0.1.1", "10.0.0.254", "192.168.1.254"]
    ng_ips = NG_IPS

    nets = [dict(type=TT.NODE_NET,
                 addr=TT.ipaddress.ip_network(ip)) for ip
            in ("10.0.1.0/24", "10.0.0.0/8", "192.168.1.0/24")]

    nodes = nets + [dict(type=None), dict(type=True),
                    dict(type="host", addr="10.0.1.1")]

    def test_10_find_network_nodes_by_addr__not_found(self):
        for ip in self.ok_ips + self.ng_ips:
            res = TT.find_network_nodes_by_addr([], ip)
            self.assertFalse(res)
            self.assertEqual(res, [])

        for ip in self.ng_ips:
            res = TT.find_network_nodes_by_addr(self.nodes, ip)
            self.assertFalse(res)
            self.assertEqual(res, [])

    def test_12_find_network_nodes_by_addr__found_1(self):
        res = TT.find_network_nodes_by_addr(self.nodes, self.ok_ips[-1])

        self.assertNotEqual(res, [])
        self.assertTrue(isinstance(res[0]["addr"], TT.ipaddress.IPv4Network))
        self.assertTrue(TT.is_net_node(res[0]))
        self.assertEqual(res[0], self.nets[-1])

    def test_14_find_network_nodes_by_addr__found_some(self):
        res = TT.find_network_nodes_by_addr(self.nodes, self.ok_ips[0])

        self.assertNotEqual(res, [])
        self.assertEqual(res, self.nets[:-1])

    def test_20_find_network_nodes_by_addr__found(self):
        for ip in self.ng_ips:
            res = TT.find_network_node_by_addr(self.nodes, ip)
            self.assertTrue(res is None)

    def test_22_find_network_nodes_by_addr__found(self):
        for ip, net in zip(self.ok_ips, self.nets):
            res = TT.find_network_node_by_addr(self.nodes, ip)

            self.assertTrue(res is not None)
            self.assertTrue(isinstance(res["addr"], TT.ipaddress.IPv4Network))
            self.assertEqual(res, net)


class With_Test_Resource_TestCase(unittest.TestCase):

    filepath = os.path.join(C.resdir(), "10_graph_nodes_and_links__ok.yml")
    graph = TT.load(filepath)


class TT_40_find_networks_by_addr_TestCases(With_Test_Resource_TestCase):

    def test_10_find_networks_by_addr__not_found(self):
        for ip in NG_IPS:
            res = TT.find_networks_by_addr(self.graph, ip)
            self.assertEqual(res, [])

    def test_20_find_networks_by_addr__found_1(self):
        # .. seealso:: tests/res/10_graph_nodes_and_links__ok.yml
        ip = "192.168.1.2"
        res = TT.find_networks_by_addr(self.graph, ip)

        self.assertNotEqual(res, [])
        self.assertEqual(len(res), 1)

        net = res[0]
        self.assertEqual(net["type"], TT.NODE_NET)
        self.assertEqual(net["addr"], "192.168.1.0/24")

    def test_30_find_networks_by_addr__found_some(self):
        # .. seealso:: tests/res/10_graph_nodes_and_links__ok.yml
        ip = "10.0.1.254"
        nets = ["10.0.1.0/24", "10.0.0.0/8"]
        res = TT.find_networks_by_addr(self.graph, ip)

        self.assertNotEqual(res, [])
        self.assertTrue(len(res) > 1)

        res_nets = [n["addr"] for n in res]
        self.assertTrue(all(n in res_nets for n in nets))
        self.assertEqual(res_nets[0], nets[0], res_nets)
        self.assertEqual(res_nets, nets, res_nets)


class TT_50_find_paths_TestCases(With_Test_Resource_TestCase):
    # .. seealso:: tests/res/*.yml
    ok_ips = ["10.0.1.1", "10.0.0.254", "192.168.1.254"]

    def test_10_find_paths__not_found(self):
        ng_ips = random.sample(NG_IPS, len(NG_IPS))

        ng_ng_pairs = (random.sample(ng_ips, 2) for _i in range(3))
        ng_ok_pairs = zip(ng_ips, self.ok_ips)
        ok_ng_pairs = zip(self.ok_ips, ng_ips)

        for src, dst in itertools.chain(ng_ng_pairs, ng_ok_pairs,
                                        ok_ng_pairs):
            res = TT.find_paths(self.graph, src, dst)
            self.assertEqual(res, [])

    def test_20_find_paths__native_found_1_path_1_net(self):
        src = "192.168.1.1"
        dst = "192.168.1.7"

        res = TT.find_paths(self.graph, src, dst)
        self.assertNotEqual(res, [])
        self.assertTrue(len(res), 1)

        path = res[0]
        self.assertEqual(path[0]["addr"], "192.168.1.0/24", path)

        # set node_type matches result's node type
        res = TT.find_paths(self.graph, src, dst, node_type=G.NODE_NET)
        path = res[0]
        self.assertEqual(path[0]["addr"], "192.168.1.0/24", path)

        # set node_type does not match result's node type
        res = TT.find_paths(self.graph, src, dst, node_type=G.NODE_HOST)
        self.assertEqual(res, [])

    def test_22_find_paths__native_found_1_path_some_nets(self):
        src = "10.0.1.1"
        dst = "192.168.1.7"

        res = TT.find_paths(self.graph, src, dst)
        self.assertNotEqual(res, [])
        self.assertTrue(len(res), 1)

        path = res[0]
        self.assertTrue(len(path) > 1)

        exp_nets = ("10.0.1.0/24", "192.168.1.0/24")
        exp_hosts = ("10.0.1.254", "10.0.0.1")
        paddrs = [x["addr"] for x in path]

        self.assertTrue(all(n in paddrs for n in exp_nets), paddrs)
        self.assertTrue(all(n in paddrs for n in exp_hosts), paddrs)

# vim:sw=4:ts=4:et:
