#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path
import os
import shutil

import anyconfig

# import nof.main.v1api as TT
import nof.main.utils

from nof.main import API_PREFIX
from .. import common as C


def _url_path(*args):
    """
    >>> _url_path("graph", "a.yml")
    '/api/v1/graph/a.yml'
    """
    return '{}/{}'.format(API_PREFIX, '/'.join(args))


def _err_msg(resp, *args):
    return "data: {}{}{}".format(resp.data, os.linesep,
                                 os.linesep.join(args))


class V1_API_10_Simple_TestCase(C.BluePrintTestCaseWithWorkdir):

    def test_10_get_or_upload_graph__get(self):
        for filepath in C.ok_yml_files():
            shutil.copy(filepath, nof.main.utils.uploaddir())

            filename = os.path.basename(filepath)
            filepath_2 = nof.main.utils.upload_filepath(filename)
            self.assertTrue(os.path.exists(filepath_2))

            path = _url_path("graph", filename)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path,
                                      "file: " + filepath_2))
            self.assertEqual(resp.data, open(filepath, 'rb').read())

    def test_20_get_or_upload_graph__post(self):
        for filepath in C.ok_yml_files():
            filename = os.path.basename(filepath)
            headers = {"content-type": "application/yaml"}  # TBD

            data = open(filepath, 'rb').read()
            path = _url_path("graph", filename)
            resp = self.client.post(path, data=data, headers=headers)

            self.assertEqual(resp.status_code, 201, resp.data)

            outpath = nof.main.utils.processed_filepath(filename)
            outdata = anyconfig.load(outpath)

            self.assertTrue(os.path.exists(outpath))
            self.assertTrue(outdata.get("nodes", False))
            self.assertTrue(outdata.get("links", False))

    def test_30_get_node_link(self):
        for filepath in C.ok_yml_files():
            filename = os.path.basename(filepath)
            shutil.copy(filepath, nof.main.utils.uploaddir())

            nof.main.utils.generate_node_link_data_from_graph_data(filename)
            outpath = nof.main.utils.processed_filepath(filename)

            self.assertTrue(os.path.exists(outpath))

            path = _url_path("node_link", filename)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path,
                                      "outpath: " + outpath))
            self.assertEqual(resp.data, open(outpath, 'rb').read())


class V1_API_20_Network_TestCase(C.BluePrintTestCaseWithWorkdir):

    def setUp(self):
        super(V1_API_20_Network_TestCase, self).setUp()

        self.filename = "10_graph_nodes_and_links__ok.yml"
        filepath = os.path.join(C.resdir(), self.filename)

        shutil.copy(filepath, nof.main.utils.uploaddir())

    def test_10_find_networks_by_addr__not_found(self):
        ip = "127.0.0.1"
        path = _url_path("networks", "by_addr", self.filename, ip)
        resp = self.client.get(path)

        self.assertEqual(resp.status_code, 200,
                         _err_msg(resp, "path: " + path, "ip: " + ip))
        self.assertTrue(resp.data)
        data = anyconfig.loads(resp.data, ac_parser="json")

        self.assertEqual(data, [], data)

    def test_20_find_networks_by_addr__found(self):
        ip = "10.0.1.12"
        path = _url_path("networks", "by_addr", self.filename, ip)
        resp = self.client.get(path)

        self.assertEqual(resp.status_code, 200,
                         _err_msg(resp, "path: " + path, "ip: " + ip))
        self.assertTrue(resp.data)
        data = anyconfig.loads(resp.data, ac_parser="json")

        self.assertEqual(data[0]["addr"], "10.0.1.0/24", data[0])
        self.assertEqual(data[1]["addr"], "10.0.0.0/8", data[1])


class V1_API_30_Paths_TestCase(C.BluePrintTestCaseWithWorkdir):

    def setUp(self):
        super(V1_API_30_Paths_TestCase, self).setUp()

        self.filename = "10_graph_nodes_and_links__ok.yml"
        filepath = os.path.join(C.resdir(), self.filename)

        shutil.copy(filepath, nof.main.utils.uploaddir())
        nof.main.utils.generate_node_link_data_from_graph_data(self.filename)

    def test_10_find_node_link_paths__not_found(self):
        i_1 = "10.0.1.7"
        i_2 = "192.168.1.10"
        ips = [("127.0.0.1", "172.16.1.1"), (i_1, "172.16.1.1"),
               ("127.0.0.1", i_2)]

        for src, dst in ips:
            path = _url_path("node_link_paths", self.filename, src, dst)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path,
                                      "src: " + src, "dst: " + dst))
            self.assertTrue(resp.data)

            try:
                data = anyconfig.loads(resp.data, ac_parser="json")
                self.assertEqual(data, [])
            except:
                raise ValueError("data: " + repr(resp.data))

    def test_20_find_node_link_paths__found(self):
        i_1 = "10.0.1.7"
        i_2 = "192.168.1.10"
        ips = [(i_2, "10.0.1.2"), (i_1, i_2)]

        for src, dst in ips:
            path = _url_path("node_link_paths", self.filename, src, dst)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path,
                                      "src: " + src, "dst: " + dst))
            self.assertTrue(resp.data)

            try:
                data = anyconfig.loads(resp.data, ac_parser="json")
                self.assertTrue(data)
                res = data[0]
            except:
                raise ValueError("data: " + repr(resp.data))

            n_1 = "10.0.1.0/24"
            n_2 = "192.168.1.0/24"
            addrs = set(x["addr"] for x in res)

            self.assertTrue(n_1 in addrs, res)
            self.assertTrue(n_2 in addrs, res)

# vim:sw=4:ts=4:et:
