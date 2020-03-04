#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring, invalid-name
import os.path
import os
import shutil

import nof.main.utils as U
import nof.lib.fortios as F

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

    def test_10_get_group_config_file(self):
        for filepath in C.test_res_files("fortios/firewall*.txt"):
            filename = os.path.basename(filepath)

            srcpath = U.upload_filepath(filename)
            shutil.copy(filepath, srcpath)
            assert os.path.exists(srcpath)

            U.parse_config_and_dump_json_file(filename, "fortios")

            outpath = U.processed_filepath(filename, prefix="fortios_")
            outpath_2 = F.group_config_path(outpath, "firewall")
            self.assertTrue(os.path.exists(outpath), outpath)
            self.assertTrue(os.path.exists(outpath_2), outpath_2)

            path = _url_path("firewall", filename)
            resp = self.client.get(path)

            self.assertEqual(resp.status_code, 200,
                             _err_msg(resp, "path: " + path,
                                      "file: " + outpath_2))
            self.assertEqual(resp.data, open(outpath_2, 'rb').read())

# vim:sw=4:ts=4:et: