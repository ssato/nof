#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
""".fortios.v1api test cases
"""
import os.path
import shutil

import nof.fortios.common as TT
import nof.libs
import nof.utils

from .. import common as C


class TestCase(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None

    # .. seealso:: tests/res/forti/show_configs/*.txt, hostname value.
    hostnames = "fortigate-01 fortigate-02".split()

    cnf_files = C.list_res_files("forti/show_configs/*.txt")

    def _arrange_uploaded_and_procecced_files(self):
        for fpath in self.cnf_files:
            # It's not a correct path but should be enough for this test case.
            upath = os.path.join(TT.uploaddir(), os.path.basename(fpath))
            nof.utils.ensure_dir_exists(upath)
            shutil.copy(fpath, upath)
            self.assertTrue(os.path.exists(upath))

            # Arrange dir and files
            nof.libs.parse_fortigate_config_and_save_files(upath)

    def test_10_list_hostnames__no_data(self):
        self.assertFalse(TT.list_hostnames())

    def test_12_list_hostnames__some_data(self):
        self._arrange_uploaded_and_procecced_files()
        res = TT.list_hostnames()

        self.assertTrue(res)
        self.assertEqual(res, self.hostnames)

    def test_20_list_host_files__no_data(self):
        for hname in self.hostnames:
            self.assertFalse(TT.list_host_files(hname))

    def test_22_list_host_files__some_data(self):
        self._arrange_uploaded_and_procecced_files()

        for hname in self.hostnames:
            self.assertFalse(
                TT.list_host_files(hname, includes=["not_exists.json"])
            )

            res = TT.list_host_files(hname)
            self.assertTrue(res)
            self.assertTrue(
                all(fname in res for fname in nof.libs.FORTI_FILENAMES)
            )

# vim:sw=4:ts=4:et:
