#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
""".fortios.v1api test cases
"""
# import nof.fortios.views as TT
from . import common


# .. seealso:: nof.fortios.views
IDX_PATH = "/fortios/"
H_FW_PATH = IDX_PATH + "/firewall/policies/"


class TestCase(common.TestBase):

    def test_10_index__no_data(self):
        resp = self.client.get(IDX_PATH)
        self.assert200(resp)

        # .. seealso:: src/nof/templates/fortios_index.html
        "fortigate-nodes" in resp.data.decode("utf-8")

    def test_12_index__some_data(self):
        self._arrange_uploaded_and_procecced_files()
        resp = self.client.get(IDX_PATH)
        self.assert200(resp)

        # .. seealso:: src/nof/templates/fortios_index.html
        "fortigate-nodes-table" in resp.data.decode("utf-8")

    def test_20_host_firewall_policies(self):
        self._arrange_uploaded_and_procecced_files()
        for hname in self.hostnames:
            upath = "{}/{}/".format(H_FW_PATH, hname)
            resp = self.client.get(upath)
            self.assert200(resp)

# vim:sw=4:ts=4:et:
