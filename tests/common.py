#
# Copyright (C) 2020 Satoru SATOH <ssato@redhat.com>.
# SPDX-License-Identifier: MIT
#
# pylint: disable=missing-docstring
import glob
import os.path
import os
import shutil
import tempfile

try:
    from unittest import SkipTest
except ImportError:
    from nose.plugins.skip import SkipTest

import flask_testing
import nof


def skip_test():
    raise SkipTest


def selfdir(self=__file__):
    """
    >>> os.path.exists(selfdir())
    True
    """
    return os.path.dirname(self)


def resdir(self=__file__):
    """
    >>> assert os.path.exists(resdir())
    """
    return os.path.join(selfdir(self), "res")


def list_res_files(pattern):
    return sorted(glob.glob(os.path.join(resdir(), pattern)))


def ok_yml_files():
    return list_res_files("*__ok.yml")


def config_files(ctype):
    return list_res_files(os.path.join(ctype, "*.txt"))


def setup_workdir():
    return tempfile.mkdtemp()


def prune_workdir(workdir):
    shutil.rmtree(workdir)


class BluePrintTestCase(flask_testing.TestCase):
    """Base class for app test cases.
    """
    def create_app(self):
        return nof.create_app("testing")  # debug, disable CSRF, etc.


class BluePrintTestCaseWithWorkdir(BluePrintTestCase):
    """Base class for app test cases need working dir.
    """
    cleanup = True

    def setUp(self):
        self.workdir = os.environ["NOF_UPLOADDIR"] = setup_workdir()
        super(BluePrintTestCaseWithWorkdir, self).setUp()

    def tearDown(self):
        super(BluePrintTestCaseWithWorkdir, self).tearDown()
        if self.cleanup:
            prune_workdir(self.workdir)

# vim:sw=4:ts=4:et:
