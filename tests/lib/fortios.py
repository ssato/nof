#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# License: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path
import unittest

import nof.lib.fortios as TT
from .. import common as C


class TT_10_Simple_Function_TestCases(unittest.TestCase):

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
                "    unset ssd-trim-weekday\n", ["unset", "ssd-trim-weekday"]),
               (TT.SET_OR_UNSET_LINE_RE,
                '    set vdom "root"\n', ["set", "vdom", "root"]))

        for reg, line, exp in les:
            try:
                matches = reg.match(line).groups()
            except AttributeError as exc:
                raise ValueError("{!s}: line={}, "
                                 "reg={!r}".format(exc, line, exp))
            self.assertEqual(TT.list_matches(matches), exp)

    def test_20_process_config_line(self):
        pass       

# vim:sw=4:ts=4:et:
