# Copyright (C) 2020 Red Hat, Inc.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-function-docstring
"""nof.utils test cases
"""
import os.path
import os
import unittest
import tempfile
import mock

import nof.utils as TT
from nof.globals import NOF_DATA_DIR


_NOF_DATA_DIR = "/tmp/xxxxxxxx/yyyyy"
_OS_ENVIRON_PATCH = {"NOF_DATA_DIR": _NOF_DATA_DIR}


def org_env():
    if "NOF_DATA_DIR" in os.environ:
        del os.environ["NOF_DATA_DIR"]
    return os.environ


class TestFunctions(unittest.TestCase):
    """Test cases for simple functions.
    """

    @mock.patch.dict(os.environ, org_env(), clear=True)
    def test_10_datadir_maybe_from_env__default(self):
        self.assertEqual(TT.datadir_maybe_from_env(), NOF_DATA_DIR)

    @mock.patch.dict(os.environ, _OS_ENVIRON_PATCH)
    def test_12_datadir_maybe_from_env__env(self):
        self.assertEqual(TT.datadir_maybe_from_env(), _NOF_DATA_DIR)

    @mock.patch.dict(os.environ, org_env(), clear=True)
    def test_20_uploaddir__default(self):
        self.assertEqual(TT.uploaddir(), os.path.join(NOF_DATA_DIR, "uploads"))

    @mock.patch.dict(os.environ, _OS_ENVIRON_PATCH)
    def test_22_uploaddir__env(self):
        self.assertEqual(TT.uploaddir(),
                         os.path.join(_NOF_DATA_DIR, "uploads"))

    def test_30_ensure_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            datadir = os.path.join(tmpdir, "a/b/c/d")
            TT.ensure_dir_exists(os.path.join(datadir, "e.txt"))

            self.assertTrue(os.path.exists(datadir))
            self.assertTrue(os.path.isdir(datadir))

# vim:sw=4:ts=4:et:
