#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name
import glob
import os.path
import unittest

import anyconfig

import nof.lib.fortios as TT
from .. import common as C


def _process(reg, proc_fn, line):
    return proc_fn(reg.match(line))


def _inp_and_exp_result_files():
    inputs = glob.glob(os.path.join(C.resdir(), "fortios", "*.txt"))
    for inp_path in sorted(inputs):
        yield (inp_path, inp_path + ".exp.json")


class TT_10_Simple_Function_TestCases(unittest.TestCase):

    maxDiff = None

    def test_10_list_matches(self):
        # A pair of (line, expected_result)
        les = ((TT.COMMENT_RE, "#global_vdom=1\n", ["global_vdom=1"]),
               (TT.CONFIG_START_RE,
                "config system global\n", ["system", "global"]),
               (TT.CONFIG_START_RE,
                "        config fp-anomaly-v4\n", ["fp-anomaly-v4"]),
               (TT.EDIT_START_RE, "    edit 1\n", ["1"]),
               (TT.EDIT_START_RE, '    edit "np6_0"\n', ["np6_0"]),
               (TT.SET_OR_UNSET_LINE_RE,
                "    set ssd-trim-min 60\n", ["set", "ssd-trim-min", "60"]),
               (TT.SET_OR_UNSET_LINE_RE,
                '        set service "HTTP" "PING" "TRACEROUTE"\n',
                ["set", "service", '"HTTP" "PING" "TRACEROUTE"']),
               (TT.SET_OR_UNSET_LINE_RE,
                "    unset ssd-trim-weekday\n", ["unset", "ssd-trim-weekday"]),
               (TT.SET_OR_UNSET_LINE_RE,
                '    set vdom "root"\n', ["set", "vdom", '"root"']))

        for reg, line, exp in les:
            try:
                matches = reg.match(line).groups()
            except AttributeError as exc:
                raise ValueError("{!s}: line={}, "
                                 "reg={!r}".format(exc, line, exp))
            self.assertEqual(TT.list_matches(matches), exp)

    def test_20_process_config_or_edit_line(self):
        res = _process(TT.CONFIG_START_RE, TT.process_config_or_edit_line,
                       "config system interface\n")
        self.assertEqual(res, ('', 'system interface'))

        res = _process(TT.CONFIG_START_RE, TT.process_config_or_edit_line,
                       "        config ipv6\n")
        self.assertEqual(res, ('        ', 'ipv6'))

    def test_30_process_set_or_unset_line(self):
        res = _process(TT.SET_OR_UNSET_LINE_RE, TT.process_set_or_unset_line,
                       "    set admin-port 80\n")
        self.assertDictEqual(res, dict(type="set", name="admin-port",
                                       values=["80"]))

        res = _process(TT.SET_OR_UNSET_LINE_RE, TT.process_set_or_unset_line,
                       "    unset ip6-allowaccess\n")
        self.assertDictEqual(res, dict(type="unset", name="ip6-allowaccess"))

        res = _process(TT.SET_OR_UNSET_LINE_RE, TT.process_set_or_unset_line,
                       '    set admin-server-cert "Fortinet_Factory"\n')
        self.assertDictEqual(res, dict(type="set", name="admin-server-cert",
                                       values=["Fortinet_Factory"]))

        res = _process(TT.SET_OR_UNSET_LINE_RE, TT.process_set_or_unset_line,
                       '    set member "DNS" "HTTP" "HTTPS"\n')
        self.assertDictEqual(res, dict(type="set", name="member",
                                       values=["DNS", "HTTP", "HTTPS"]))

    def test_80_parse_show_config__simple_config_set(self):
        for inp_path, exp_path in _inp_and_exp_result_files():
            res = TT.parse_show_config(inp_path)

            self.assertTrue(os.path.exists(exp_path))
            res_exp = anyconfig.load(exp_path)["configs"]

            self.assertEqual(len(res),  len(res_exp))
            for cnf, exp in zip(res, res_exp):
                self.assertDictEqual(cnf, exp, cnf)

    def test_90_parse_show_config_and_dump__simple_config_set(self):
        for inp_path, exp_path in _inp_and_exp_result_files():
            res = TT.parse_show_config_and_dump(inp_path, exp_path)

            self.assertTrue(os.path.exists(exp_path))
            res_exp = anyconfig.load(exp_path)

            self.assertDictEqual(res, res_exp, repr(res))

# vim:sw=4:ts=4:et:
