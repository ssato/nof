#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
""".fortios.v1api test cases
"""
import os.path

import anyconfig

import nof.fortios.v1api as TT
import nof.libs
import nof.utils

from nof.fortios.common import API_PREFIX
from . import common


# .. seealso:: nof.fortios.v1api
UP_PREFIX = os.path.join(API_PREFIX, "upload/")
GET_PREFIX = os.path.join(API_PREFIX, "configs/")
FIND_PREFIX = os.path.join(API_PREFIX, "firewall/policies/by_addr/")


class V1_API_10_TestCase(common.TestBase):

    hosts = "fortigate-01 fortigate-02".split()

    def test_10_upload_show_config__wrong_data(self):
        fname = os.path.basename(__file__)

        # .. seealso:: nof.fortios.v1api.UP_PATH
        rpath = os.path.join(UP_PREFIX, fname)
        content = open(__file__).read()
        headers = {"content-type": "text/plain"}

        # API: upload_show_config
        resp = self.client.post(rpath, data=content, headers=headers)
        self.assertStatus(resp, 400, resp.data)

        # API: index
        resp = self.client.get(API_PREFIX + TT.IDX_PATH)
        self.assertStatus(resp, 204, resp.data)  # 204: no content
        self.assertFalse(resp.data)

    def test_12_upload_show_config__valid_data(self):
        for hname, fpath in zip(self.hosts, self.cnf_files):
            fname = os.path.basename(fpath)
            rpath = os.path.join(UP_PREFIX, fname)
            content = open(fpath).read()
            headers = {"content-type": "text/plain"}

            # API: upload_show_config
            resp = self.client.post(rpath, data=content, headers=headers)
            self.assertStatus(resp, 201, resp.data)

            upath = nof.utils.uploaded_filepath(
                fname, nof.libs.FT_FORTI_SHOW_CONFIG, content=content
            )
            self.assertTrue(os.path.exists(upath))

            # API: index
            resp = self.client.get(API_PREFIX + TT.IDX_PATH)
            self.assert200(resp)
            self.assertTrue(resp.data)

            # API: get_host_config (1)
            resp = self.client.get(GET_PREFIX + hname)
            # self.assertStatus(resp, ?, resp.data)  # FIXME
            self.assertTrue(resp.data)

    def test_20_find_firewall_policy_by_ipa__no_data(self):
        for hname in self.hosts:
            upath = os.path.join(FIND_PREFIX, hname, "127.0.0.1")
            resp = self.client.get(upath)
            self.assertStatus(resp, 204, resp.data)  # no content

    def test_22_find_firewall_policy_by_ipa__not_found(self):
        self._arrange_uploaded_and_procecced_files()
        for hname in self.hosts:
            upath = os.path.join(FIND_PREFIX, hname, "127.0.0.1")
            resp = self.client.get(upath)
            self.assert200(resp)

            res = anyconfig.loads(
                resp.data.decode("utf-8"),  # b -> u
                ac_parser="json"
            )
            self.assertFalse(res)  # == []

    def test_24_find_firewall_policy_by_ipa__match_ip(self):
        self._arrange_uploaded_and_procecced_files()
        for hname in self.hostnames:
            upath = os.path.join(FIND_PREFIX, hname, "192.168.3.5")
            resp = self.client.get(upath)
            self.assert200(resp)

            res = anyconfig.loads(
                resp.data.decode("utf-8"),  # b -> u
                ac_parser="json"
            )
            self.assertTrue(res)  # == [{"edit":, ...}]

    def test_34_find_firewall_policy_by_addr__contain_ipa(self):
        self._arrange_uploaded_and_procecced_files()
        for hname in self.hostnames:
            upath = os.path.join(FIND_PREFIX, hname, "192.168.2.2")
            resp = self.client.get(upath)
            self.assert200(resp)

            res = anyconfig.loads(
                resp.data.decode("utf-8"),  # b -> u
                ac_parser="json"
            )
            self.assertTrue(res)

# vim:sw=4:ts=4:et:
