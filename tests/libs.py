# Copyright (C) 2020 Red Hat, Inc.
# SPDX-License-Identifier: MIT
#
# pylint: disable=invalid-name
# pylint: disable=missing-class-docstring,missing-function-docstring
"""nof.libs test cases
"""
import os.path
import unittest
import tempfile

import nof.libs as TT


class TestCase(unittest.TestCase):

    maxDiff = None

    def test_10_ensure_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            datadir = os.path.join(tmpdir, "a/b/c/d")
            TT.ensure_dir_exists(os.path.join(datadir, "e.txt"))

            self.assertTrue(os.path.exists(datadir))
            self.assertTrue(os.path.isdir(datadir))

# vim:sw=4:ts=4:et:
