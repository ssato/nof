#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path
import shutil

import nof.main.utils as TT
from .. import common as C


def _show_dict(dict):
    return ", ".join("'{!s}': '{!s}'".format(*kv) for kv in dict.items())


class TT_10_path_functions_TestCases(C.BluePrintTestCaseWithWorkdir):

    def test_10_uploaddir(self):
        self.assertEqual(TT.uploaddir(), self.workdir)

    def test_20_graph_path(self):
        filename = "foo.yml"
        self.assertEqual(TT.graph_path(filename),
                         os.path.join(TT.uploaddir(), filename))

        filename = "../../foo.yml"
        self.assertNotEqual(TT.graph_path(filename),
                            os.path.join(TT.uploaddir(), filename))

    def test_30_node_link_filename(self):
        filename = "a.yml"
        res = TT.node_link_filename(filename)

        self.assertTrue(res)
        self.assertTrue(res.endswith(".json"))
        self.assertNotEqual(res, os.path.join(TT.uploaddir(), filename))


class TT_20_util_functions_TestCases(C.BluePrintTestCaseWithWorkdir):

    def test_10_generate_node_link_data_from_graph_data(self):
        for filepath in C.ok_yml_files():
            shutil.copy(filepath, TT.uploaddir())

            filename = os.path.basename(filepath)
            TT.generate_node_link_data_from_graph_data(filename)

            outpath = TT.node_link_path(filename)
            self.assertTrue(os.path.exists(outpath))
            self.assertTrue(outpath.endswith(".json"))

    def test_20_find_paths_from_graph(self):
        filename = "10_graph_nodes_and_links__ok.yml"
        filepath = os.path.join(C.resdir(), filename)
        shutil.copy(filepath, TT.uploaddir())

        i_1 = "10.0.1.7"
        i_2 = "192.168.1.10"
        fun = TT.find_paths_from_graph

        self.assertEqual(fun(filename, "127.0.0.1", "172.16.1.1"), [])
        self.assertEqual(fun(filename, i_1, "172.16.1.1"), [])
        self.assertEqual(fun(filename, "127.0.0.1", i_2), [])

        res_1 = fun(filename, i_1, "10.0.1.2")  # :: [[<dict>]]
        res_2 = fun(filename, i_1, i_2)

        self.assertTrue(res_1)
        self.assertTrue(res_2)
        self.assertTrue(res_1[0])  # res_1[0] :: [<dict>]
        self.assertTrue(res_2[0])
        self.assertEqual(len(res_1[0]), 1)
        self.assertTrue(len(res_2[0]) > 1)

        n_1 = "10.0.1.0/24"
        n_2 = "192.168.1.0/24"

        self.assertEqual(n_1, res_1[0][0]["addr"], repr(res_1))
        self.assertEqual(n_2, res_2[0][-1]["addr"], repr(res_2[0][-1]["addr"]))

    def test_30_list_filenames(self):
        for filepath in C.ok_yml_files():
            shutil.copy(filepath, TT.uploaddir())

        res = TT.list_filenames()
        exp = sorted(os.path.basename(f) for f in C.ok_yml_files())

        self.assertEqual(len(res), len(C.ok_yml_files()))
        self.assertEqual(res, exp, res)

# vim:sw=4:ts=4:et:
