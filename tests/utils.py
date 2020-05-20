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

    def test_30_checksum__no_filepath_content(self):
        self.assertRaises(ValueError, TT.checksum)

    def test_32_checksum__filepath(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fpath = os.path.join(tmpdir, "hello.txt")
            content = "hello, world!\n"
            # checksum (sha1) value of the above `content`
            ref = "e91ba0972b9055187fa2efa8b5c156f487a8293a"
            open(fpath, 'w').write(content)

            res = TT.checksum(filepath=fpath)
            self.assertEqual(res, ref)

    def test_34_checksum__content(self):
        content = "hello, world!\n"
        # checksum (sha1) value of the above `content`
        ref = "e91ba0972b9055187fa2efa8b5c156f487a8293a"

        res = TT.checksum(content=content)
        self.assertEqual(res, ref)

    def test_40_uploaded_filename__no_content(self):
        fname = "test.txt"
        self.assertEqual(TT.uploaded_filename(fname), fname)

    def test_40_uploaded_filename__with_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fname = "hello.txt"
            content = "hello, world!\n"
            # checksum (sha1) value of the above `content`
            csum = "e91ba0972b9055187fa2efa8b5c156f487a8293a"
            open(os.path.join(tmpdir, fname), 'w').write(content)

            ref = "{}-{}".format(fname, csum)
            res = TT.uploaded_filename(fname, content=content)
            self.assertEqual(res, ref)

    def test_60_ensure_dir_exists(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            datadir = os.path.join(tmpdir, "a/b/c/d")
            TT.ensure_dir_exists(os.path.join(datadir, "e.txt"))

            self.assertTrue(os.path.exists(datadir))
            self.assertTrue(os.path.isdir(datadir))

    def test_70_list_filenames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fnames = "012.yml abc.txt xyz.json".split()
            for fname in fnames:
                fpath = os.path.join(tmpdir, fname)
                open(fpath, 'w').write("1\n")

            res = TT.list_filenames("*.dat", datadir=tmpdir)
            self.assertFalse(res)

            res = TT.list_filenames("*.json", datadir=tmpdir)
            self.assertTrue(res)
            self.assertEqual(res, [fnames[-1]])

            res = TT.list_filenames("*.*", datadir=tmpdir)
            self.assertTrue(res)
            self.assertEqual(res, fnames)

# vim:sw=4:ts=4:et:
