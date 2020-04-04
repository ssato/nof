#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import glob
import os.path
import unittest

import nof.lib.fortios as TT
from .. import common as C


def _try_match_and_proc(line, reg, proc_fn):
    matched = reg.match(line)
    try:
        return proc_fn(matched)
    except AttributeError:
        raise ValueError("Not match! line={}".format(line))


def _result_files(workdir):
    inputs = glob.glob(os.path.join(C.resdir(), "fortios", "*.txt"))
    for inp_path in sorted(inputs):
        exp_path = os.path.join(inp_path + ".exp", "ref.json")
        out_path = os.path.join(workdir, os.path.basename(inp_path) + ".json")
        yield (inp_path, out_path, exp_path)


class TT_10_Simple_Function_TestCases(unittest.TestCase):

    maxDiff = None

    def test_20_parse_show_config__simple_config_set(self):
        for inp_path, _out_path, exp_path in _result_files("/tmp"):
            self.assertTrue(os.path.exists(exp_path), exp_path)
            exp = TT.anyconfig.load(exp_path)

            res = TT.parse_show_config(inp_path)
            self.assertEqual(res, exp)

    def test_50_hostname_from_configs(self):
        hostname = "nof-test-1"
        css = [[dict(config="system global", hostname=hostname)],
               [dict(config="global", hostname=hostname)]]
        for cnfs in css:
            self.assertEqual(TT.hostname_from_configs(cnfs), hostname)

        with self.assertRaises(ValueError):
            TT.hostname_from_configs([])

        cnfs = [dict(config="system global")]
        self.assertEqual(TT.hostname_from_configs(cnfs), None)


class TT_20_Function_with_IO_TestCases(C.BluePrintTestCaseWithWorkdir):

    def test_10_parse_show_config_and_dump__simple_config_set(self):
        for inp_path, out_path, exp_path in _result_files(self.workdir):
            res = TT.parse_show_config_and_dump(inp_path, out_path)

            self.assertTrue(os.path.exists(exp_path))
            res_exp = TT.anyconfig.load(exp_path)

            self.assertEqual(res, res_exp, repr(res))

# vim:sw=4:ts=4:et:
