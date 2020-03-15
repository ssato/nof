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


def _inp_and_exp_result_files():
    inputs = glob.glob(os.path.join(C.resdir(), "fortios", "*.txt"))
    for inp_path in sorted(inputs):
        yield (inp_path, inp_path + ".exp.json")


class TT_10_Simple_Function_TestCases(unittest.TestCase):

    maxDiff = None

    def test_20_process_config_or_edit_line__config(self):
        exps = (("config system global\n", ('', 'system global')),
                ("    config fp-anomaly-v4\n", ('    ', 'fp-anomaly-v4')),
                ("config firewall service category\n",
                 ('', 'firewall service category')),
                ('config system replacemsg utm "virus-html"\n',
                 ('', 'system replacemsg utm "virus-html"')))

        for line, exp in exps:
            res = _try_match_and_proc(line, TT.CONFIG_START_RE,
                                      TT.process_config_or_edit_line)
            self.assertEqual(res, exp)

    def test_22_process_config_or_edit_line__edit(self):
        exps = (("    edit 1\n", ('    ', '1')),
                ('    edit "np6_0"\n', ('    ', 'np6_0')),
                ('    edit "VoIP, Messaging & Other Applications"',
                 ('    ', 'VoIP, Messaging & Other Applications')))

        for line, exp in exps:
            res = _try_match_and_proc(line, TT.EDIT_START_RE,
                                      TT.process_config_or_edit_line)
            self.assertEqual(res, exp)

    def test_30_process_set_or_unset_line(self):
        exps = (("    set admin-port 80\n",
                 dict(type="set", name="admin-port", values=["80"])),
                ("    unset ip6-allowaccess\n",
                 dict(type="unset", name="ip6-allowaccess")),
                ('    set admin-server-cert "Fortinet_Factory"\n',
                 dict(type="set", name="admin-server-cert",
                      values=["Fortinet_Factory"])),
                ('    set member "DNS" "HTTP" "HTTPS"\n',
                 dict(type="set", name="member",
                      values=["DNS", "HTTP", "HTTPS"])))

        for line, exp in exps:
            res = _try_match_and_proc(line, TT.SET_OR_UNSET_LINE_RE,
                                      TT.process_set_or_unset_line)
            self.assertEqual(res, exp)

    def test_80_parse_show_config__simple_config_set(self):
        for inp_path, exp_path in _inp_and_exp_result_files():
            res = TT.parse_show_config(inp_path)

            self.assertTrue(os.path.exists(exp_path))
            res_exp = TT.anyconfig.load(exp_path)["configs"]

            self.assertEqual(len(res), len(res_exp))
            for cnf, exp in zip(res, res_exp):
                self.assertEqual(cnf, exp, cnf)


class TT_20_Function_with_IO_TestCases(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None

    def _result_files(self):
        inputs = glob.glob(os.path.join(C.resdir(), "fortios", "*.txt"))
        for inp_path in sorted(inputs):
            out_path = os.path.join(self.workdir,
                                    os.path.basename(inp_path) + ".json")
            yield (inp_path, out_path, inp_path + ".exp.json")

    def test_10_parse_show_config_and_dump__simple_config_set(self):
        for inp_path, out_path, exp_path in self._result_files():
            res = TT.parse_show_config_and_dump(inp_path, out_path)

            self.assertTrue(os.path.exists(exp_path))
            res_exp = TT.anyconfig.load(exp_path)

            self.assertEqual(res, res_exp, repr(res))

# vim:sw=4:ts=4:et:
