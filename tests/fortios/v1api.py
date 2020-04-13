#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path

import nof.fortios.utils as U

from nof.fortios import API_PREFIX
from .. import common as C


def _url_path(*args):
    """
    >>> _url_path("firewall", "a.json")
    '/fortios/api/v1/firewall/a.json'
    """
    return '{}/{}'.format(API_PREFIX, os.path.sep.join(args))


def _err_msg(resp, *args):
    return "data: {}{}{}".format(resp.data, os.linesep,
                                 os.linesep.join(args))


class V1_API_10_Simple_TestCase(C.BluePrintTestCaseWithWorkdir):

    maxDiff = None
    cleanup = False

    hostname = "foo-1"
    filenames = ["metadata.json", "firewall_policies.json"]

    def test_10_get_host_configs(self):
        hdir = U.host_configs_dir(self.hostname)
        for fn in self.filenames:
            C.touch_file(os.path.join(hdir, fn))

        path = _url_path(self.hostname)
        resp = self.client.get(path)

        self.assertEqual(resp.status_code, 200,
                         _err_msg(resp, "path: " + path))
        self.assertEqual(set(resp.data), set(self.filenames),
                         resp.data)

    def test_50_get_host_config(self):
        hdir = U.host_configs_dir(self.hostname)
        for fn in self.filenames:
            filepath = os.path.join(hdir, fn)
            C.touch_file(filepath, fn)

            path = _url_path(self.hostname, fn)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path))
            self.assertEqual(resp.data, open(filepath, "rb").read())

# vim:sw=4:ts=4:et:
