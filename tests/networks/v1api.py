#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
""".networks.v1api test cases
"""
import os.path
import os
import shutil

import anyconfig

import nof.networks.v1api as TT
import nof.utils

from .. import common as C


def _uploaded_filepath(filepath):
    """
    :param filepath: A str gives file path
    """
    return nof.utils.uploaded_filepath(
        os.path.basename(filepath),
        TT.FT_NETWORKS,
        content=open(filepath).read()  # str
    )


def _err_msg(resp, *args):
    """Make error message.
    """
    return "data: {}{}{}".format(resp.data, os.linesep,
                                 os.linesep.join(args))


class Get_Or_Upload_10_TestCase(C.BluePrintTestCaseWithWorkdir):

    net_files = C.list_res_files("networks/*.json")

    def test_10_get_or_upload_networks(self):
        for fpath in self.net_files:
            fname = os.path.basename(fpath)
            headers = {"content-type": "application/json"}

            content = open(fpath).read()
            opath = nof.utils.uploaded_filepath(fname, TT.FT_NETWORKS,
                                                content=content)
            nof.utils.ensure_dir_exists(opath)

            upath = os.path.join(TT.API_PREFIX, fname)
            resp = self.client.post(upath, data=content, headers=headers)

            self.assertStatus(resp, 201, resp.data)

            self.assertTrue(os.path.exists(opath))

            odata = anyconfig.load(opath)
            self.assertTrue(odata.get("nodes", False))
            self.assertTrue(odata.get("links", False))

            fname = os.path.basename(opath)  # Updated filename
            upath = os.path.join(TT.API_PREFIX, fname)
            resp = self.client.get(upath)

            self.assert200(resp, _err_msg(resp, "path: " + upath,
                                          "file: " + opath))
            self.assertEqual(resp.data, content.encode("utf-8"))


class Find_Networks_20_TestCase(C.BluePrintTestCaseWithWorkdir):

    net_files = C.list_res_files("networks/*.json")

    def setUp(self):
        super(Find_Networks_20_TestCase, self).setUp()

        self.up_files = [_uploaded_filepath(f) for f in self.net_files]
        for src, dst in zip(self.net_files, self.up_files):
            nof.utils.ensure_dir_exists(dst)
            shutil.copy(src, dst)

    def test_10_find_networks_by_addr__not_found(self):
        ipa = "127.0.0.1"
        for upf in self.up_files:
            fname = os.path.basename(upf)
            upath = os.path.join(TT.API_PREFIX, "by_addr", fname, ipa)

            resp = self.client.get(upath)

            self.assert200(resp, _err_msg(resp,
                                          "path: " + upath, "ip: " + ipa))
            self.assertTrue(resp.data)
            data = anyconfig.loads(resp.data, ac_parser="json")
            self.assertEqual(data, [], data)

    def test_20_find_networks_by_addr__found(self):
        ipa = "192.168.122.5"
        for upf in self.up_files:
            fname = os.path.basename(upf)
            upath = os.path.join(TT.API_PREFIX, "by_addr", fname, ipa)

            resp = self.client.get(upath)

            self.assert200(resp, _err_msg(resp,
                                          "path: " + upath, "ip: " + ipa))
            self.assertTrue(resp.data)
            data = anyconfig.loads(resp.data, ac_parser="json")
            self.assertEqual(data[0]["addrs"][0], "192.168.122.0/24", data[0])

    def test_30_find_networks_by_path__not_found(self):
        (src, dst) = ("192.168.1.5", "127.0.0.1")

        for upf in self.up_files:
            fname = os.path.basename(upf)
            upath = os.path.join(TT.API_PREFIX, "by_path", fname, src, dst)

            resp = self.client.get(upath)
            self.assert200(resp, _err_msg(resp,
                                          "path: {}, src: {}, "
                                          "dst: {}".format(upath, src, dst)))
            self.assertTrue(resp.data)
            data = anyconfig.loads(resp.data, ac_parser="json")
            self.assertEqual(data, [])

    def test_32_find_networks_by_path__found(self):
        (sip, dip) = ("192.168.122.10", "192.168.5.2")
        # (snt, dnt) = ("192.168.122.0/24", "192.168.5.0/24")

        for upf in self.up_files:
            fname = os.path.basename(upf)
            upath = os.path.join(TT.API_PREFIX, "by_path", fname, sip, dip)

            resp = self.client.get(upath)
            self.assert200(resp, _err_msg(resp,
                                          "path: {}, src: {}, "
                                          "dst: {}".format(upath, sip, dip)))
            self.assertTrue(resp.data)
            data = anyconfig.loads(resp.data, ac_parser="json")  # [[node]]
            self.assertNotEqual(data, [])

# vim:sw=4:ts=4:et:
