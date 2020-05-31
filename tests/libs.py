# Copyright (C) 2020 Red Hat, Inc.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
"""nof.libs test cases
"""
import glob
import os.path

import nof.libs as TT

from . import common as C


class V1_API_10_TestCase(C.BluePrintTestCaseWithWorkdir):

    cleanup = False
    cnf_files = C.list_res_files("forti/show_configs/*.txt")

    def test_10_parse_fortigate_config_and_save_files(self):
        for src in self.cnf_files:
            TT.parse_fortigate_config_and_save_files(src)
            ofiles = glob.glob(os.path.join(os.path.dirname(src),
                                            '*', "*.json"))
            self.assertTrue(ofiles)

# vim:sw=4:ts=4:et:
