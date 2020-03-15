# Copyright (C) 2020 Red Hat, Inc.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name,missing-module-docstring
# pylint: disable=missing-class-docstring,missing-function-docstring
import os.path
import os
import unittest
import mock

import nof.utils as TT
import nof.globals


_NOF_DATA_DIR = "/tmp/xxxxxxxx/yyyyy"
_OS_ENVIRON_PATCH = {"NOF_DATA_DIR": _NOF_DATA_DIR}


class TestFunctions(unittest.TestCase):

    def test_datadir_maybe_from_env__default(self):
        self.assertEqual(TT.datadir_maybe_from_env(), nof.globals.NOF_DATA_DIR)

    @mock.patch.dict(os.environ, _OS_ENVIRON_PATCH)
    def test_datadir_maybe_from_env__env(self):
        self.assertEqual(TT.datadir_maybe_from_env(), _NOF_DATA_DIR)

    def test_uploaddir__default(self):
        self.assertEqual(TT.uploaddir(),
                         os.path.join(nof.globals.NOF_DATA_DIR, "uploads"))

    @mock.patch.dict(os.environ, _OS_ENVIRON_PATCH)
    def test_uploaddir__env(self):
        self.assertEqual(TT.uploaddir(),
                         os.path.join(_NOF_DATA_DIR, "uploads"))

    def test_database_url__default(self):
        self.assertEqual(TT.database_url(),
                         "sqlite:///" + os.path.join(nof.globals.NOF_DATA_DIR,
                                                     "main.db"))

    @mock.patch.dict(os.environ, _OS_ENVIRON_PATCH)
    def test_database_url__env(self):
        self.assertEqual(TT.database_url(),
                         "sqlite:///" + os.path.join(_NOF_DATA_DIR, "main.db"))
